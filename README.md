# George Brencher's academic website

A buildless website prepared for GitHub Pages. The published files are in `dist/`.

## Editing

- `dist/index.html`: homepage, research, publications, teaching, portfolios, and press.
- `dist/cv.html`: accessible HTML transcription of the CV.
- `dist/assets/George-Brencher-CV.docx`: original supplied CV download.
- `.github/workflows/pages.yml`: deploys `dist/` on pushes to `main`.

The two portfolio sections remain placeholders pending original images. The homepage uses the supplied headshot and lakeside portrait. Academic content comes from the CV supplied October 19, 2026; research summaries are draft prose for the author's review. Publication statuses and funding qualifications are retained in the online CV. The original CV download includes the contact information in the supplied document.

## Publishing

Push this directory to the intended GitHub repository with default branch `main`. In repository Settings → Pages, choose GitHub Actions as the publishing source. The included workflow deploys the site. A repository named `<username>.github.io` serves at the account's root Pages address; other repository names serve under a repository path. All local links use relative paths to support either configuration.

See https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages.

## Preview

Serve `dist/` with any static HTTP server, or open `dist/index.html` directly in a browser.
