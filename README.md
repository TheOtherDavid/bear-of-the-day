# bear-of-the-day

A little serverless app that generates an AI image of a bear every day, emails it
to a list of recipients, and keeps a browsable gallery of every bear ever made.
Because bears are cute.

It builds a prompt by randomly combining a subject, a scene, and two "spirits"
(moods) drawn from CSV word lists, calls OpenAI's image API, stores the result in
S3, and emails it out.

## How it works

The backend is an AWS SAM (CloudFormation) stack of Python 3.12 Lambda functions,
in `us-east-2`, wired together like this:

1. **Generator** (`bear_of_the_day.py`) — runs on a daily schedule (EventBridge,
   13:00 UTC). It composes a prompt from `subjects.csv`, `scenes.csv`, and
   `spirits.csv`, calls the OpenAI image API (currently the `gpt-image-2` model),
   saves the PNG to S3 with the prompt/subject/scene/spirits/model as object
   metadata, records the image in the manifest (see below), and publishes an SNS
   message.
2. **Emailer** (`send_bear_email.py`) — triggered by that SNS message. It pulls
   the latest image from S3, re-encodes it to a ~350 KB JPEG for a lightweight
   attachment (the S3 original PNG is left full-size), and sends it via Gmail SMTP.
3. **Gallery API** (API Gateway + Lambdas) for the frontend:
   - `GET /bear` (`get_latest_bear.py`) — the latest image (presigned URL + metadata).
   - `POST /morebears` (`get_bears_batch.py`) — a page of recent images.
   - `GET /manifest` (`get_manifest.py`) — the full image catalog for client-side filtering.
   - `POST /bearurls` (`bear_urls.py`) — presigned URLs for a set of image keys.
4. **Manifest** — `manifest.json` in the bucket lists every image with its
   attributes (`key`, `timestamp`, `subject`, `scene`, `spirits[]`, `model`,
   `prompt`). The generator appends to it on each run; `rebuild_manifest.py` is a
   manual-invoke Lambda that regenerates it from scratch by scanning the bucket
   (initial backfill and reconciler). It powers attribute-based filtering of the
   gallery.

Storage is a single S3 bucket (images + `manifest.json`). Shared helpers live in
`backend/common/` (`dalle.py`, `s3.py`, `send_email.py`, `manifest.py`, `config.py`).

## Frontend

A Vue.js app in `frontend/` displays the gallery. It reads the API endpoint URLs
from build-time environment variables (`VUE_APP_BACKEND_URL`, etc.). Run locally
with `npm run serve` from the `frontend/` directory.

## Data / customization

The image vocabulary is just CSV files in `backend/`: `subjects.csv`,
`scenes.csv`, `spirits.csv`, `styles.csv`. Edit those to change what the bears
look like. Removed entries stay searchable in the gallery because the manifest is
built from what's actually in the bucket, not from the current CSVs.

## Deployment

Deployed via GitHub Actions on push to `main` (`.github/workflows/build-deploy-lambda.yml`),
which runs `sam package` / `sam deploy` against the `BEAR-OF-THE-DAY` stack.

Configuration is supplied as CloudFormation parameters, sourced from GitHub
Actions secrets/variables:

- `OPENAI_API_KEY` — OpenAI API key (secret)
- `SENDER_EMAIL` / `SENDER_PASS` — Gmail account + app password for sending (secret)
- `RECIPIENTS` — comma-separated recipient list (variable)
- `AWS_BUCKET_NAME` — the image bucket (variable)

For local runs, the same values go in `backend/.env` (see `.env-example`);
`DEBUG_MODE=True` generates a blank image and sends only to `DEBUG_RECIPIENTS`.
