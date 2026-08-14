# Create the GitHub repository

Suggested repository name: `global-informal-settlements-storymap`

With GitHub CLI installed and authenticated:

```bash
git init
git add .
git commit -m "Initial JupyterGIS global informal settlements storymap"
git branch -M main
gh repo create global-informal-settlements-storymap --public --source=. --remote=origin --push
```

Then open repository **Settings → Pages** and select **GitHub Actions** as the Pages source if required.
