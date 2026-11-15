# The website of Dīwān al-Wathāʼiq

This folder is the website of the project. It is plain HTML, CSS and JavaScript: no server, no build step, no keys.
It lives on the branch `website`, so changes here never start the Hugging Face deploy of the branch `main`.

- Public home page: <https://hchagroune.github.io/diwan-htr/>
- Team board (needs the access code): <https://hchagroune.github.io/diwan-htr/board.html>

## Switch it on (once, about 5 minutes)

1. **Add the two pictures.** Download `diwan-site-scan-0188.jpg` and `diwan-site-og-card.jpg` from the Google Drive
   folder "1 MiOM 31-20261113T172917Z-1-001". On GitHub, switch to the branch **website**, open `docs/assets/img`,
   click **Add file** → **Upload files**, drop the two files and click **Commit changes**.
2. **Switch on Pages.** Open **Settings** → **Pages**. Under **Build and deployment**, set **Source** to
   **Deploy from a branch**, choose the branch **website** and the folder **/docs**, then click **Save**.
3. Wait a minute or two, then open the address above.

## The board (once, about 3 minutes)

The board shows where each page is: Inbox, Being read, With the expert, Approved, Needs attention.
It reads the n8n workflow **Diwan door: board**, which reads the n8n data table **Diwan pages**.
The main workflow writes one row per page into that table as the page moves.

To open the door:

1. In n8n, open the workflow **Diwan door: board** and double-click the step **Board door**.
2. Next to **Credential for Header Auth**, choose **Create new credential**.
   - **Name:** `X-Diwan-Code`
   - **Value:** an access code you choose (long and hard to guess, for example four random words).
   - Save the credential with the name **Diwan board code**.
3. Click **Publish** at the top right of the workflow.
4. Open the board address, type the same code and click **Open the board**.

The code is stored only in n8n and in the browsers where someone ticks "Remember on this device".
To change it, edit the credential in n8n: every board then asks for the new code.

Each click on **Refresh** runs the door once, so it counts as one n8n execution. The board never refreshes on its own.

## What is in it

| File | What it is |
| --- | --- |
| `index.html` | The home page: hero, how a page travels, the three rules, the archive, the experts section |
| `board.html` | The team board, behind the access code |
| `assets/site.css` | All the colours, fonts and layout (the "ink, paper and zellige" look) |
| `assets/board.css` | The layout of the board |
| `assets/board.js` | Asks n8n for the data and draws the cards |
| `assets/favicon.svg` | The zellige star shown in the browser tab |
| `assets/img/diwan-site-scan-0188.jpg` | The scan of page 0188, 1006 × 1600 px |
| `assets/img/diwan-site-og-card.jpg` | The picture shown when someone shares the link, 1200 × 630 px |
| `404.html` | The page shown for a wrong address |

## Credits and contact

- Scan: Archives nationales d'outre-mer (France), fonds 1 MiOM 31, page 0188.
- Transcription of line 9: the project's expert transcription of page 0188.
- Contact shown on the page: chagroune.amc@gmail.com.
