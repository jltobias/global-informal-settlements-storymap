from __future__ import annotations
import argparse,csv,json,urllib.request
from pathlib import Path
IND='EN.POP.SLUM.UR.ZS'

def load_iso(path):
    with open(path,encoding='utf-8') as f: return {r['iso3']:r for r in csv.DictReader(f)}
def fetch_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'global-informal-settlements-storymap/0.1'})
    with urllib.request.urlopen(req,timeout=60) as r: return json.load(r)
def main(output,offline_ok):
    iso=load_iso(Path(output).with_name('iso_countries.csv'))
    try:
        data=fetch_json(f'https://api.worldbank.org/v2/country/all/indicator/{IND}?format=json&mrnev=1&per_page=20000')[1]
        countries=fetch_json('https://api.worldbank.org/v2/country?format=json&per_page=400')[1]
        coords={c.get('id'):(c.get('longitude',''),c.get('latitude','')) for c in countries}
        vals={r.get('countryiso3code'):r for r in data if r.get('countryiso3code') in iso and r.get('value') is not None}
        rows=[]
        for k,meta in sorted(iso.items()):
            r=vals.get(k,{}); lon,lat=coords.get(k,('',''))
            rows.append([k,meta['country_name'],IND,'Population living in slums (% of urban population)',r.get('date',''),r.get('value',''),lon,lat,'fetched' if r else 'no_value'])
        with open(output,'w',newline='',encoding='utf-8') as f:
            w=csv.writer(f); w.writerow(['iso3','country_name','indicator','indicator_name','year','value_percent','country_longitude','country_latitude','status']); w.writerows(rows)
        print(f'wrote {len(rows)} country rows to {output}')
    except Exception as e:
        if offline_ok:
            print(f'WARNING: WDI refresh failed; keeping checked-in fallback: {e}')
        else: raise
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--output',default='content/data/country_slum_context.csv'); ap.add_argument('--offline-ok',action='store_true'); a=ap.parse_args(); main(a.output,a.offline_ok)
