from __future__ import annotations
import json, shutil, uuid
from pathlib import Path
from collections import defaultdict
from geo_utils import bbox_polygon,bbox_to_webmercator,lonlat_to_webmercator

def uid(): return str(uuid.uuid4())
def vector_layer(name,source,color):
    return {'name':name,'parameters':{'color':color,'opacity':1.0,'source':source,'symbologyState':{}},'type':'VectorLayer','visible':True}
def geojson_source(name,path): return {'name':name,'parameters':{'path':path},'type':'GeoJSONSource'}
def osm_source(): return {'name':'OpenStreetMap.Mapnik','parameters':{'attribution':'© OpenStreetMap contributors','interpolate':False,'maxZoom':19.0,'minZoom':0.0,'provider':'OpenStreetMap','url':'https://tile.openstreetmap.org/{z}/{x}/{y}.png','urlParameters':{}},'type':'RasterSource'}
def story_segment(name,bbox,markdown):
    return {'name':name,'parameters':{'content':{'contentMode':'map','image':'','markdown':markdown,'title':name},'extent':bbox_to_webmercator(bbox),'layerOverride':[],'transition':{'time':1.5,'type':'smooth'},'zoom':13.0},'type':'StorySegmentLayer','visible':True}
def fc(features): return {'type':'FeatureCollection','features':features}
def point_feature(feat):
    p=feat['properties']; return {'type':'Feature','id':p['settlement_id']+'-point','properties':p,'geometry':{'type':'Point','coordinates':[p['representative_lon'],p['representative_lat']]}}
def bbox_feature(feat):
    p=feat['properties']; return {'type':'Feature','id':p['settlement_id']+'-bbox','properties':p,'geometry':bbox_polygon(p['bbox_wgs84'])}
