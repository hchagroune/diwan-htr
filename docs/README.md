# The public website of Dīwān al-Wathāʼiq

This folder is the public home page of the project. It is plain HTML and CSS: no server, no build step, no keys.
It lives on the branch `website`, so changes here never start the Hugging Face deploy of the branch `main`.

Address once published: <https://hchagroune.github.io/diwan-htr/>

## Switch it on (once, about 5 minutes)

1. **Add the two pictures.** Download `diwan-site-scan-0188.jpg` and `diwan-site-og-card.jpg` from the Google Drive
   folder "1 MiOM 31-20261113T172917Z-1-001". On GitHub, switch to the branch **website**, open `docs/assets/img`,
   click **Add file** → **Upload files**, drop the two files and click **Commit changes**.
2. **Switch on Pages.** Open **Settings** → **Pages**. Under **Build and deployment**, set **Source** to
   **Deploy from a branch**, choose the branch **website** and the folder **/docs**, then click **Save**.
3. Wait a minute or two, then open the address above.

## What is in it

| File | What it is |
| --- | --- |
| `index.html` | The home page: hero, how a page travels, the three rules, the archive, the experts section |
| `assets/site.css` | All the colours, fonts and layout (the "ink, paper and zellige" look) |
| `assets/favicon.svg` | The zellige star shown in the browser tab |
| `assets/img/diwan-site-scan-0188.jpg` | The scan of page 0188, 1006 × 1600 px |
| `assets/img/diwan-site-og-card.jpg` | The picture shown when someone shares the link, 1200 × 630 px |
| `404.html` | The page shown for a wrong address |

## Credits and contact

- Scan: Archives nationales d'outre-mer (France), fonds 1 MiOM 31, page 0188.
- Transcription of line 9: the project's expert transcription of page 0188.
- Contact shown on the page: chagroune.amc@gmail.com.
