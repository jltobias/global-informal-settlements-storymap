# Data-source strategy

## Principle

No single source should be treated as a globally complete inventory of informal-settlement boundaries. The integration model is **source-by-source**, with geometry retained only when the source explicitly maps the phenomenon of interest.

## Recommended source tiers

### Tier A — Explicit settlement/deprived-area geometry

- **Jiang et al. (2026) Permanent Informal Settlements (PIS)** — a circa-2020, 10 m binary GeoTIFF classification across the Global South (Zenodo DOI `10.5281/zenodo.21459094`). It is model-derived raster evidence, not a catalog of locally named settlements. Use `scripts/polygonize_binary_raster.py` locally to convert connected classified pixels into candidate polygons, then normalize and review them. Verify the dataset's current Zenodo Rights/license metadata before redistribution.
- **World Bank / ESA EO4SD-Urban** city datasets. The World Bank catalog exposes spatially explicit probable informal-settlement products for cities such as Dhaka and Karachi, with CC BY 4.0 catalog licensing.
- **IDEAMAPS Network** citywide deprivation outputs, typically represented as approximately 100 × 100 m grid cells. These support deprived-area mapping but are not identical to cadastral settlement boundaries.
- **Humanitarian Data Exchange (HDX)** and municipal/open-data portals can provide additional local layers. License, definition, date, and completeness are dataset-specific.

### Tier B — Gridded and country context, not authoritative settlement boundaries

- **Li et al. slum-population micro-estimates** — 2018 estimates for 129 Global South countries at roughly 3.63 arc-minute neighborhood resolution (Zenodo DOI `10.5281/zenodo.13779003`). Useful as analytical context, not named settlement boundaries.
- **World Bank WDI `EN.POP.SLUM.UR.ZS`**, sourced from UN-Habitat. This is a country-level share of urban population and cannot identify settlement locations.
- UN-Habitat data products and Global Urban Monitoring Framework materials provide definitions and monitoring context.

### Tier C — Contextual covariates, not labels

Built-up footprints, buildings, roads, population, night lights, and land cover can support analysis but must **not** be relabeled as informal settlements without a defensible classification method and validation.

## Registry

`sources/source_registry.json` is intentionally human-reviewable. Add a new entry before ingesting a source. Record:

- provider and title
- geographic scope
- geometry type / spatial unit
- source URL and catalog URL
- date/year
- license
- definition/classification logic
- automated adapter status

## World Bank EO4SD examples

The source registry includes catalog and service/download URLs for:

- Dhaka, Bangladesh (2017 probable informal settlements)
- Karachi, Pakistan (2017 probable informal settlements)

These adapters are disabled by default because external feature services can change availability. Use `scripts/fetch_arcgis_geojson.py` when the service is reachable, then inspect fields and create a mapping JSON before normalization.

## Raster-to-polygon workflow

For a binary classified raster such as the 2026 PIS release:

```bash
python scripts/polygonize_binary_raster.py path/to/PIS_tile.tif \
  --output data/raw/pis_polygons.geojson \
  --license "<license verified from the source record>"
```

Then inspect/dissolve/filter the connected components as appropriate, add country and naming fields from defensible sources, create a mapping JSON, and pass the result through `scripts/normalize_geojson.py`. The raster-derived polygon should retain `geometry_status=model_derived_boundary`; do not upgrade it to a surveyed/administrative boundary without evidence.
