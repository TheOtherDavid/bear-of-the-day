# bear-of-the-day-ui

The standalone Vue frontend for Bear of the Day. It can also be embedded by the
legacy `umbrella-portfolio-fe` during the migration period.

## Project setup

```bash
npm install
```

### Local development

The standalone page loads the portfolio navbar from a local shell server when
running on localhost. Start the shell first from the `portfolio-shell` directory:

```bash
py -m http.server 4173
```

Then, in this directory, run:

```bash
npm run serve
```

Open <http://localhost:8080/>. If the shell server is not running, the Bear UI
still works; only the optional navbar fails to load.

### Production build

```bash
npm run build
```

## Standalone deployment

Create a separate Vercel project for the repository with:

- **Root directory:** `frontend`
- **Build command:** `npm run build`
- **Output directory:** `dist`
- **Custom domain:** `bears.handcraftedai.com`

The backend remains independent: the SAM/CloudFormation deployment under
`backend/` continues to run through `.github/workflows/build-deploy-lambda.yml`.
The frontend deployment does not need AWS credentials.

The navbar is loaded at runtime by `public/portfolio-nav-loader.js`:

- localhost → `http://localhost:4173/nav.js`
- deployed frontend → `https://handcraftedai.com/nav.js`
- optional override → set `window.PORTFOLIO_NAV_URL` before the loader runs

The navbar host is in `public/index.html`, outside the Vue app root. This keeps
the old umbrella integration from receiving a duplicate navbar while the
migration is in progress.
