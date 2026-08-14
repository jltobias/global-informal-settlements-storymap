# Global Informal Settlements Storymap

A reproducible starter repository for building a **country-by-country global storymap of informal settlements** with **JupyterGIS**, **JupyterLite**, and GitHub Pages.

The repository deliberately separates three kinds of evidence:

1. **Settlement geometry** — Polygon/MultiPolygon boundaries when an explicit spatial source is available.
2. **Representative coordinates and bounding boxes** — derived for every normalized feature and stored alongside the source geometry.
3. **Country context** — UN-Habitat / World Bank SDG 11.1.1 context (`EN.POP.SLUM.UR.ZS`) used only as country-level context, never as a substitute for settlement boundaries.

> **Important:** there is no single globally complete, authoritative polygon inventory of informal settlements. This project is therefore a provenance-first integration framework. The shipped `XDM` data are synthetic smoke-test geometries; do not interpret them as real settlements.

## What is included

- Browser-only JupyterGIS + Xeus-Python environment for JupyterLite.
- GitHub Pages deployment workflow.
- A canonical GeoJSON schema containing source, date, license, classification, representative latitude/longitude, geometry quality, and bbox fields.
- Data-source registry for the 2026 10 m Global South PIS raster release, 129-country slum-population micro-estimates, World Bank WDI, World Bank EO4SD-Urban examples, IDEAMAPS, UN-Habitat context, and extensible local/HDX inputs.
- Pure-Python GeoJSON normalization (no GeoPandas required in the browser), plus an optional local rasterio polygonizer for binary classification rasters.
- JupyterGIS `.jGIS` generation with separate **boundary**, **representative point**, and **bounding-box** layers.
- One guided story segment per settlement feature.
- Country index covering all ISO 3166-1 countries, with flags for geometry availability and WDI context.
- Data-quality tests and an ethics/provenance checklist.

## Repository layout

```text
content/
  notebooks/                  JupyterLite notebooks
  data/                       normalized catalog and country context
  countries/                  generated country storymaps and GeoJSON sidecars
  global/                     global JupyterGIS index project
scripts/                      ingestion, normalization, generation, validation
data/raw/                     place source GeoJSON here
sources/source_registry.json  source catalog and adapter hints
.github/workflows/            GitHub Pages build/deploy
```

## Fast start

1. Open `content/notebooks/00_Welcome.ipynb` in JupyterLite.
2. Add source GeoJSON files to `data/raw/` and a mapping JSON describing property names.
3. Run `python scripts/normalize_geojson.py ...` locally, or use notebook `02_Normalize_Settlements.ipynb`.
4. Run `python scripts/generate_jgis.py` to rebuild country storymaps.
5. Push to `main`; the GitHub Actions workflow builds and deploys JupyterLite to Pages.

## GitHub Pages

The workflow builds JupyterLite with `jupyterlite-xeus` and `jupytergis-lite`, mounts the site content into the browser kernel, validates the repository, uploads the static artifact, and deploys with GitHub Pages Actions.

After creating the repository on GitHub, set **Settings → Pages → Build and deployment → Source** to **GitHub Actions** if it is not already selected.

## Adding real data

See [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md), [`docs/SCHEMA.md`](docs/SCHEMA.md), and notebook `06_Add_New_Source.ipynb`. A source should be added only when its definition, spatial unit, date, license, and provenance are understood. Never infer that a dense or low-income neighborhood is an informal settlement solely from morphology.

## Source notes

- JupyterGIS story maps: https://jupytergis.readthedocs.io/en/latest/user_guide/how-tos/story-maps.html
- JupyterLite GitHub Pages: https://jupyterlite.readthedocs.io/en/latest/quickstart/deploy.html
- JupyterLite-Xeus environments: https://jupyterlite-xeus.readthedocs.io/en/latest/environment.html
- World Bank WDI indicator metadata: https://databank.worldbank.org/metadataglossary/world-development-indicators/series/EN.POP.SLUM.UR.ZS
- IDEAMAPS: https://www.ideamapsnetwork.org/

## License

Code and documentation in this repository are MIT licensed. **Upstream data retain their own licenses.** Every imported settlement record must preserve source and license fields. See `docs/DATA_LICENSES.md`.
