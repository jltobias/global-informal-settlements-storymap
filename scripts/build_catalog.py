from __future__ import annotations
import csv,json
from pathlib import Path

def main():
    root=Path(__file__).resolve().parents[1]
    fc=json.loads((root/'content/data/settlements.geojson').read_text(encoding='utf-8'))
    counts={}
    for f in fc.get('features',[]):
        p=f.get('properties',{}); iso=p.get('country_iso3','UNK'); counts[iso]=counts.get(iso,0)+1
    wdi={}
    with (root/'content/data/country_slum_context.csv').open(encoding='utf-8') as f:
        for r in csv.DictReader(f): wdi[r['iso3']]=r
    rows=[]
    with (root/'content/data/iso_countries.csv').open(encoding='utf-8') as f:
        for r in csv.DictReader(f):
            x=wdi.get(r['iso3'],{})
            rows.append([r['iso3'],r['iso2'],r['country_name'],counts.get(r['iso3'],0),x.get('year',''),x.get('value_percent',''),x.get('status','')])
    if 'XDM' in counts:
        rows.insert(0,['XDM','XD','Demonstration Country (synthetic)',counts['XDM'],'','','synthetic_demo'])
    out=root/'content/data/country_index.csv'
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['iso3','iso2','country_name','settlement_feature_count','wdi_year','wdi_slum_share_percent','wdi_status']); w.writerows(rows)
    print(f'wrote {len(rows)} rows to {out}')
if __name__=='__main__': main()
