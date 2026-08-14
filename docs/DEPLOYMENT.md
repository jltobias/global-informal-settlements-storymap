# Deployment

## GitHub Pages

1. Create a GitHub repository and push this repository to `main`.
2. In **Settings → Pages**, choose **GitHub Actions** as the source.
3. The workflow `.github/workflows/deploy-pages.yml` will:
   - refresh the World Bank country-level context when reachable,
   - rebuild the country index and JupyterGIS projects,
   - validate the content,
   - build JupyterLite with Xeus-Python and `jupytergis-lite`,
   - upload and deploy the Pages artifact.
4. The site will normally be at `https://<owner>.github.io/<repository>/`.

## Local build

Use a conda/mamba environment with JupyterLite Core and JupyterLite-Xeus, then run:

```bash
python scripts/build_catalog.py
python scripts/generate_jgis.py
python scripts/validate.py
jupyter lite build --contents content --output-dir dist --XeusAddon.mount_jupyterlite_content=True
python -m http.server -d dist 8000
```

The content mount is enabled because Xeus documentation notes that embedding JupyterLite content into the kernel is more robust than relying on service-worker access.