def build_country(root,iso,features):
    folder=root/'content/countries'/iso; folder.mkdir(parents=True,exist_ok=True)
    (folder/'settlements.geojson').write_text(json.dumps(fc(features),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (folder/'settlement_points.geojson').write_text(json.dumps(fc([point_feature(x) for x in features]),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (folder/'settlement_bboxes.geojson').write_text(json.dumps(fc([bbox_feature(x) for x in features]),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    layers={}; sources={}; tree=[]
    osm_s=uid(); osm_l=uid(); sources[osm_s]=osm_source(); layers[osm_l]={'name':'OpenStreetMap','parameters':{'opacity':1.0,'source':osm_s},'type':'RasterLayer','visible':True}; tree.append(osm_l)
    specs=[('Settlement boundaries','settlements.geojson',{'fill-color':'#d95f0e','stroke-color':'#7f2704','stroke-width':1.25,'circle-fill-color':'#d95f0e','circle-radius':4.0,'circle-stroke-color':'#7f2704','circle-stroke-width':1.0}),('Bounding boxes','settlement_bboxes.geojson',{'fill-color':'#00000000','stroke-color':'#2b8cbe','stroke-width':1.0,'circle-fill-color':'#2b8cbe','circle-radius':3.0}),('Representative coordinates','settlement_points.geojson',{'fill-color':'#31a354','stroke-color':'#006d2c','stroke-width':1.0,'circle-fill-color':'#31a354','circle-radius':5.0,'circle-stroke-color':'#006d2c','circle-stroke-width':1.0})]
    for name,path,color in specs:
        s=uid(); l=uid(); sources[s]=geojson_source(name,path); layers[l]=vector_layer(name,s,color); tree.append(l)
    segment_ids=[]
    for feat in features:
        p=feat['properties']; sid=uid(); segment_ids.append(sid)
        bbox=p['bbox_wgs84']; md=(f"**Classification:** {p.get('classification_label','')}  \n"
          f"**Representative coordinate:** {p['representative_lat']:.6f}, {p['representative_lon']:.6f}  \n"
          f"**BBox (WGS84):** `{bbox}`  \n"
          f"**Source:** {p.get('source_id','')} ({p.get('source_year','')})  \n"
          f"**License:** {p.get('license','')}  \n"
          f"**Geometry status:** {p.get('geometry_status','')}  \n\n"
          f"{p.get('notes','')}")
        layers[sid]=story_segment(p['settlement_name'],bbox,md); tree.append(sid)
    allbbox=[f['properties']['bbox_wgs84'] for f in features]
    merged=[min(x[0] for x in allbbox),min(x[1] for x in allbbox),max(x[2] for x in allbbox),max(x[3] for x in allbbox)]
    center=[(merged[0]+merged[2])/2,(merged[1]+merged[3])/2]
    story_id=uid(); country=features[0]['properties']['country_name']
    doc={'layerTree':tree,'layers':layers,'metadata':{'generatedBy':'scripts/generate_jgis.py','countryISO3':iso},'options':{'bearing':0.0,'extent':bbox_to_webmercator(merged,0.2),'latitude':center[1],'longitude':center[0],'pitch':0.0,'projection':'EPSG:3857','zoom':9.0},'schemaVersion':'0.6.0','sources':sources,'stories':{story_id:{'presentationBgColor':'#171B2C','presentationTextColor':'#F5F5F5','showGradient':True,'storySegments':segment_ids,'storyType':'guided','title':f'{country}: Informal Settlement Evidence'}},'viewState':{}}
    (folder/f'{iso}.jGIS').write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return iso,country,len(features)
def build_global(root,countries):
    folder=root/'content/global'; folder.mkdir(parents=True,exist_ok=True)
    world_s=uid(); world_l=uid(); intro=uid(); story=uid()
    layers={world_l:vector_layer('Natural Earth countries',world_s,{'fill-color':'#f0f0f0','stroke-color':'#636363','stroke-width':0.75,'circle-fill-color':'#636363','circle-radius':3.0}),intro:{'name':'Global overview','parameters':{'content':{'contentMode':'map','image':'','markdown':'This global index is an entry point to country storymaps. Settlement-level completeness depends on the registered sources; country-level SDG 11.1.1 values are context only.','title':'Global Informal Settlements Storymap'},'extent':[-20037508,-15538711,20037508,15538711],'layerOverride':[],'transition':{'time':1.0,'type':'smooth'},'zoom':1.5},'type':'StorySegmentLayer','visible':True}}
    doc={'layerTree':[world_l,intro],'layers':layers,'metadata':{'generatedBy':'scripts/generate_jgis.py'},'options':{'bearing':0.0,'extent':[-20037508,-15538711,20037508,15538711],'latitude':10.0,'longitude':0.0,'pitch':0.0,'projection':'EPSG:3857','zoom':1.5},'schemaVersion':'0.6.0','sources':{world_s:geojson_source('Natural Earth countries','https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson')},'stories':{story:{'presentationBgColor':'#171B2C','presentationTextColor':'#F5F5F5','showGradient':True,'storySegments':[intro],'storyType':'guided','title':'Global Informal Settlements Storymap'}},'viewState':{}}
    (folder/'global_index.jGIS').write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8')
    lines=['# Country storymaps','']+[f"- **{iso} — {name}**: `{n}` settlement feature(s); open `../countries/{iso}/{iso}.jGIS`." for iso,name,n in countries]
    (folder/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
def main():
    root=Path(__file__).resolve().parents[1]; src=root/'content/data/settlements.geojson'; obj=json.loads(src.read_text(encoding='utf-8'))
    out=root/'content/countries'
    if out.exists(): shutil.rmtree(out)
    groups=defaultdict(list)
    for f in obj.get('features',[]): groups[f.get('properties',{}).get('country_iso3','UNK')].append(f)
    built=[build_country(root,k,v) for k,v in sorted(groups.items()) if k!='UNK' and v]
    build_global(root,built); print(f'generated {len(built)} country storymap(s)')
if __name__=='__main__': main()
