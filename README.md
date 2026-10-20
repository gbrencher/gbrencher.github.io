# George (Quinn) Brencher's academic website

A buildless website prepared for GitHub Pages. The published files are in `dist/`.

## Editing

- `dist/index.html`: homepage, research, publications, teaching, portfolios, and press.
- `dist/style.css`: responsive sidebar layout and gallery styling.
- `dist/maps/`: map viewing pages.
- `dist/assets/maps/`: optimized WebP map exports.
- `dist/cv.html`: accessible HTML transcription of the CV.
- `dist/assets/George-Brencher-CV.docx`: original supplied CV download.
- `.github/workflows/pages.yml`: deploys `dist/` on pushes to `main`.

The homepage leads with Seattle terrain mapping. Cartography includes five optimized map images and individual detail pages in `dist/maps/`. Photography remains forthcoming. The supplied headshot appears in About. Original map PDFs remain outside the repository; embedded map credits are retained. Academic content comes from the CV supplied October 19, 2026; research summaries are draft prose for the author's review. Publication statuses and funding qualifications are retained in the online CV. The original CV download includes the contact information in the supplied document.

## Publishing

Push this directory to the intended GitHub repository with default branch `main`. In repository Settings → Pages, choose GitHub Actions as the publishing source. The included workflow deploys the site. A repository named `<username>.github.io` serves at the account's root Pages address; other repository names serve under a repository path. All local links use relative paths to support either configuration.

See https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages.

## Preview

Serve `dist/` with any static HTTP server, or open `dist/index.html` directly in a browser.

## Daily North Cascades snow map

`daily-snow.yml` runs at 15:37 UTC daily (08:37 PDT / 07:37 PST), on manual dispatch, and when its implementation changes on main. It targets six days earlier in Pacific time. This is a configurable starting lag, not a confirmed upstream availability guarantee. The default snow-off date is the most recent September 10 strictly before the target; validate this reference for the North Cascades before interpreting results.

Extent: -122.10, 48.25, -120.50, 49.00 (west, south, east, north). The fixed extent creates two upstream tiles. If the extent or tile size changes, also update BBOX and expected tile count in scripts/render_snow.py.

`snow-batch.yml` and `snow-tile.yml` are adapted copies of the supplied deep-snow workflows, pinned to bcc0f928f979af2b65f3bdc984cf2a563fea96fd. They retain the upstream prediction scripts and environment; explicit upstream checkouts allow execution from this repository. The upstream BSD license is retained in LICENSE-deep-snow. Two parallel jobs are allowed, with a 90-minute prediction timeout per tile.

The renderer reprojects both completed GeoTIFFs to a shared UTM zone 10 grid, preserves missing data, and produces latest.png and latest.json. The fixed 0–5 m color scale has an overflow indicator. The website loads only real successful outputs; until then, the Seattle cartography remains visible. No synthetic test output is published. Composite inputs do not all represent the displayed target date.

The daily job commits only the small display assets, while original GeoTIFFs remain workflow artifacts. A successful daily workflow triggers the existing Pages deployment using workflow_run because commits made with GITHUB_TOKEN do not trigger ordinary push workflows. Failed predictions do not overwrite the previous map. GitHub Pages must already be configured to use Actions, and repository policies must allow the daily job contents:write.

Manual first run: Actions → Daily North Cascades snow → Run workflow. Optionally supply a known usable target and snow-off date. Inspect the output before treating the reference date and data lag as established production settings.
