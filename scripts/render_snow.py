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

BBOX = (-122.10, 48.25, -120.50, 49.00)
CRS = 'EPSG:32610'


def render(source, output, target, snow_off):
    files = sorted(Path(source).rglob('*_sd.tif'))
    # The upstream 1.4-degree core tiling creates two tiles for this fixed extent.
    if len(files) != 2:
        raise ValueError(f'Expected two completed prediction tiles, received {len(files)}')
    bounds = transform_bounds('EPSG:4326', CRS, *BBOX, densify_pts=41)
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
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'], 'font.size': 10})
    fig, ax = plt.subplots(figsize=(12, 8), layout='constrained')
    cmap = plt.get_cmap('Blues').copy()
    cmap.set_bad('#e3e3e3')
    im = ax.imshow(mosaic, extent=bounds[0:1] + bounds[2:3] + bounds[1:2] + bounds[3:4],
                   origin='upper', cmap=cmap, vmin=0, vmax=5)
    ax.set_axis_off()
    ax.set_title('North Cascades | Modeled snow depth', loc='left', fontsize=16, pad=14)
    date = datetime.strptime(target, '%Y%m%d').date().isoformat()
    ax.text(1, 1.025, date, transform=ax.transAxes, ha='right')
    ax.annotate('N ↑', (.97, .94), xycoords='axes fraction', ha='right')
    bar = fig.colorbar(im, ax=ax, orientation='horizontal', fraction=.035, pad=.025, extend='max')
    bar.set_label('Snow depth (m) · Gray indicates no data · Display resampled from model output')
    fig.savefig(output / 'latest.png', dpi=150, facecolor='white')
    plt.close(fig)
    metadata = {'target_date': date, 'snow_off_date': datetime.strptime(snow_off, '%Y%m%d').date().isoformat(),
                'generated_at': datetime.now(timezone.utc).isoformat(), 'bbox': list(BBOX),
                'image': 'assets/snow/latest.png', 'tile_count': len(files),
                'description': 'Deep-snow model prediction using composite satellite inputs; the target date is not the acquisition date of every input.'}
    (output / 'latest.json').write_text(json.dumps(metadata, indent=2) + '\n')


if __name__ == '__main__':
    render(*sys.argv[1:])
