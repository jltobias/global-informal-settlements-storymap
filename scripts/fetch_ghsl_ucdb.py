from __future__ import annotations

import argparse
import csv
import json
import math
import re
import time
import unicodedata
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SERVICE = (
    "https://services2.arcgis.com/jUpNdisbWqRpMo35/ArcGIS/rest/services/"
    "Urban_Center_Database_2025_GHSL_Infrastructure/FeatureServer/0/query"
)
FIELDS = [
    "OBJECTID",
    "ID_UC_G0",
    "GC_UCN_MAI_2025",
    "GC_CNT_GAD_2025",
    "GC_UCA_KM2_2025",
    "GC_POP_TOT_2025",
    "GC_DEV_WIG_2025",
    "GC_DEV_USR_2025",
    "GH_BUS_TOT_2000",
    "GH_BUS_TOT_2010",
    "GH_BUS_TOT_2020",
    "GH_BUS_TOT_2025",
    "GH_POP_TOT_2000",
    "GH_POP_TOT_2010",
    "GH_POP_TOT_2020",
    "GH_POP_TOT_2025",
]

ALIASES = {
    "bolivia": "BOL",
    "brunei": "BRN",
    "cape verde": "CPV",
    "congo": "COG",
    "democratic republic of the congo": "COD",
    "democratic republic of congo": "COD",
    "czech republic": "CZE",
    "ivory coast": "CIV",
    "iran": "IRN",
    "laos": "LAO",
    "moldova": "MDA",
    "north korea": "PRK",
    "south korea": "KOR",
    "palestine": "PSE",
    "russia": "RUS",
    "syria": "SYR",
    "taiwan": "TWN",
    "tanzania": "TZA",
    "turkey": "TUR",
    "united states of america": "USA",
    "usa": "USA",
    "venezuela": "VEN",
    "vietnam": "VNM",
}


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().lower()
    return re.sub(r"\s+", " ", value)


def iso_lookup(path: Path) -> dict[str, str]:
    result = dict(ALIASES)
    if not path.exists():
        return result
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            iso = (row.get("iso3") or "").strip()
            name = (row.get("country_name") or "").strip()
            if iso and name:
                result[normalize_name(name)] = iso
    return result


def geometry_bbox(geometry: dict) -> list[float] | None:
    coords = geometry.get("coordinates") if geometry else None
    if not coords:
        return None

    points: list[tuple[float, float]] = []

    def walk(obj):
        if isinstance(obj, list) and len(obj) >= 2 and all(
            isinstance(v, (int, float)) for v in obj[:2]
        ):
            x, y = float(obj[0]), float(obj[1])
            if math.isfinite(x) and math.isfinite(y):
                points.append((x, y))
            return
        if isinstance(obj, list):
            for child in obj:
                walk(child)

    walk(coords)
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def request_page(offset: int, page_size: int, timeout: int = 90) -> dict:
    params = {
        "where": "1=1",
        "outFields": ",".join(FIELDS),
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
        "resultOffset": offset,
        "resultRecordCount": page_size,
        "orderByFields": "OBJECTID",
    }
    req = Request(
        f"{SERVICE}?{urlencode(params)}",
        headers={"User-Agent": "global-human-settlements-storymap/1.0"},
    )
    with urlopen(req, timeout=timeout) as response:
        return json.load(response)


def fetch_all(page_size: int = 2000) -> list[dict]:
    features: list[dict] = []
    offset = 0
    while True:
        payload = request_page(offset, page_size)
        page = payload.get("features", [])
        if not page:
            break
        features.extend(page)
        print(f"fetched {len(features):,} GHSL urban centres")
        if len(page) < page_size:
            break
        offset += len(page)
        time.sleep(0.15)
    return features


def build_point_features(
    features: list[dict], lookup: dict[str, str]
) -> tuple[list[dict], dict[str, dict]]:
    out: list[dict] = []
    countries: dict[str, dict] = {}
    for feature in features:
        props = dict(feature.get("properties") or {})
        country_name = str(props.get("GC_CNT_GAD_2025") or "Unknown").strip()
        iso3 = lookup.get(normalize_name(country_name), "")
        bbox = geometry_bbox(feature.get("geometry") or {})
        if not bbox:
            continue
        lon = (bbox[0] + bbox[2]) / 2
        lat = (bbox[1] + bbox[3]) / 2
        props.update(
            {
                "country_iso3": iso3,
                "country_name": country_name,
                "urban_centre_name": props.get("GC_UCN_MAI_2025") or "Unnamed urban centre",
                "representative_lon": lon,
                "representative_lat": lat,
                "bbox_wgs84": bbox,
                "source": "GHSL GHS-UCDB R2024A (2025 urban-centre delineation)",
                "source_service": SERVICE.rsplit("/query", 1)[0],
            }
        )
        out.append(
            {
                "type": "Feature",
                "id": str(props.get("ID_UC_G0") or props.get("OBJECTID")),
                "properties": props,
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            }
        )
        key = iso3 or f"NAME-{normalize_name(country_name).replace(' ', '-').upper()}"
        rec = countries.setdefault(
            key,
            {"country_iso3": iso3, "country_name": country_name, "features": []},
        )
        rec["features"].append(out[-1])
    return out, countries


def write_outputs(root: Path, points: list[dict], countries: dict[str, dict]) -> None:
    global_dir = root / "content" / "global"
    global_dir.mkdir(parents=True, exist_ok=True)
    (global_dir / "ghsl_urban_centres.geojson").write_text(
        json.dumps(
            {"type": "FeatureCollection", "features": points},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )

    index_rows = []
    human_root = root / "content" / "human-settlements"
    human_root.mkdir(parents=True, exist_ok=True)
    for key, rec in sorted(countries.items(), key=lambda kv: kv[1]["country_name"]):
        folder = human_root / key
        folder.mkdir(parents=True, exist_ok=True)
        features = sorted(
            rec["features"],
            key=lambda f: (
                -(f["properties"].get("GC_POP_TOT_2025") or 0),
                f["properties"]["urban_centre_name"],
            ),
        )
        (folder / "centres.geojson").write_text(
            json.dumps(
                {"type": "FeatureCollection", "features": features},
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        index_rows.append(
            {
                "country_key": key,
                "country_iso3": rec["country_iso3"],
                "country_name": rec["country_name"],
                "urban_centre_count": len(features),
            }
        )

    (global_dir / "ghsl_country_index.json").write_text(
        json.dumps(index_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(points):,} centres across {len(index_rows):,} country groups")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch and compact GHSL UCDB R2024A urban centres for JupyterGIS."
    )
    parser.add_argument("--root", default=None)
    parser.add_argument("--page-size", type=int, default=2000)
    parser.add_argument("--offline-ok", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    lookup = iso_lookup(root / "content" / "data" / "iso_countries.csv")
    try:
        raw = fetch_all(args.page_size)
    except Exception as exc:
        cached = root / "content" / "global" / "ghsl_urban_centres.geojson"
        if args.offline_ok and cached.exists():
            print(f"GHSL refresh failed; keeping cached output: {exc}")
            return 0
        raise
    points, countries = build_point_features(raw, lookup)
    if len(points) < 10000:
        raise RuntimeError(
            f"Expected roughly 11,000 GHSL urban centres, received only {len(points)}"
        )
    write_outputs(root, points, countries)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
