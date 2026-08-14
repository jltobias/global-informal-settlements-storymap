# AI chat in the Global Human Settlements Atlas

The GitHub Pages build installs **jupyterlite-ai**, which adds an AI chat panel to the same browser-based JupyterLab interface that hosts the JupyterGIS story maps.

## Launch

Open the Global Human Settlements Tour in the full JupyterLab interface:

https://jltobias.github.io/global-informal-settlements-storymap/lab/index.html?path=global/Global_Human_Settlements_Tour.jGIS

Use the AI/chat icon in the JupyterLab sidebar. If no provider is configured, open the AI settings and add a provider. JupyterLite AI supports direct providers such as OpenAI, Anthropic and Mistral, and a Generic OpenAI-compatible endpoint.

**Do not commit API keys to this repository.** Provider credentials belong in the user's browser settings or in a controlled OpenAI-compatible gateway/proxy.

## Suggested prompts

- Summarize what the GHSL fields on the currently inspected urban centre mean.
- Compare population and built-up surface change for the largest centres in this country.
- Explain the difference between a GHSL urban centre and an informal settlement.
- Which attributes in this atlas are source data and which were derived by the build pipeline?
- Write Python to load `global/ghsl_urban_centres.geojson` and rank urban centres by 2025 population.
- Help me join a country informal-settlement inventory to the GHSL urban-centre context without treating built-up morphology as proof of informality.

## Interpretation guardrail

GHSL describes human settlement, built-up surface, population and Degree of Urbanisation classes. It does **not** by itself identify an area as an informal settlement. Informal-settlement classification must come from an explicit administrative, survey, community-mapping or model-derived source whose definition and provenance are preserved.
