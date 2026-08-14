"""Polygonize a binary classified GeoTIFF into WGS84 GeoJSON.

Designed for local preprocessing of model-derived raster products such as the
Jiang et al. (2026) Permanent Informal Settlements (PIS) tiles. This script is
not required in JupyterLite. It requires rasterio and numpy locally.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path


def polygonize(paths, output, value=1, source_id='raster_classification', source_url='', source_year='', license_text='VERIFY_SOURCE_LICENSE'):
    try:
        import numpy as np
        import rasterio
        from rasterio.features import shapes
        from rasterio.warp import transform_geom
    except ImportError as exc:
        raise SystemExit('This local adapter requires rasterio and numpy.') from exc

    features=[]
    seq=0
    for path in paths:
        path=Path(path)
        with rasterio.open(path) as src:
            arr=src.read(1)
            mask=arr == value
            for geom, pixel_value in shapes(arr, mask=mask, transform=src.transform, connectivity=8):
                if int(pixel_value) != value:
                    continue
                geom4326=transform_geom(src.crs, 'EPSG:4326', geom, precision=7)
                seq += 1
                features.append({
                    'type':'Feature',
                    'id':f'{source_id}-{seq:09d}',
                    'properties':{
                        'source_id':source_id,
                        'source_url':source_url,
                        'source_year':source_year,
                        'license':license_text,
                        'classification_label':'model-derived informal-settlement raster patch',
                        'classification_definition':f'Connected pixels with raster value {value}',
                        'geometry_status':'model_derived_boundary',
                        'source_tile':path.name,
                        'notes':'Raster-connected component; not necessarily a locally named settlement.'
                    },
                    'geometry':geom4326,
                })
    out={'type':'FeatureCollection','features':features}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(out,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'wrote {len(features)} raster-derived polygon feature(s) to {output}')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rasters', nargs='+', help='Input GeoTIFF tile(s)')
    ap.add_argument('--output', required=True)
    ap.add_argument('--value', type=int, default=1)
    ap.add_argument('--source-id', default='jiang_2026_pis_10m')
    ap.add_argument('--source-url', default='https://zenodo.org/records/21459094')
    ap.add_argument('--source-year', default='circa 2020')
    ap.add_argument('--license', dest='license_text', default='VERIFY_ZENODO_RIGHTS_METADATA')
    a=ap.parse_args()
    polygonize(a.rasters,a.output,a.value,a.source_id,a.source_url,a.source_year,a.license_text)

if __name__=='__main__':
    main()
