# Setup guide

One-time configuration to make this profile repo fully functional after you push
it to `github.com/maddox095/maddox095`. None of this requires secret tokens; the
automation runs on the built-in `GITHUB_TOKEN`.

## 1. Enable Actions write access (required)

The Tic-Tac-Toe and snake workflows commit back to the repo, so they need write
permission:

1. Go to repo **Settings -> Actions -> General**.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Click **Save**.

Without this, the game cannot update the board and the snake cannot publish.

## 2. Generate the contribution snake (one-time kick-off)

The snake images do not exist until the workflow runs once:

1. Go to the **Actions** tab.
2. Open the **generate-snake** workflow.
3. Click **Run workflow**.

This creates an `output` branch containing `snake.svg` and `snake-dark.svg`,
which the README references by raw URL. After this first run it also refreshes
automatically on every push to `main` and twice a day. Until it has run once, the
snake image in the README shows as broken, which is expected.

## 3. Tic-Tac-Toe game

Nothing extra to enable (Issues are on by default). Once step 1 is done:

- Visitors click a square on the board, which opens a pre-filled issue; they
  press Submit and the board updates in about 30 seconds.
- The board resets automatically after each finished game.
- Internals, local testing, and how to reset or tune the bot are documented in
  [tictactoe/README.md](tictactoe/README.md).

The [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml) keeps
blank issues enabled (required for the move links) and adds a friendly link on
the new-issue chooser page.

## 4. Widgets

All of these are third-party image widgets embedded by URL; no setup needed.
The **streak stats**, **contribution activity graph**, **typing header**, and
**dev quote** were all verified reachable.

Note: the `github-readme-stats` overall-stats and top-languages cards were
intentionally removed. The shared public instance is frequently rate-limited and
returns 503, which left the cards broken on the profile. If you ever want them
back with 100% reliability, deploy your own instance on Vercel (see
https://github.com/anuraghazra/github-readme-stats#deploy-on-your-own ) and add
the two image URLs to the GitHub Stats section of the README.

## 5. Repository structure

```
README.md                         Profile page (what shows on your GitHub profile)
SETUP.md                          This file
LICENSE                           MIT license
.gitignore                        Ignores __pycache__ and *.bak
.github/
  ISSUE_TEMPLATE/config.yml       Issue chooser config (keeps blank issues on)
  workflows/
    tictactoe.yml                 Runs a game move on issue open
    snake.yml                     Generates the contribution snake
tictactoe/
  engine.py                       Game engine (stdlib only)
  state.json                      Persisted game state
  requirements.txt                Dependency note (none)
  README.md                       Game internals and local testing
```
