"""Render real deep-snow tile outputs on a common UTM grid for the homepage."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import cmocean
from matplotlib.colors import ListedColormap, PowerNorm
import rasterio
from rasterio.transform import from_bounds
from rasterio.warp import reproject, transform_bounds, Resampling

BBOX = (-122.10, 48.375, -120.50, 48.875)
CRS = 'EPSG:32610'
OUTPUT_DPI = 200
SNOW_NORM = PowerNorm(gamma=.55, vmin=0, vmax=6, clip=False)


def snow_cmap(hi=.88, white_below=.05, blend_to=.15, norm=SNOW_NORM, n=512):
    """Suppress shallow prediction noise with a white floor and smooth onset."""
    lut = cmocean.cm.ice_r(np.linspace(0, hi, n))
    v = np.linspace(0, 1, n)
    v0 = float(norm(white_below))
    v1 = float(norm(max(blend_to, white_below)))
    if v1 <= v0:
        weight = (v > v0).astype(float)
    else:
        weight = np.clip((v - v0) / (v1 - v0), 0, 1)
        weight = weight * weight * (3 - 2 * weight)
    lut[:, :3] = (1 - weight[:, None]) + lut[:, :3] * weight[:, None]
    cmap = ListedColormap(lut, name='snow')
    cmap.set_over('#3d1152')
    cmap.set_bad(alpha=0)
    return cmap


SNOW_CMAP = snow_cmap()


def composite_snow(depth, shade, cmap=SNOW_CMAP, hillshade_opacity=.30, opacity=1.0):
    """Multiply snow colour by a light terrain layer on a white page."""
    d = np.where(np.isfinite(depth), np.maximum(depth, 0), 0)
    hs = (1 - hillshade_opacity * (1 - np.clip(shade, 0, 1) ** .90))[..., None]
    snow_rgb = cmap(SNOW_NORM(d))[..., :3]
    snow_rgb = 1 - opacity * (1 - snow_rgb)
    snow_rgb[~np.isfinite(depth)] = 1
    return np.clip(hs * snow_rgb, 0, 1)


def display_grid():
    outer = transform_bounds('EPSG:4326', CRS, *BBOX, densify_pts=41)
    dx, dy = outer[2] - outer[0], outer[3] - outer[1]
    # Fixed inset avoids the curved geographic boundary in the UTM rectangle.
    bounds = (outer[0] + .015*dx, outer[1] + .06*dy, outer[2] - .015*dx, outer[3] - .06*dy)
    # Preserve the original 14-inch export width at twice the former DPI.
    width = 14 * OUTPUT_DPI
    height = round(width * (bounds[3] - bounds[1]) / (bounds[2] - bounds[0]))
    transform = from_bounds(*bounds, width, height)
    return bounds, width, height, transform


def render(source, output, target, snow_off):
    files = sorted(Path(source).rglob('*_sd.tif'))
    # The upstream 1.4-degree core tiling creates two tiles for this fixed extent.
    if len(files) != 2:
        raise ValueError(f'Expected two completed prediction tiles, received {len(files)}')
    bounds, width, height, transform = display_grid()
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
    # Only scientific pixels go in the image; all lettering is native website text.
    terrain_path = Path(__file__).parent / 'data' / 'north-cascades-hillshade.tif'
    with rasterio.open(terrain_path) as terrain:
        if terrain.shape != mosaic.shape or terrain.crs.to_string() != CRS or not terrain.transform.almost_equals(transform):
            raise ValueError('Hillshade grid differs from map; rebuild with prepare_hillshade.py')
        shade = terrain.read(1).astype('float32') / 255
    rgb = composite_snow(mosaic, shade)
    plt.imsave(output / 'latest.png', rgb, dpi=OUTPUT_DPI)
    date = datetime.strptime(target, '%Y%m%d').date().isoformat()
    metadata = {'presentation_version': 2, 'width': width, 'height': height, 'dpi': OUTPUT_DPI,
                'scale_metres': 10000, 'snow_opacity': 1.0, 'terrain': 'Copernicus DEM GLO-30',
                'colormap': 'cmocean.ice_r', 'colormap_range': [0, .88],
                'white_below_metres': .05, 'blend_to_metres': .15,
                'norm': 'power', 'gamma': .55, 'vmin': 0, 'vmax': 6,
                'blend': 'multiply', 'hillshade_opacity': .30, 'hillshade_exponent': .90,
                'terrain_vertical_exaggeration': 1.4, 'nodata_display': 'bare hillshade',
                'over_color': '#3d1152',
                'legend_ticks': [{'value': x, 'position': float(SNOW_NORM(x))} for x in [0, .25, 1, 2, 4, 6]],
                'scale_fraction': 10000 / (bounds[2] - bounds[0]),
                'projected_bounds': list(bounds), 'crs': CRS, 'valid_fraction': coverage,
                'legend_colors': [matplotlib.colors.to_hex(SNOW_CMAP(x)) for x in np.linspace(0, 1, 256)],
                'target_date': date, 'snow_off_date': datetime.strptime(snow_off, '%Y%m%d').date().isoformat(),
                'generated_at': datetime.now(timezone.utc).isoformat(), 'bbox': list(BBOX),
                'image': 'assets/snow/latest.png', 'tile_count': len(files),
                'description': 'Deep-snow model prediction using composite satellite inputs; the target date is not the acquisition date of every input.'}
    (output / 'latest.json').write_text(json.dumps(metadata, indent=2) + '\n')


if __name__ == '__main__':
    render(*sys.argv[1:])
