# Tic-Tac-Toe (README game engine)

A playable Tic-Tac-Toe game that lives inside the profile `README.md`. Visitors
play as **X** against an optimal **O** bot. Every move runs entirely on GitHub
Actions using the built-in `GITHUB_TOKEN`, so there are no servers, secrets, or
external services involved.

## How it works

1. **A visitor clicks a square.** Each empty cell on the board is a link that
   opens a pre-filled GitHub Issue titled `ttt|move|<cell>` (cell is 0-8,
   top-left to bottom-right). The visitor just presses "Submit new issue".
2. **A workflow wakes up.** [`.github/workflows/tictactoe.yml`](../.github/workflows/tictactoe.yml)
   triggers on the new issue (only when the title starts with `ttt|move|`).
3. **The engine processes the move.** [`engine.py`](engine.py) places the X,
   then a [minimax](https://en.wikipedia.org/wiki/Minimax) search picks the
   optimal reply as O (it never loses).
4. **The board redraws.** The script rewrites the section between the
   `<!--START_SECTION:tictactoe-->` and `<!--END_SECTION:tictactoe-->` markers in
   the profile README, commits it, and closes the issue with the result. The
   whole round takes about 30 seconds.

When a game ends (win or draw) the next click starts a fresh board. A player who
forces a draw or beats the bot is added to the Hall of Fame.

## Files

| File | Purpose |
|------|---------|
| `engine.py` | Move parsing, minimax bot, board/stats rendering, README rewrite. |
| `state.json` | Persisted game state (see schema below). |
| `requirements.txt` | Documents that the engine has no third-party dependencies. |
| `../.github/workflows/tictactoe.yml` | The workflow that runs a move. |

## `state.json` schema

| Field | Type | Meaning |
|-------|------|---------|
| `board` | list[9] | Each cell is `" "`, `"X"`, or `"O"`. |
| `status` | string | `playing`, `won`, or `draw`. |
| `winner` | string/null | `"X"`, `"O"`, or `null`. |
| `games_played` | int | Completed games. |
| `human_wins` | int | Games a human won. |
| `bot_wins` | int | Games the bot won. |
| `draws` | int | Drawn games. |
| `last_player` | string/null | GitHub login of the last human to move. |
| `history` | list | Most-recent-first list of `{by, mark, cell, time}`. |
| `hall_of_fame` | list | Logins of players who drew with or beat the bot. |
| `updated` | string/null | UTC timestamp of the last update. |

## Run it locally

```bash
# Simulate a move at the center cell (4) as user "yourname".
# On Windows, prefix with PYTHONUTF8=1 so the console can print emoji.
python engine.py "ttt|move|4" yourname
```

This updates `state.json` and rewrites the board section of `../README.md`,
exactly as the workflow does.

## Reset the game

```bash
cd tictactoe
python -c "import engine; s = engine.default_state(); engine.save_state(s); engine.update_readme(engine.render_section(s))"
```

## Make the bot beatable (optional)

The bot is unbeatable by default. To give visitors a real chance to win, make it
play a random move some of the time by editing `bot_move` in `engine.py`:

```python
import random

def bot_move(board):
    empty = [i for i in range(9) if board[i] == " "]
    if random.random() < 0.2:          # 20% chance of a beatable, random move
        return random.choice(empty)
    _, move = minimax(board, "O")
    return move
```

## Requirements

- Python 3 (the workflow uses `actions/setup-python`).
- Repository Actions permission set to "Read and write" (see [../SETUP.md](../SETUP.md)).
