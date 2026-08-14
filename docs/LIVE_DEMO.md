# Live JupyterGIS story-map demo

The repository now includes a ready-to-open story map at the repository root:

`Informal_Settlements_Story_Map.jGIS`

It uses a live public **City of Ekurhuleni Metropolitan Municipality** ArcGIS polygon layer titled **Informal Settlements**. The geometry is fetched when the JupyterGIS document opens, so the example is not based on the repository's synthetic smoke-test polygons.

## Open it with Notebook.link

Use:

`https://notebook.link/@jltobias/global-informal-settlements-storymap`

Then open `Informal_Settlements_Story_Map.jGIS` from the file browser. When the repository's GitHub Pages/JupyterLite deployment is active, the same file is bundled into the browser environment.

## Story chapters

The guided story contains six chapters:

1. Metro-wide overview
2. Northern Ekurhuleni — Thembisa area
3. Eastern Ekurhuleni — Benoni area
4. Western Ekurhuleni — Germiston area
5. Southern Ekurhuleni — Katlehong area
6. From one city to a global atlas

## Explore the data

Use JupyterGIS's Identify tool and click an orange polygon. The municipal service exposes fields including settlement name, households (2016 field), hectares, ward, classification, water, sanitation, lighting, and NUSP category when populated.

## Provenance

Source: City of Ekurhuleni Metropolitan Municipality ArcGIS REST service, `Ekurhuleni_Propety_Data_Map/MapServer/7`, layer name `Informal Settlements`.

The project treats these as source-defined administrative polygons. Informal-settlement status and boundaries can change, so downstream use should preserve source, date, license/terms, and quality notes rather than treating a geometry as timeless ground truth.
