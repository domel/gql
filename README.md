# GQL Essentials

Dominik Tomaszuk

[Read the book](https://gql.fyi/) · [Download PDF](assets/gql-essentials.pdf) · [BibTeX](assets/book.bib)

Static HTML edition of *GQL Essentials*: 23 chapters, bibliography, illustrations, mathematical notation, a searchable index and publication details.

Open `index.html` to read the book locally. All required styles, scripts, images and search data are included in `assets`.

GitHub Pages publishes the repository root from the `main` branch. The `.nojekyll` file enables direct publication of the static files.

To update the website, replace the generated HTML files and assets, then push the changes to `main`.

SEO metadata, homepage introduction and six learning guides are maintained by `tools/seo.py`. After replacing generated HTML, run `python3 tools/seo.py` before publishing (requires `beautifulsoup4`). This applies titles, descriptions, canonical URLs, Open Graph metadata, Book JSON-LD, guide navigation and search entries, and rebuilds the sitemap. It leaves chapter content and PDF files unchanged.

The detailed contents page has its own canonical URL. Standalone footnotes use `noindex,follow` and are omitted from the sitemap, which contains 49 indexable URLs.

Rerunning the SEO script refreshes the homepage guide list and preserves each page's `robots`, `googlebot` and `bingbot` directives. Pages marked `noindex` or `none` are excluded from the sitemap. New guides do not inherit the homepage's indexing directives.

Run the regression checks with `python3 -m unittest discover -s tools -p 'test_seo.py'`.
