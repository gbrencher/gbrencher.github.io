"""Small synthetic raster checks; never publish these fixtures."""
import json
import tempfile
from pathlib import Path
from PIL import Image
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from render_snow import render, composite_snow, SNOW_CMAP, SNOW_NORM, BBOX as BOUNDS
import matplotlib
depths = np.array([[0, .019, .05, .1, .2, 1, 6, 7, np.nan]])
colors = composite_snow(depths, np.full_like(depths, .5))
bare = 1 - .30 * (1 - .5 ** .90)
assert np.allclose(colors[0, 0], bare)
assert np.allclose(SNOW_CMAP(0)[:3], 1)  # No cyan tint on bare ground.
assert np.allclose(colors[0, :3], bare)  # Predictions through 5 cm are hidden.
assert not np.allclose(colors[0, 3], bare)  # Snow colour eases in above 5 cm.
assert not np.allclose(colors[0, 6], colors[0, 7])  # Overflow is distinct.
assert np.allclose(colors[0, -1], bare)  # Missing data shows terrain.
assert np.allclose(composite_snow(depths, np.ones_like(depths))[0, 5], SNOW_CMAP(SNOW_NORM(1))[:3])
assert np.allclose(composite_snow(depths, np.zeros_like(depths))[0, 5], .7 * np.array(SNOW_CMAP(SNOW_NORM(1))[:3]))
assert .46 < SNOW_NORM(1.5) < .47
assert np.allclose(SNOW_CMAP(SNOW_NORM(7))[:3], matplotlib.colors.to_rgb('#3d1152'))
assert np.isfinite(colors).all() and colors.min() >= 0 and colors.max() <= 1

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
    assert abs(meta['scale_fraction'] * (meta['projected_bounds'][2] - meta['projected_bounds'][0]) - 10000) < .01
    assert meta['valid_fraction'] == 1.0
    assert meta['white_below_metres'] == .05 and meta['blend_to_metres'] == .15
    with Image.open(root/'output/latest.png') as image:
        assert image.size == (meta['width'], meta['height'])
        assert image.width == 2800 and abs(image.info['dpi'][0] - 200) < .01
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
