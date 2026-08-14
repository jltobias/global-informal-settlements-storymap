# Global Informal Settlements + Human Settlements Storymap

A browser-first **JupyterGIS + JupyterLite** atlas that combines two related but distinct views:

1. a provenance-first atlas of **informal-settlement evidence**, and
2. a global **GHSL human-settlements tour** indexed by country and generated from the European Commission JRC GHS-UCDB R2024A urban-centre layer.

The deployed JupyterLab also includes **jupyterlite-ai**, so the map and notebooks can be explored with an interactive AI chat panel.

## 🚀 Live demos

### Global GHSL tour + AI chat

> **[Launch the Global Human Settlements Tour with the AI sidebar](https://jltobias.github.io/global-informal-settlements-storymap/lab/index.html?path=global/Global_Human_Settlements_Tour.jGIS)**

This is the primary demo. The build fetches the current public GHSL UCDB R2024A FeatureServer, reduces the 11,000+ quality-controlled urban-centre polygons to a lightweight browser catalog, and creates:

- a **world story** with one guided chapter per country group;
- a **country story** for every country represented in the GHSL layer; and
- one guided story segment for **every GHSL urban centre** inside each country story.

For a presentation-focused view without emphasizing the full JupyterLab workspace:

> **[Launch the Global Human Settlements Tour in single-document mode](https://jltobias.github.io/global-informal-settlements-storymap/lab/index.html?path=global/Global_Human_Settlements_Tour.jGIS&mode=single-document)**

### Informal-settlement showcase

> **[Launch the Ekurhuleni Informal Settlements Story Map](https://jltobias.github.io/global-informal-settlements-storymap/lab/index.html?path=showcase/Ekurhuleni_Informal_Settlements_Story_Map.jGIS&mode=single-document)**

This example uses live City of Ekurhuleni municipal **Informal Settlements** polygons and demonstrates the stricter provenance model used for informal-settlement evidence.

### Notebook.link

> **[Launch the repository on Notebook.link](https://notebook.link/github.com/jltobias/global-informal-settlements-storymap/)**

Notebook.link loads the GitHub repository into a browser Jupyter environment. For the most predictable GHSL demo, use the GitHub Pages link above because the Pages workflow refreshes and generates the GHSL tour before deployment.

## 🤖 AI chat

The Pages build installs `jupyterlite-ai`. In the full JupyterLab link, open the AI/chat icon in the sidebar, add a provider, and start prompting. Supported configurations include OpenAI, Anthropic, Mistral and Generic OpenAI-compatible endpoints.

**No API key is stored in this repository.** Each user supplies credentials in the browser, or an organization can point the Generic provider at a controlled gateway/proxy. See [`docs/AI_CHAT.md`](docs/AI_CHAT.md).

Useful prompts include:

- “Compare the largest GHSL urban centres in this country by 2025 population.”
- “Explain built-up-surface change between 2000 and 2025 for this centre.”
- “What is the difference between a GHSL urban centre and an informal settlement?”
- “Show me Python that loads `global/ghsl_urban_centres.geojson` and filters one country.”

## 🌍 How the global tour works

The build queries the public **GHS-UCDB R2024A / 2025 urban-centre** FeatureServer in pages of 2,000 records. It keeps a compact set of attributes useful for browser exploration, including urban-centre name, country, 2025 population, area, selected built-up-surface values and selected population time-series values.

For each GHSL urban-centre polygon the build derives a representative longitude/latitude and a WGS84 bounding box. Those compact records are written to:

```text
content/global/ghsl_urban_centres.geojson
content/global/ghsl_country_index.json
content/human-settlements/<COUNTRY>/centres.geojson
```

Then `scripts/generate_human_settlement_tour.py` creates:

```text
content/global/Global_Human_Settlements_Tour.jGIS
content/human-settlements/<COUNTRY>/<COUNTRY>.jGIS
```

The global story cycles **country by country**. Each country story cycles **centre by centre**, preserving the source fields and loading the corresponding GHSL polygon layer live from the public service.

### Why UCDB instead of bundling the full GHS-BUILT-S raster?

The GHS-BUILT-S raster is valuable contextual evidence, but the global 100 m/10 m products are too large to sensibly bundle into a static GitHub Pages site. GHS-UCDB R2024A provides a harmonized global set of quality-controlled urban-centre spatial entities and multi-temporal GHSL attributes, making it much better suited to a responsive browser story tour. The source registry and notebooks can still reference or process GHS-BUILT-S for deeper analysis.

## ⚠️ Human settlements are not the same as informal settlements

GHSL is a global human-settlement and built-environment framework. **A GHSL urban centre is not an informal-settlement classification.** The global GHSL tour must not be interpreted as a global map of slums.

The informal-settlement side of this repository deliberately separates:

1. **Settlement geometry** — Polygon/MultiPolygon boundaries when an explicit spatial source is available.
2. **Representative coordinates and bounding boxes** — derived for every normalized feature.
3. **Country context** — UN-Habitat / World Bank SDG 11.1.1 context used as statistical context, never as substitute geometry.

There is no single globally complete authoritative polygon inventory of informal settlements. Administrative inventories, survey/community sources and model-derived classifications therefore retain their own definitions, dates, licenses and provenance.

## Repository layout

```text
content/
  global/                     generated GHSL world tour and global compact catalog
  human-settlements/          generated GHSL country tours
  showcase/                   live informal-settlement demonstration
  notebooks/                  JupyterLite notebooks
  countries/                  informal-settlement country storymaps
  data/                       normalized informal-settlement and country context
scripts/
  fetch_ghsl_ucdb.py          refresh current GHSL urban-centre catalog
  generate_human_settlement_tour.py
  generate_jgis.py            informal-settlement story generator
sources/source_registry.json  source catalog and adapter hints
docs/AI_CHAT.md               AI provider setup and prompt examples
.github/workflows/            GitHub Pages build/deploy
```

## Local / reproducible build

```bash
python scripts/build_catalog.py
python scripts/generate_jgis.py
python scripts/fetch_ghsl_ucdb.py
python scripts/generate_human_settlement_tour.py
python scripts/validate.py
jupyter lite build --contents content --output-dir dist --XeusAddon.mount_jupyterlite_content=True
```

The GitHub Actions workflow performs these steps automatically on every push to `main` and deploys the resulting static JupyterLite application to GitHub Pages.

## Existing informal-settlement workflow

See [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md), [`docs/SCHEMA.md`](docs/SCHEMA.md), and notebook `06_Add_New_Source.ipynb`. A source should be added only when its definition, spatial unit, date, license and provenance are understood. Never infer that a dense, built-up or low-income neighborhood is an informal settlement solely from morphology.

## Key upstream references

- GHSL Urban Centre Database R2024A: https://human-settlement.emergency.copernicus.eu/ghs_ucdb_2024.php
- GHSL data download: https://human-settlement.emergency.copernicus.eu/download.php
- JupyterGIS story maps: https://jupytergis.readthedocs.io/en/latest/user_guide/how-tos/story-maps.html
- JupyterLite: https://jupyterlite.readthedocs.io/
- JupyterLite AI: https://jupyterlite-ai.readthedocs.io/
- Notebook.link JupyterGIS: https://notebook.link/docs/build-content/jupytergis-project/
- World Bank WDI slum-share context: https://databank.worldbank.org/metadataglossary/world-development-indicators/series/EN.POP.SLUM.UR.ZS

## License

Code and documentation in this repository are MIT licensed. **Upstream data retain their own licenses and attribution requirements.** GHSL data are reused with European Commission/JRC attribution; informal-settlement datasets retain their source-specific terms. See `docs/DATA_LICENSES.md`.
