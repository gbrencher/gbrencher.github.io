"""Build the static terrain layer from downloaded Copernicus GLO-30 COG tiles.

Usage: python scripts/prepare_hillshade.py /path/to/cop30
Input tiles: https://copernicus-dem-30m.s3.amazonaws.com/readme.html
"""
import sys
from pathlib import Path
import numpy as np
import rasterio
from matplotlib.colors import LightSource
from rasterio.warp import reproject, Resampling
from render_snow import display_grid, CRS


def build(source):
    bounds, width, height, transform = display_grid()
    elevation = np.full((height, width), np.nan, dtype='float32')
    for file in sorted(Path(source).glob('Copernicus*.tif')):
        tile = np.full_like(elevation, np.nan)
        with rasterio.open(file) as src:
            reproject(rasterio.band(src, 1), tile, src_transform=src.transform,
                      src_crs=src.crs, src_nodata=src.nodata,
                      dst_transform=transform, dst_crs=CRS, dst_nodata=np.nan,
                      resampling=Resampling.bilinear)
        valid = np.isfinite(tile)
        elevation[valid] = tile[valid]
    if not np.isfinite(elevation).all():
        raise ValueError('Incomplete terrain coverage')
    shade = LightSource(azdeg=315, altdeg=45).hillshade(
        elevation, vert_exag=1, dx=transform.a, dy=-transform.e)
    out = Path(__file__).parent / 'data' / 'north-cascades-hillshade.tif'
    out.parent.mkdir(exist_ok=True)
    with rasterio.open(out, 'w', driver='GTiff', width=width, height=height,
                       count=1, dtype='uint8', crs=CRS, transform=transform,
                       compress='deflate') as dst:
        dst.write(np.round(shade * 255).astype('uint8'), 1)
        dst.update_tags(source='Copernicus DEM GLO-30 (AWS public COGs)',
                        azimuth='315', altitude='45', vertical_exaggeration='1')
    print(out)


if __name__ == '__main__':
    build(sys.argv[1])
