# Live story-map demo

The repository ships a real-data guided JupyterGIS document at:

`content/showcase/Ekurhuleni_Informal_Settlements_Story_Map.jGIS`

A root-level copy, `Informal_Settlements_Story_Map.jGIS`, makes the example easy to locate when the whole GitHub repository is launched with Notebook.link.

## Launch

Notebook.link:

`https://notebook.link/@jltobias/global-informal-settlements-storymap`

GitHub Pages, after deployment:

`https://jltobias.github.io/global-informal-settlements-storymap/lab/index.html?path=showcase/Ekurhuleni_Informal_Settlements_Story_Map.jGIS&mode=single-document`

JupyterLite supports the `?path=` URL parameter for opening a bundled file directly.

## Data source

The showcase points directly to the City of Ekurhuleni Metropolitan Municipality ArcGIS REST layer named **Informal Settlements** (MapServer layer 7). The layer is polygon geometry and advertises GeoJSON query support. Available attributes include `INFML_SETTLEM_NAME`, `HH_2016`, `HECTARES`, `WARD`, `CLASSIFICATION`, `WATER`, `SANITATION`, `LIGHTING`, and `NUSP_CATEGORY`.

The map deliberately reads the municipal polygons live. If the upstream service is temporarily unavailable, the story layer will not render. This makes data currency and provenance explicit rather than silently freezing a copy.

## Presentation

Open the `.jGIS` file, switch the Story panel to Preview mode or open it with Specta presentation mode, and step through the guided chapters. Use the Identify tool on an orange polygon to inspect source attributes.
