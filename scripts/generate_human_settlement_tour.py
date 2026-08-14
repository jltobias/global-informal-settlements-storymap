from __future__ import annotations

import json
import math
import uuid
from pathlib import Path
from urllib.parse import urlencode

GHSL_SERVICE = (
    "https://services2.arcgis.com/jUpNdisbWqRpMo35/ArcGIS/rest/services/"
    "Urban_Center_Database_2025_GHSL_Infrastructure/FeatureServer/0/query"
)


def uid() -> str:
    return str(uuid.uuid4())


def lonlat_to_webmercator(lon: float, lat: float) -> tuple[float, float]:
    lat = max(min(lat, 85.05112878), -85.05112878)
    x = lon * 20037508.342789244 / 180.0
    y = math.log(math.tan((90.0 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
    y = y * 20037508.342789244 / 180.0
    return x, y


def bbox_to_webmercator(bbox: list[float], pad: float = 0.08) -> list[float]:
    minx, miny, maxx, maxy = bbox
    dx = max(maxx - minx, 0.05) * pad
    dy = max(maxy - miny, 0.05) * pad
    a = lonlat_to_webmercator(minx - dx, miny - dy)
    b = lonlat_to_webmercator(maxx + dx, maxy + dy)
    return [a[0], a[1], b[0], b[1]]


def merged_bbox(features: list[dict]) -> list[float]:
    bboxes = [f["properties"]["bbox_wgs84"] for f in features]
    return [
        min(b[0] for b in bboxes),
        min(b[1] for b in bboxes),
        max(b[2] for b in bboxes),
        max(b[3] for b in bboxes),
    ]


def osm_source() -> dict:
    return {
        "name": "OpenStreetMap.Mapnik",
        "parameters": {
            "attribution": "© OpenStreetMap contributors",
            "interpolate": False,
            "maxZoom": 19.0,
            "minZoom": 0.0,
            "provider": "OpenStreetMap",
            "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            "urlParameters": {},
        },
        "type": "RasterSource",
    }


def geojson_source(name: str, path: str) -> dict:
    return {"name": name, "parameters": {"path": path}, "type": "GeoJSONSource"}


def vector_layer(name: str, source: str, color: dict, opacity: float = 1.0) -> dict:
    return {
        "name": name,
        "parameters": {
            "color": color,
            "opacity": opacity,
            "source": source,
            "symbologyState": {},
        },
        "type": "VectorLayer",
        "visible": True,
    }


def story_segment(name: str, bbox: list[float], markdown: str, zoom: float) -> dict:
    return {
        "name": name,
        "parameters": {
            "content": {
                "contentMode": "map",
                "image": "",
                "markdown": markdown,
                "title": name,
            },
            "extent": bbox_to_webmercator(bbox),
            "layerOverride": [],
            "transition": {"time": 1.0, "type": "smooth"},
            "zoom": zoom,
        },
        "type": "StorySegmentLayer",
        "visible": True,
    }


def base_doc(title: str, bbox: list[float]) -> tuple[dict, str, str]:
    osm_s, osm_l = uid(), uid()
    cx = (bbox[0] + bbox[2]) / 2
    cy = (bbox[1] + bbox[3]) / 2
    doc = {
        "layerTree": [osm_l],
        "layers": {
            osm_l: {
                "name": "OpenStreetMap",
                "parameters": {"opacity": 1.0, "source": osm_s},
                "type": "RasterLayer",
                "visible": True,
            }
        },
        "metadata": {"generatedBy": "scripts/generate_human_settlement_tour.py"},
        "options": {
            "bearing": 0.0,
            "extent": bbox_to_webmercator(bbox),
            "latitude": cy,
            "longitude": cx,
            "pitch": 0.0,
            "projection": "EPSG:3857",
            "zoom": 2.0,
        },
        "schemaVersion": "0.6.0",
        "sources": {osm_s: osm_source()},
        "stories": {},
        "viewState": {},
    }
    return doc, osm_s, osm_l


def fmt_int(value) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "n/a"


def build_country(root: Path, country_key: str, features: list[dict]) -> dict:
    props0 = features[0]["properties"]
    country_name = props0["country_name"]
    bbox = merged_bbox(features)
    doc, _, _ = base_doc(f"{country_name}: GHSL Urban Centres", bbox)

    points_s, points_l = uid(), uid()
    doc["sources"][points_s] = geojson_source(
        "GHSL urban-centre centroids", "centres.geojson"
    )
    doc["layers"][points_l] = vector_layer(
        "GHSL urban-centre centroids",
        points_s,
        {
            "fill-color": "#2b8cbe",
            "stroke-color": "#045a8d",
            "stroke-width": 1.0,
            "circle-fill-color": "#2b8cbe",
            "circle-radius": 5.0,
            "circle-stroke-color": "#045a8d",
            "circle-stroke-width": 1.0,
        },
    )
    doc["layerTree"].append(points_l)

    escaped = country_name.replace("'", "''")
    query = urlencode(
        {
            "where": f"GC_CNT_GAD_2025='{escaped}'",
            "outFields": "ID_UC_G0,GC_UCN_MAI_2025,GC_CNT_GAD_2025,GC_UCA_KM2_2025,GC_POP_TOT_2025,GH_BUS_TOT_2020,GH_BUS_TOT_2025",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
            "resultRecordCount": 2000,
        }
    )
    poly_s, poly_l = uid(), uid()
    doc["sources"][poly_s] = geojson_source(
        "GHSL UCDB 2025 urban-centre polygons", f"{GHSL_SERVICE}?{query}"
    )
    doc["layers"][poly_l] = vector_layer(
        "GHSL UCDB 2025 urban-centre polygons",
        poly_s,
        {
            "fill-color": "#fdae6b",
            "stroke-color": "#e6550d",
            "stroke-width": 1.0,
            "circle-fill-color": "#fdae6b",
            "circle-radius": 4.0,
            "circle-stroke-color": "#e6550d",
            "circle-stroke-width": 1.0,
        },
        opacity=0.55,
    )
    doc["layerTree"].append(poly_l)

    segment_ids = []
    for n, feature in enumerate(features, 1):
        p = feature["properties"]
        sid = uid()
        segment_ids.append(sid)
        growth = None
        b20, b25 = p.get("GH_BUS_TOT_2020"), p.get("GH_BUS_TOT_2025")
        if isinstance(b20, (int, float)) and b20 and isinstance(b25, (int, float)):
            growth = (b25 - b20) / b20 * 100.0
        md = (
            f"**Country:** {country_name}  \n"
            f"**Urban centre:** {p['urban_centre_name']}  \n"
            f"**Tour position:** {n:,} of {len(features):,}  \n"
            f"**2025 population:** {fmt_int(p.get('GC_POP_TOT_2025'))}  \n"
            f"**2025 urban-centre area:** {fmt_int(p.get('GC_UCA_KM2_2025'))} km²  \n"
            f"**Built-up surface 2020:** {fmt_int(b20)} m²  \n"
            f"**Built-up surface 2025:** {fmt_int(b25)} m²  \n"
            + (
                f"**Built-up change 2020→2025:** {growth:+.1f}%  \n"
                if growth is not None
                else ""
            )
            + f"**Representative coordinate:** {p['representative_lat']:.5f}, {p['representative_lon']:.5f}  \n"
            f"**Bounding box:** `{p['bbox_wgs84']}`  \n\n"
            "Source: European Commission JRC, GHS-UCDB R2024A. The orange polygon is loaded live from the public FeatureServer."
        )
        doc["layers"][sid] = story_segment(
            p["urban_centre_name"], p["bbox_wgs84"], md, 10.5
        )
        doc["layerTree"].append(sid)

    story_id = uid()
    doc["stories"][story_id] = {
        "presentationBgColor": "#171B2C",
        "presentationTextColor": "#F5F5F5",
        "showGradient": True,
        "storySegments": segment_ids,
        "storyType": "guided",
        "title": f"{country_name}: {len(features):,} GHSL Urban Centres",
    }
    doc["metadata"].update(
        {
            "title": f"{country_name}: GHSL Urban Centres",
            "countryKey": country_key,
            "countryISO3": props0.get("country_iso3", ""),
            "urbanCentreCount": str(len(features)),
            "source": "GHS-UCDB R2024A / public ArcGIS FeatureServer",
        }
    )
    folder = root / "content" / "human-settlements" / country_key
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{country_key}.jGIS").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {
        "key": country_key,
        "name": country_name,
        "count": len(features),
        "bbox": bbox,
        "features": features,
    }


def build_global(root: Path, countries: list[dict]) -> None:
    world_bbox = [-180.0, -60.0, 180.0, 85.0]
    doc, _, _ = base_doc("Global Human Settlements Tour", world_bbox)
    points_s, points_l = uid(), uid()
    doc["sources"][points_s] = geojson_source(
        "GHSL urban-centre centroids", "ghsl_urban_centres.geojson"
    )
    doc["layers"][points_l] = vector_layer(
        "GHSL R2024A urban centres (11k+)",
        points_s,
        {
            "fill-color": "#31a354",
            "stroke-color": "#006d2c",
            "stroke-width": 0.8,
            "circle-fill-color": "#31a354",
            "circle-radius": 4.0,
            "circle-stroke-color": "#006d2c",
            "circle-stroke-width": 0.8,
        },
    )
    doc["layerTree"].append(points_l)

    intro = uid()
    total = sum(c["count"] for c in countries)
    doc["layers"][intro] = story_segment(
        "Global Human Settlements Tour",
        world_bbox,
        f"This tour indexes **{total:,} GHSL quality-controlled urban centres** by country using GHS-UCDB R2024A. Use the story controls to move country-by-country. Open a country's `.jGIS` file in `human-settlements/<country>/` to cycle through every centre in that country.  \n\nThe green points are a compact browser representation derived from the official GHSL 2025 urban-centre polygons. The original informal-settlement atlas remains a separate evidence layer in this repository.",
        1.5,
    )
    doc["layerTree"].append(intro)
    segments = [intro]

    for country in sorted(countries, key=lambda c: c["name"]):
        sid = uid()
        segments.append(sid)
        top = sorted(
            country["features"],
            key=lambda f: -(f["properties"].get("GC_POP_TOT_2025") or 0),
        )[:5]
        names = ", ".join(f["properties"]["urban_centre_name"] for f in top)
        link = f"../human-settlements/{country['key']}/{country['key']}.jGIS"
        md = (
            f"**{country['name']}** contains **{country['count']:,}** GHSL urban centres in this release.  \n\n"
            f"Largest centres in the compact catalog: {names or 'n/a'}.  \n\n"
            f"[Open the centre-by-centre country tour]({link})  \n\n"
            "Use the AI chat panel to ask for comparisons, trends, or explanations of GHSL fields. Do not treat GHSL urban-centre status as evidence that an area is an informal settlement."
        )
        doc["layers"][sid] = story_segment(
            country["name"], country["bbox"], md, 4.5
        )
        doc["layerTree"].append(sid)

    story_id = uid()
    doc["stories"][story_id] = {
        "presentationBgColor": "#171B2C",
        "presentationTextColor": "#F5F5F5",
        "showGradient": True,
        "storySegments": segments,
        "storyType": "guided",
        "title": "Global Human Settlements by Country — GHSL UCDB R2024A",
    }
    doc["metadata"].update(
        {
            "title": "Global Human Settlements by Country",
            "urbanCentreCount": str(total),
            "countryGroupCount": str(len(countries)),
            "source": "European Commission JRC GHS-UCDB R2024A",
            "sourceService": GHSL_SERVICE.rsplit("/query", 1)[0],
        }
    )
    out = root / "content" / "global" / "Global_Human_Settlements_Tour.jGIS"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    index_path = root / "content" / "global" / "ghsl_country_index.json"
    if not index_path.exists():
        raise SystemExit("Run scripts/fetch_ghsl_ucdb.py first")
    rows = json.loads(index_path.read_text(encoding="utf-8"))
    countries = []
    for row in rows:
        key = row["country_key"]
        path = root / "content" / "human-settlements" / key / "centres.geojson"
        obj = json.loads(path.read_text(encoding="utf-8"))
        features = obj.get("features", [])
        if features:
            countries.append(build_country(root, key, features))
    build_global(root, countries)
    print(f"generated global tour and {len(countries)} country tours")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
