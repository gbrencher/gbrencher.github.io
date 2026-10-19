"""Render upstream snow-depth tiles on a common, north-up UTM grid."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.warp import reproject, transform_bounds, Resampling

BOUNDS = (-121.85, 48.35, -120.50, 49.00)
REF = 'bcc0f928f979af2b65f3bdc984cf2a563fea96fd'

def render(input_dir, output_dir, target, reference):
    files = sorted(Path(input_dir).rglob('*_sd.tif'))
    if not files:
        raise ValueError('No snow-depth GeoTIFFs found; retaining previous map.')
    bounds = transform_bounds('EPSG:4326', 'EPSG:32610', *BOUNDS)
    width = 1600
    height = round(width * (bounds[3] - bounds[1]) / (bounds[2] - bounds[0]))
    transform = from_bounds(*bounds, width, height)
    mosaic = np.full((height, width), np.nan, dtype='float32')
    for file in files:
        with rasterio.open(file) as src:
            if src.crs is None:
                raise ValueError(f'Missing CRS: {file}')
            data = src.read(1, masked=True).astype('float32').filled(np.nan)
            tile = np.full_like(mosaic, np.nan)
            reproject(data, tile, src_transform=src.transform, src_crs=src.crs,
                      src_nodata=np.nan, dst_transform=transform, dst_crs='EPSG:32610',
                      dst_nodata=np.nan, resampling=Resampling.nearest)
            valid = np.isfinite(tile) & (tile >= 0)
            mosaic[valid] = tile[valid]
    coverage = float(np.isfinite(mosaic).mean())
    if coverage < .8:
        raise ValueError(f'Only {coverage:.1%} valid coverage; retaining previous map.')
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 9))
    fig.subplots_adjust(left=.01, right=.99, top=.95, bottom=.12)
    cmap = plt.get_cmap('magma_r').copy()
    cmap.set_bad('#dedede')
    img = ax.imshow(mosaic, cmap=cmap, vmin=0, vmax=5, origin='upper')
    ax.set_axis_off()
    ax.set_title('NORTH CASCADES', loc='left', fontsize=12, pad=10)
    bar = fig.colorbar(img, ax=ax, orientation='horizontal', fraction=.035, pad=.025, extend='max')
    bar.set_label('Predicted snow depth (m) · Grey: no data')
    fig.savefig(output/'latest.png', dpi=150, facecolor='white')
    plt.close(fig)
    metadata = dict(target_date=datetime.strptime(target, '%Y%m%d').date().isoformat(),
                    snow_off_date=reference, generated_at=datetime.now(timezone.utc).isoformat(),
                    bounds=BOUNDS, valid_fraction=coverage, source_commit=REF,
                    source='https://github.com/geo-smart/deep-snow',
                    run_url=f"https://github.com/{os.getenv('GITHUB_REPOSITORY', '')}/actions/runs/{os.getenv('GITHUB_RUN_ID', '')}")
    (output/'latest.json').write_text(json.dumps(metadata, indent=2)+'\n')

if __name__ == '__main__':
    render('snow-input', 'dist/assets/snow', os.environ['TARGET_DATE'], os.environ['SNOW_OFF_DATE'])
