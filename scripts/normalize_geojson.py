from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
from geo_utils import geometry_bbox, representative_point

REQUIRED = ['country_iso3','country_name','settlement_name','source_id','source_url','source_year','license','classification_label']

def normalize(src, mapping, output):
    fc=json.loads(Path(src).read_text(encoding='utf-8'))
    mp=json.loads(Path(mapping).read_text(encoding='utf-8'))
    out=[]
    for i, feat in enumerate(fc.get('features', [])):
        props=feat.get('properties') or {}; geom=feat.get('geometry')
        bbox=geometry_bbox(geom)
        if bbox is None: continue
        rep=representative_point(geom)
        norm={}
        for canonical, source_key in mp.items():
            norm[canonical]=props.get(source_key) if source_key else None
        missing=[k for k in REQUIRED if norm.get(k) in (None,'')]
        if missing: raise ValueError(f'feature {i}: missing mapped values: {missing}')
        iso3=str(norm['country_iso3']).upper()
        if len(iso3)!=3: raise ValueError(f'feature {i}: country_iso3 must be 3 letters')
        norm['country_iso3']=iso3
        if not norm.get('settlement_id'):
            key=f"{norm['source_id']}|{iso3}|{norm['settlement_name']}|{i}".encode()
            norm['settlement_id']=hashlib.sha1(key).hexdigest()[:16]
        norm['geometry_status']=norm.get('geometry_status') or ('point_only' if geom.get('type')=='Point' else 'boundary')
        norm['representative_lon'],norm['representative_lat']=rep
        norm['representative_method']='bbox_center'
        norm['bbox_wgs84']=bbox
        norm.setdefault('classification_definition','')
        norm.setdefault('confidence',None)
        norm.setdefault('notes','')
        out.append({'type':'Feature','id':norm['settlement_id'],'bbox':bbox,'properties':norm,'geometry':geom})
    result={'type':'FeatureCollection','features':out}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'wrote {len(out)} normalized features to {output}')

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('--mapping',required=True); ap.add_argument('--output',required=True)
    a=ap.parse_args(); normalize(a.src,a.mapping,a.output)
