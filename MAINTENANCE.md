# Profile display

The profile combines original raster artwork with self-contained SVG instrument panels. Each project monitor links to a public repository. Narrow screens select dedicated mobile layouts with `<picture>`.

`scripts/update_profile.py` reads public user and repository metadata and regenerates the displays. `scripts/project_panels.py` draws the three decorative project instruments. `scripts/render_landscape.py` renders the supplied contribution archive. The public repository count is omitted from both operator layouts.

## Contribution archive

`data/contributions.json` is the authoritative source for **Combined Account Contribution topography**. It contains 1,658 unique dated records totaling 6,715, imported from the owner's `Old Contribution.numbers`, sheet `Random rolls`, table `Table 1`, cells A6:D1663. The workbook's stated coverage is June 1, 2018 through May 31, 2026; its last listed date is May 28, 2026. Source provenance and a SHA-256 fingerprint are stored with the normalized date/count data. The original workbook is not included in this repository.

These are owner-supplied counts, not an independently verified GitHub account merge. No account identifiers were included in the workbook. Dates absent from the source remain unlisted, rather than being assigned confirmed zero contributions. The current account's API calendar is not added, avoiding unrequested changes and possible double counting. This custom image does not alter GitHub's native contribution history.

The eight June–May landscapes preserve every supplied daily value. Height is linear in daily contribution count. Color is decorative and does not encode an additional metric. The rendered date range identifies archive coverage; the operator's refresh date does not imply new contribution data.

## Refreshing

The **Refresh profile instruments** workflow runs daily and can be dispatched manually. It reads the committed archive every time; it never replaces it with a current-account API calendar. It uses the repository's built-in GitHub token for public metadata. A failed update leaves existing committed assets visible. GitHub image caching may delay refreshed graphics.

Render with an authenticated GitHub CLI:

```sh
GH_TOKEN="$(gh auth token)" python3 scripts/update_profile.py
```

For offline rendering, provide the previously fetched public metadata responses `profile.json` and `repos.json`:

```sh
python3 scripts/update_profile.py --input-dir /path/to/metadata
```

To update the archive, replace the normalized daily records and coverage in `data/contributions.json`, reconcile `totalContributions` to the sum of the records, update source provenance, and regenerate both layouts. Preserve the difference between missing dates and known zeros.

Custom styles remain inside the SVG images and do not change GitHub's outer layout or theme. Decorative animations honor reduced-motion preferences.
