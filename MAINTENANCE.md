# Profile display

The visible profile is intentionally compact: original island artwork, name and location, repository and LinkedIn links, then one continuous contribution landscape. Project panels and the extra footer are no longer displayed or regenerated.

The graph groups listed daily contributions by calendar month. Each month has one crystal whose height uses a shared linear scale. Rainbow color follows the timeline. The last month is partial through the stated refresh date. Desktop and mobile use separate layouts of the same data.

## Contribution sources

`data/contributions.json` preserves the owner-supplied archive: 1,658 unique dated records totaling 6,715, June 1, 2018 through May 31, 2026. Its last listed date is May 28, 2026. It was imported from `Old Contribution.numbers`; provenance and a source fingerprint are stored with the daily counts. Missing archive dates remain unlisted, not confirmed zero. These historical counts are supplied by the owner, not an independently verified GitHub account merge.

`scripts/update_profile.py` appends the `acesava` GitHub contribution calendar starting June 1, 2026, after the archive's stated coverage ends. No overlapping date is counted twice. All subsequent dates, including known zeros, must be returned by GitHub before the display is updated. The daily query is split into windows of at most 365 days. `data/combined-contributions.json` records the exact combined snapshot and source subtotals used to draw the graph.

This custom image does not alter GitHub's native contribution graph. The daily refresh uses the local date in America/Los_Angeles; today's contributions may still change.

## Refreshing

The **Refresh profile instruments** workflow runs daily and can be dispatched manually. It uses the repository's built-in GitHub token, refreshes public profile information and recent contribution counts, and commits the resulting SVGs and combined snapshot. The source archive is never rewritten. Failed queries or invalid daily data leave the committed profile visible. GitHub image caching can delay refreshed graphics.

Render with an authenticated GitHub CLI:

```sh
GH_TOKEN="$(gh auth token)" python3 scripts/update_profile.py
```

Offline rendering uses `profile.json` and a saved `recent-contributions.json` GraphQL response. Set its matching coverage date:

```sh
python3 scripts/update_profile.py --input-dir /path/to/metadata --as-of 2026-10-01
```

`scripts/render_landscape.py` verifies totals, unique dates, nonnegative integer counts, and coverage before rendering. Daily records remain embedded under their monthly groups for reconciliation. The legend identifies the aggregation as listed monthly contributions.

Custom styles remain inside the images and do not change GitHub's surrounding layout or theme. The operator cursor honors reduced-motion preferences.
