# Canonical settlement schema

Each normalized GeoJSON feature keeps the original geometry and adds a feature-level `bbox` plus canonical properties.

Core fields:

| Field | Meaning |
|---|---|
| `settlement_id` | Stable source-aware identifier |
| `country_iso3` | ISO 3166-1 alpha-3 code |
| `country_name` | Country label used by the source/integration |
| `settlement_name` | Settlement or mapped-area name |
| `source_id` | Key into the source registry |
| `source_url` | Direct or catalog source URL |
| `source_year` | Observation/publication/reference year |
| `license` | Upstream data license |
| `classification_label` | Source-specific classification |
| `classification_definition` | Definition or interpretation notes |
| `confidence` | Source/model confidence when available |
| `geometry_status` | `boundary`, `point_only`, `derived`, or `synthetic` |
| `representative_lon/lat` | WGS84 representative coordinate |
| `representative_method` | How the point was computed |
| `bbox_wgs84` | `[xmin, ymin, xmax, ymax]` |
| `notes` | Quality/provenance caveats |

The default normalizer uses bbox center as the representative coordinate. That is deterministic and robust for irregular source geometries, but it is not guaranteed to fall inside a concave polygon; replace it with a point-on-surface method if that distinction matters.
