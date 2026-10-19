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

`daily-snow.yml` runs at 15:23 UTC daily (08:23 PDT / 07:23 PST), or manually from Actions. It requests yesterday in America/Los_Angeles. The bbox is -121.85 48.35 -120.50 49.00 (Mount Baker and North Cascades National Park). The reference is September 10 of the most recent completed summer, switching in October. These are initial scientific configuration choices to review with the author.

`snow-batch.yml` and `snow-tile.yml` adapt geo-smart/deep-snow's batch_predict_sd and predict_tile_sd workflows at bcc0f928f979af2b65f3bdc984cf2a563fea96fd. Explicit upstream checkouts are necessary because a reusable workflow otherwise checks out the calling repository. Prediction uses composite acquisition selection, descending Sentinel-1, 25% cloud threshold, the single model, and no SWE. Update the checkout refs and renderer provenance together when updating the model code.

The renderer reprojects depth rasters (metres) to UTM zone 10N, retains nodata, requires 80% valid map coverage, and uses a fixed 0–5 m scale (values above 5 m share the endpoint color). No-data pixels are grey. Input-gap artifacts are retained in the workflow artifacts, not presented as uncertainty estimates. A requested prediction date is not an assertion of daily satellite observations.

On success, the bot commits the image and provenance JSON and explicitly dispatches pages.yml. GITHUB_TOKEN pushes alone do not trigger the Pages push workflow. No personal access token is required; the publish job requests contents:write and actions:write. Repository or organization policies and branch protection must allow this bot push and workflow dispatch. Failed prediction/rendering leaves the last map intact; the page marks updates older than two days. Before the first success, the homepage keeps the Seattle map.

After pushing, run **Daily North Cascades snow → Run workflow** once to populate the feature. Confirm the prediction and Pages runs pass. The full inference pipeline requires Linux and upstream model/data downloads and has not been executed locally on Windows. CI runtime and data latency need validation on the first real run.

Local renderer checks: install rasterio, numpy, matplotlib, then run `python scripts/test_snow.py`. Test data are synthetic and never copied to dist.
