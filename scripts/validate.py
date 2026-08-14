from __future__ import annotations
import csv,json,sys
from pathlib import Path
REQ={'settlement_id','country_iso3','country_name','settlement_name','source_id','source_url','source_year','license','classification_label','geometry_status','representative_lon','representative_lat','bbox_wgs84'}
def main():
    root=Path(__file__).resolve().parents[1]; errors=[]
    fc=json.loads((root/'content/data/settlements.geojson').read_text(encoding='utf-8'))
    if fc.get('type')!='FeatureCollection': errors.append('settlements.geojson is not FeatureCollection')
    for i,f in enumerate(fc.get('features',[])):
        p=f.get('properties',{}); miss=REQ-set(p)
        if miss: errors.append(f'feature {i} missing {sorted(miss)}')
        b=p.get('bbox_wgs84');
        if not isinstance(b,list) or len(b)!=4: errors.append(f'feature {i} invalid bbox')
        if p.get('geometry_status')=='synthetic' and 'synthetic' not in (p.get('notes','')+p.get('settlement_name','')).lower(): errors.append(f'feature {i} synthetic not clearly labelled')
    for p in (root/'content').rglob('*.jGIS'):
        d=json.loads(p.read_text(encoding='utf-8'))
        if not {'layers','sources'}.issubset(d): errors.append(f'{p}: missing layers/sources')
        for st in d.get('stories',{}).values():
            for sid in st.get('storySegments',[]):
                if sid not in d.get('layers',{}): errors.append(f'{p}: story segment {sid} missing layer')
                elif d['layers'][sid].get('type')!='StorySegmentLayer': errors.append(f'{p}: story segment {sid} wrong type')
    for p in (root/'content/notebooks').glob('*.ipynb'):
        n=json.loads(p.read_text(encoding='utf-8'))
        if n.get('nbformat')!=4: errors.append(f'{p}: invalid nbformat')
    if errors:
        print('\n'.join('ERROR: '+e for e in errors)); return 1
    print(f'validation passed: {len(fc.get("features",[]))} canonical feature(s), {len(list((root/"content").rglob("*.jGIS")))} jGIS project(s)')
    return 0
if __name__=='__main__': sys.exit(main())
