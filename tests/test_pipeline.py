import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_validate():
    p=subprocess.run([sys.executable,str(ROOT/'scripts/validate.py')],cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0,p.stdout+p.stderr
def test_demo_is_explicitly_synthetic():
    d=json.loads((ROOT/'content/data/settlements.geojson').read_text())
    assert d['features']
    assert all(f['properties']['geometry_status']=='synthetic' for f in d['features'])
def test_storymap_has_boundary_point_bbox_layers():
    p=ROOT/'content/countries/XDM/XDM.jGIS'; d=json.loads(p.read_text())
    names={v['name'] for v in d['layers'].values()}
    assert {'Settlement boundaries','Bounding boxes','Representative coordinates'}.issubset(names)

def test_live_showcase_uses_real_remote_polygon_layer():
    p=ROOT/'content/showcase/Ekurhuleni_Informal_Settlements_Story_Map.jGIS'
    d=json.loads(p.read_text())
    remote=[s for s in d['sources'].values() if s.get('type')=='GeoJSONSource']
    assert len(remote)==1
    path=remote[0]['parameters']['path']
    assert 'gis.ekurhuleni.gov.za' in path and 'MapServer/7/query' in path and 'f=geojson' in path
    story=next(iter(d['stories'].values()))
    assert story['storyType']=='guided'
    assert len(story['storySegments'])>=5
    assert d['metadata']['exampleType']=='live remote polygon showcase'
    assert d['metadata']['sourceLayer']=='Informal Settlements'
