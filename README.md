---
title: Diwan al-Wathaiq
emoji: 📜
colorFrom: green
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
short_description: Transcribe Maghrebi-script court deeds with Gemini
---

# Dīwān al-Wathāʾiq · ديوان الوثائق

This website transcribes handwritten Arabic court deeds in Maghrebi script from 18th- and 19th-century Algeria,
such as the ANOM fonds *1 MiOM 31*. Gemini makes the first transcription. An expert then corrects it line by line
and approves it, and every approved page becomes a new example for the next pages.
The interface is in Arabic, with a button to switch to English.

The code is on GitHub (`hchagroune/diwan-htr`). The site runs on Hugging Face (`hsmcgn19/diwan-htr`).
Every change pushed to GitHub is tested, then deployed automatically. That deploy step also creates the Space
and copies your keys into it.

---

## Setup: three keys in GitHub (about 5 minutes)

All settings go in one place: the GitHub repository → **Settings** → **Secrets and variables** → **Actions**.
Keys go only into GitHub's secret boxes, never into a chat or a file.

1. **Hugging Face token.** Go to <https://huggingface.co/settings/tokens> → **Create new token** → type **Write** →
   name it `github-deploy` → **Create**. Copy it.
2. **Add the secrets.** In the GitHub page above, open the **Secrets** tab and click **New repository secret**
   three times:

   | Name | Value |
   |---|---|
   | `HF_TOKEN` | the token from step 1 |
   | `GEMINI_API_KEY` | your key from <https://aistudio.google.com/apikey> |
   | `APP_PASSWORD` | a password you choose for the website. Share it with your expert. |

3. **Deploy.** Open **Actions** → **Deploy to Hugging Face** → **Run workflow**. In about 5 minutes the private Space
   `hsmcgn19/diwan-htr` is created, configured and running. Open it at <https://huggingface.co/spaces/hsmcgn19/diwan-htr>.

The website now works in *upload mode*: you drop scans and texts in the browser, and you download the results.

> **Upload mode keeps files only temporarily.** A free Space loses its disk when it restarts, and it goes to sleep
> after 48 hours without visits. Download your approved texts, or connect Google Drive below so that everything
> lives in your Drive.

## Optional: connect Google Drive (15 minutes, recommended)

With Drive connected:
- new scans are read from your *inbox* folder;
- approved `.txt` files are written to your *results* folder;
- the Library syncs from your training folder;
- the review queue is backed up to Drive, so nothing is lost when the Space restarts.

1. **Enable the Drive API.** Go to <https://console.cloud.google.com/>, create a project, then open
   **APIs & Services → Library → Google Drive API → Enable**.
2. **Set up the consent screen.** Open **APIs & Services → OAuth consent screen**, choose **External**, and fill in
   the app name and your email. Add yourself under **Test users**. Then click **Publish app**
   (status *In production*). If you skip publishing, Google cuts the access every 7 days. The *unverified app*
   warning you'll see later is normal for personal use.
3. **Create the OAuth client.** Open **Credentials → Create credentials → OAuth client ID** and choose
   type **Web application**. Under **Authorized redirect URIs** add `https://developers.google.com/oauthplayground`.
   Create it, then copy the **Client ID** and **Client secret**.
4. **Get a refresh token.** Open <https://developers.google.com/oauthplayground>:
   1. Click the gear icon (top right), tick **Use your own OAuth credentials**, and paste the Client ID and secret.
   2. In **Step 1**, type `https://www.googleapis.com/auth/drive`, then click **Authorize APIs**.
      Sign in, click *Advanced → Go to (app)*, then **Allow**.
   3. In **Step 2**, click **Exchange authorization code for tokens** and copy the **Refresh token**.
5. **Add it in GitHub** (Settings → Secrets and variables → Actions):

   | Tab | Name | Value |
   |---|---|---|
   | Secrets | `GOOGLE_CLIENT_ID` | from step 3 |
   | Secrets | `GOOGLE_CLIENT_SECRET` | from step 3 |
   | Secrets | `GOOGLE_REFRESH_TOKEN` | from step 4 |
   | Variables | `HTR_TRAIN_FOLDER` | `1KwJiFUvtqs75G3p7dfXddcUkdwEoZJvY` (the *1 MiOM 31* folder) |
   | Variables | `HTR_INBOX_FOLDER` | ID of a folder for new scans |
   | Variables | `HTR_OUTPUT_FOLDER` | ID of a folder for approved texts |

   A folder ID is the part of the Drive address after `/folders/`. You need **edit** rights on all three folders.
   If *1 MiOM 31* is only shared with you as a viewer, make a copy in your own Drive and use the copy's ID.
6. **Run the workflow again** (Actions → Deploy to Hugging Face → Run workflow). At start the website syncs the
   Library from Drive and looks for new scans in the inbox.

## Using the website

| Tab | What it does |
|---|---|
| **Pages** (الأوراق) | Drop scans (or a .zip), or click *Fetch new pages from Drive*. Then *Transcribe all new*. |
| **Review** (المراجعة) | Scan on one side, editable text on the other, one manuscript line per line. Lines the checker doubts are marked in red. *Approve* saves the .txt and adds the page to the Library. |
| **Library** (الخزانة) | Verified image + text pairs used as examples. Pages with two conflicting versions come first, for the expert to settle. |
| **Register** (السجل) | Correction rate over time, *Measure accuracy* on the test pages, transcription settings, and *Download all approved*. |

## Optional variables

| Variable (GitHub *Variables* tab) | Default | Meaning |
|---|---|---|
| `HTR_MODEL` | `gemini-3.1-pro-preview` | Gemini model for transcription. You can also change it in the Register tab. |
| `HTR_TRAIN_TEXT_FOLDER` | same as `HTR_TRAIN_FOLDER` | use when texts and images are in separate folders |

## Costs

- **Hugging Face:** the Space runs on free CPU.
- **Gemini:** billed per page by Google. One page with 3 examples, plus the checker, is a few image calls.
  To cut the cost, lower *Examples per page* or turn the checker off in the Register tab.

## For developers

```
server/main.py      FastAPI app: REST API, background worker, Drive backup of the queue
static/             website (index.html, style.css, app.js) — no build step
htr/                transcription pipeline (Gemini, Drive, few-shot retrieval, verifier, metrics)
config.space.yaml   default settings; secrets and folders come from the Space settings
tests/              API tests (run on every push before deploying)
.github/            deploy workflow: test → create/configure the Space → push the code
```

Run locally with `pip install -r requirements.txt` and `HTR_ENGINE=mock uvicorn server.main:app --port 7860`.
