# Profile display

The profile combines original raster artwork with self-contained SVG instrument panels. Each project monitor links to a public repository. Smaller panel variants are selected on narrow screens with `<picture>`.

`scripts/update_profile.py` reads the public user and repository endpoints plus GitHub's contribution calendar, then regenerates the SVG assets. `scripts/render_landscape.py` draws one crystal per date with linear contribution-count heights. Rainbow colors distinguish weekday rows and do not encode counts. Project-panel diagrams are decorative.

The **Refresh profile instruments** workflow runs daily and can also be dispatched manually. It uses the repository's built-in GitHub token; no personal access token or third-party widget service is required. A failed update leaves the existing committed assets visible. GitHub image caching may delay when refreshed graphics appear.

To render locally with an authenticated GitHub CLI:

```sh
GH_TOKEN="$(gh auth token)" python3 scripts/update_profile.py
```

To render without network access, provide a directory containing JSON responses named `profile.json`, `repos.json`, and `contributions.json`:

```sh
python3 scripts/update_profile.py --input-dir /path/to/data
```

The contribution display reports GitHub activity, including anonymized counts that GitHub makes available. It does not measure time spent or skill. The asset's date range indicates its coverage.

Custom CSS and SVG animation are confined to the SVG images. The README does not change GitHub's outer layout or theme. Reduced-motion preferences disable the decorative cursor and scan animations.
