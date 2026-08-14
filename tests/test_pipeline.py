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
