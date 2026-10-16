# Publish this repository

The files in this folder are prepared for:
https://github.com/S-Bhim/customer-value-retention-analytics

## Use this clean folder

Extract the package into a fresh folder. Upload the contents of
`customer-value-retention-analytics` so README.md, docs/, src/ and the other
folders are at the repository root. Avoid combining it with the old
validation/schemas directory: its long filenames have been replaced here.
If Git is already initialized in your existing folder, preserve its .git
directory when applying your local changes. This package contains no Git history.

## Publish the files

Use GitHub Desktop's Add local repository / Publish repository workflow,
or Git from this folder. Review staged files before committing. This package
does not publish itself or configure a remote.

The .gitattributes file protects PDF/image/database bytes and normalizes text
to LF. The .gitignore file excludes environments, caches and local Power BI
settings. Schema filenames are short; core.longpaths is not needed for the
names in this package, although deeply nested extraction folders can still
cause Windows path limits. A short local path such as C:/Projects is useful.

## Enable the hosted dashboard

After committing and pushing the files:

1. Open your GitHub repository's Settings > Pages.
2. Under Build and deployment, choose Deploy from a branch.
3. Select the branch containing these files (normally main) and /docs.
4. Save, wait for deployment, and check the published site.

Dashboard URL:
https://s-bhim.github.io/customer-value-retention-analytics/

The dashboard entry file is already included at docs/index.html.
The folder is named docs, not docx. No backend, build command or API key is
required. The HTML contains the customer snapshot, so publishing the dashboard
also publishes its embedded data. Confirm that your assignment/dataset may be
redistributed before making the repository public; no dataset license was supplied.

Once the site loads, you can remove the README sentence explaining that the
hosted link becomes available after enabling Pages.

## Rebuild and validate

Install requirements.txt, then run:

    python run_project.py
    python validation/validate_project.py

Dashboard regeneration updates both dashboard/Founder_Dashboard.html and
docs/index.html, keeping the offline and hosted copies aligned.
The Power BI source still requires a Desktop open/refresh/visual check.

## Preparation changes

- Replaced README with the concise portfolio version and repository-specific links.
- Added docs/index.html and docs/.nojekyll for GitHub Pages.
- Added .gitattributes and .gitignore.
- Replaced long schema filenames with nine readable names plus a URL index.
- Updated the validator to load schemas through that index.
- Omitted the original assignment PDF containing personal contact details.
- Retained analysis, feature data, SQL, PDFs, Power BI source and validation records.
- No license or measured business impact has been invented.
