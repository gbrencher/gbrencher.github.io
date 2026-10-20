"""Small synthetic raster checks; never publish these fixtures."""
import json
import tempfile
from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from render_snow import render, BBOX as BOUNDS

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    inputs = root/'input'
    inputs.mkdir()
    tile = inputs/'test_sd.tif'
    with rasterio.open(tile, 'w', driver='GTiff', width=200, height=150, count=1,
                       dtype='float32', crs='EPSG:4326',
                       transform=from_bounds(*BOUNDS, 200, 150), nodata=-9999) as ds:
        ds.write(np.tile(np.linspace(0, 5, 200, dtype='float32'), (150, 1)), 1)
    import shutil
    shutil.copyfile(tile, inputs/'second_sd.tif')
    render(inputs, root/'output', '20261018', '20260910')
    assert json.loads((root/'output/latest.json').read_text())['bbox'] == list(BOUNDS)
    meta = json.loads((root/'output/latest.json').read_text())
    assert meta['presentation_version'] == 2
    assert abs(meta['scale_fraction'] * (meta['projected_bounds'][2] - meta['projected_bounds'][0]) - 20000) < .01
    assert meta['valid_fraction'] == 1.0
    before = (root/'output/latest.png').read_bytes()
    with rasterio.open(tile, 'r+') as ds:
        ds.write(np.full((150, 200), -9999, dtype='float32'), 1)
    shutil.copyfile(tile, inputs/'second_sd.tif')
    try:
        render(inputs, root/'output', '20261019', '20260910')
    except ValueError:
        pass
    else:
        raise AssertionError('Missing data must reject publication')
    assert (root/'output/latest.png').read_bytes() == before
print('Renderer and previous-map preservation checks passed.')
