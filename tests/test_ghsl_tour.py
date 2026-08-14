import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.fetch_ghsl_ucdb import geometry_bbox, normalize_name
from scripts.generate_human_settlement_tour import bbox_to_webmercator


def test_geometry_bbox_polygon():
    geom = {"type": "Polygon", "coordinates": [[[1, 2], [4, 2], [4, 6], [1, 6], [1, 2]]]}
    assert geometry_bbox(geom) == [1.0, 2.0, 4.0, 6.0]


def test_country_name_normalization():
    assert normalize_name("Côte d'Ivoire") == "cote d ivoire"


def test_webmercator_extent_is_ordered():
    extent = bbox_to_webmercator([-10, -5, 10, 5])
    assert extent[0] < extent[2] and extent[1] < extent[3]
