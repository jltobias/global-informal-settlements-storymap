from __future__ import annotations
import argparse,json,urllib.parse,urllib.request
from pathlib import Path

def get_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'global-informal-settlements-storymap/0.1'})
    with urllib.request.urlopen(req,timeout=90) as r: return json.load(r)
def main(service,layer,output):
    base=service.rstrip('/')+'/'+str(layer)+'/query'
    features=[]; offset=0; page=2000
    while True:
        qs=urllib.parse.urlencode({'where':'1=1','outFields':'*','f':'geojson','resultOffset':offset,'resultRecordCount':page,'returnGeometry':'true'})
        obj=get_json(base+'?'+qs)
        batch=obj.get('features',[]); features.extend(batch)
        if len(batch)<page: break
        offset+=len(batch)
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps({'type':'FeatureCollection','features':features},indent=2)+'\n',encoding='utf-8')
    print(f'wrote {len(features)} features to {output}')
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('service'); ap.add_argument('--layer',type=int,default=0); ap.add_argument('--output',required=True); a=ap.parse_args(); main(a.service,a.layer,a.output)
