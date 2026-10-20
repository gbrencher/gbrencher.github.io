"""Render real deep-snow tile outputs on a common UTM grid for the homepage."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.warp import reproject, transform_bounds, Resampling

BBOX = (-122.10, 48.375, -120.50, 48.875)
CRS = 'EPSG:32610'


def render(source, output, target, snow_off):
    files = sorted(Path(source).rglob('*_sd.tif'))
    # The upstream 1.4-degree core tiling creates two tiles for this fixed extent.
    if len(files) != 2:
        raise ValueError(f'Expected two completed prediction tiles, received {len(files)}')
    outer = transform_bounds('EPSG:4326', CRS, *BBOX, densify_pts=41)
    dx, dy = outer[2] - outer[0], outer[3] - outer[1]
    # Fixed inset avoids the curved geographic boundary in the UTM rectangle.
    bounds = (outer[0] + .015*dx, outer[1] + .06*dy, outer[2] - .015*dx, outer[3] - .06*dy)
    width = 1400
    height = round(width * (bounds[3] - bounds[1]) / (bounds[2] - bounds[0]))
    transform = from_bounds(*bounds, width, height)
    mosaic = np.full((height, width), np.nan, dtype='float32')
    for path in files:
        tile = np.full_like(mosaic, np.nan)
        with rasterio.open(path) as src:
            if src.crs is None:
                raise ValueError(f'Missing CRS: {path}')
            reproject(rasterio.band(src, 1), tile,
                      src_transform=src.transform, src_crs=src.crs,
                      src_nodata=src.nodata, dst_transform=transform,
                      dst_crs=CRS, dst_nodata=np.nan,
                      resampling=Resampling.bilinear)
        valid = np.isfinite(tile) & (tile >= 0)
        if not valid.any():
            raise ValueError(f'No valid nonnegative depths in {path}')
        mosaic[valid] = tile[valid]
    if not np.isfinite(mosaic).any():
        raise ValueError('No valid map pixels')
    coverage = float(np.isfinite(mosaic).mean())
    edges = np.concatenate([mosaic[:3].ravel(), mosaic[-3:].ravel(), mosaic[:, :3].ravel(), mosaic[:, -3:].ravel()])
    if coverage < .995 or not np.isfinite(edges).all():
        raise ValueError(f'Incomplete display coverage ({coverage:.2%}); retain previous map')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    cmap = plt.get_cmap('Blues').copy()
    cmap.set_bad('#e3e3e3')
    # Only scientific pixels go in the image; all lettering is native website text.
    plt.imsave(output / 'latest.png', mosaic, cmap=cmap, vmin=0, vmax=5)
    date = datetime.strptime(target, '%Y%m%d').date().isoformat()
    metadata = {'presentation_version': 2, 'width': width, 'height': height,
                'scale_fraction': 20000 / (bounds[2] - bounds[0]),
                'projected_bounds': list(bounds), 'crs': CRS, 'valid_fraction': coverage,
                'legend_colors': [matplotlib.colors.to_hex(cmap(x)) for x in np.linspace(0, 1, 21)],
                'target_date': date, 'snow_off_date': datetime.strptime(snow_off, '%Y%m%d').date().isoformat(),
                'generated_at': datetime.now(timezone.utc).isoformat(), 'bbox': list(BBOX),
                'image': 'assets/snow/latest.png', 'tile_count': len(files),
                'description': 'Deep-snow model prediction using composite satellite inputs; the target date is not the acquisition date of every input.'}
    (output / 'latest.json').write_text(json.dumps(metadata, indent=2) + '\n')


if __name__ == '__main__':
    render(*sys.argv[1:])
