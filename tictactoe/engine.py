#!/usr/bin/env python3
"""Tic-Tac-Toe engine for the maddox095 profile README.

Visitors play as X by opening a GitHub Issue titled ``ttt|move|<cell>`` where
``cell`` is 0-8 (top-left to bottom-right). This script applies the move, lets an
optimal minimax bot respond as O, regenerates the README board + stats between the
``<!--START_SECTION:tictactoe-->`` / ``<!--END_SECTION:tictactoe-->`` markers, and
persists ``state.json``.

Run in CI via env vars (ISSUE_TITLE / ISSUE_ACTOR) or locally for testing:

    python tictactoe/engine.py "ttt|move|4" someuser
"""
import json
import os
import sys
import urllib.parse
from datetime import datetime, timezone

REPO = "maddox095/maddox095"
HERE = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(HERE, "state.json")
README_PATH = os.path.join(os.path.dirname(HERE), "README.md")
START = "<!--START_SECTION:tictactoe-->"
END = "<!--END_SECTION:tictactoe-->"

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
]


def new_board():
    return [" "] * 9


def default_state():
    return {
        "board": new_board(),
        "status": "playing",      # playing | won | draw
        "winner": None,           # "X" | "O" | None
        "games_played": 0,
        "human_wins": 0,
        "bot_wins": 0,
        "draws": 0,
        "last_player": None,
        "history": [],            # most-recent-first list of moves
        "hall_of_fame": [],       # users who drew or beat the bot
        "updated": None,
    }


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            state = json.load(f)
        for key, value in default_state().items():
            state.setdefault(key, value)
        return state
    return default_state()


def save_state(state):
    state["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def winner(board):
    for a, b, c in WIN_LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_full(board):
    return all(cell != " " for cell in board)


def minimax(board, player):
    """Return (score, move) with O maximizing and X minimizing.

    Scores are from O's perspective: +1 O win, -1 X win, 0 draw. Depth is folded
    in so the bot prefers the fastest win and the slowest loss.
    """
    win = winner(board)
    if win == "O":
        return 10 - board.count("O") - board.count("X"), None
    if win == "X":
        return -10 + board.count("O") + board.count("X"), None
    if is_full(board):
        return 0, None

    moves = [i for i in range(9) if board[i] == " "]
    best_move = moves[0]
    if player == "O":
        best = -99
        for m in moves:
            board[m] = "O"
            score, _ = minimax(board, "X")
            board[m] = " "
            if score > best:
                best, best_move = score, m
        return best, best_move
    else:
        best = 99
        for m in moves:
            board[m] = "X"
            score, _ = minimax(board, "O")
            board[m] = " "
            if score < best:
                best, best_move = score, m
        return best, best_move


def bot_move(board):
    _, move = minimax(board, "O")
    return move


# --------------------------------------------------------------------------- #
# README rendering
# --------------------------------------------------------------------------- #
def cell_link(index):
    body = ("Just press the green **Submit new issue** button below. My bot plays "
            "its move and the board on my profile updates in ~30 seconds. "
            "Thanks for playing!")
    query = urllib.parse.urlencode({"title": f"ttt|move|{index}", "body": body})
    return f"https://github.com/{REPO}/issues/new?{query}"


def render_board(state):
    board = state["board"]
    playable = state["status"] == "playing"

    def cell(index):
        mark = board[index]
        if mark == "X":
            return "❌"
        if mark == "O":
            return "⭕"
        if playable:
            return f"[⬜]({cell_link(index)})"
        return "⬜"

    rows = ["|  |  |  |", "|:-:|:-:|:-:|"]
    for r in range(3):
        rows.append("| " + " | ".join(cell(r * 3 + c) for c in range(3)) + " |")
    return "\n".join(rows)


def render_section(state):
    board = state["board"]
    status = state["status"]
    started = any(c != " " for c in board)

    if status == "playing":
        if started:
            turn = ("**Your move.** You're **❌**. Click any ⬜ to drop your mark; "
                    "the bot (**⭕**) answers instantly.")
        else:
            turn = ("**New game.** You're **❌**. Click any ⬜ to start. "
                    "Can you outsmart my unbeatable bot?")
    elif status == "won" and state["winner"] == "X":
        turn = "**A human beat the bot!** Click any ⬜ to start a fresh game."
    elif status == "won" and state["winner"] == "O":
        turn = "**Bot wins this round.** Click any ⬜ to start over and try again."
    else:
        turn = ("**Draw: the best possible result against the bot.** "
                "Click any ⬜ for a new game.")

    games = state["games_played"]
    human = state["human_wins"]
    bot = state["bot_wins"]
    draws = state["draws"]

    lines = [
        "## Beat My Tic-Tac-Toe Bot",
        "",
        "> You're **❌**, my bot is **⭕** and plays *optimally* (minimax). The best "
        "most humans manage is a draw. Click any square: a pre-filled GitHub Issue opens, "
        "just hit **Submit** and the board refreshes in ~30s.",
        "",
        render_board(state),
        "",
        turn,
        "",
        (f"![Games](https://img.shields.io/badge/Games-{games}-1f2328?style=flat-square&labelColor=161b22) "
         f"![Bot wins](https://img.shields.io/badge/Bot_wins-{bot}-da3633?style=flat-square&labelColor=161b22) "
         f"![Draws](https://img.shields.io/badge/Draws-{draws}-1f6feb?style=flat-square&labelColor=161b22) "
         f"![Humans who won](https://img.shields.io/badge/Humans_who_won-{human}-2ea043?style=flat-square&labelColor=161b22)"),
        "",
    ]

    if state["history"]:
        lines += ["<details><summary>Recent moves</summary>", ""]
        lines += ["| Player | Mark | Cell | When |", "|--------|:----:|:----:|------|"]
        for move in state["history"][:8]:
            by = move["by"]
            who = "TicTacToeBot" if by == "TicTacToeBot" else f"[@{by}](https://github.com/{by})"
            mark = "❌" if move["mark"] == "X" else "⭕"
            lines.append(f"| {who} | {mark} | {move['cell'] + 1} | {move.get('time', '')} |")
        lines += ["", "</details>", ""]

    if state["hall_of_fame"]:
        fame = ", ".join(f"[@{u}](https://github.com/{u})" for u in state["hall_of_fame"][:15])
        lines += [f"**Hall of Fame** (drew with or beat the bot): {fame}", ""]

    return "\n".join(lines)


def update_readme(section):
    if not os.path.exists(README_PATH):
        return False
    with open(README_PATH, encoding="utf-8") as f:
        content = f.read()
    if START not in content or END not in content:
        return False
    pre = content.split(START)[0]
    post = content.split(END)[1]
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(pre + START + "\n" + section + "\n" + END + post)
    return True


def write_output(key, value):
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"{key}={value.replace(chr(10), ' ')}\n")


def stamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def parse_cell(text):
    token = text.strip().split("|")[-1].strip()
    try:
        cell = int(token)
    except ValueError:
        return None
    return cell if 0 <= cell <= 8 else None


def main():
    raw = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("ISSUE_TITLE", "")
    actor = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("ISSUE_ACTOR", "someone")

    cell = parse_cell(raw)
    if cell is None:
        msg = f"Could not read a cell (0-8) from '{raw}'. Move ignored."
        print(msg)
        write_output("result", msg)
        return

    state = load_state()

    # Finished game? The next click begins a fresh board.
    if state["status"] != "playing":
        state["board"] = new_board()
        state["status"] = "playing"
        state["winner"] = None
        state["history"] = []

    board = state["board"]

    if board[cell] != " ":
        msg = f"Cell {cell + 1} is already taken, @{actor}. Pick an empty one!"
        update_readme(render_section(state))
        save_state(state)
        print(msg)
        write_output("result", msg)
        return

    # Human (X) move.
    board[cell] = "X"
    state["history"].insert(0, {"by": actor, "mark": "X", "cell": cell, "time": stamp()})

    if winner(board) == "X":
        state.update(status="won", winner="X")
        state["games_played"] += 1
        state["human_wins"] += 1
        if actor not in state["hall_of_fame"]:
            state["hall_of_fame"].insert(0, actor)
        msg = f"🎉 @{actor} BEAT the bot. Legendary! The board resets on the next move."
    elif is_full(board):
        state.update(status="draw")
        state["games_played"] += 1
        state["draws"] += 1
        if actor not in state["hall_of_fame"]:
            state["hall_of_fame"].insert(0, actor)
        msg = f"🤝 @{actor} forced a DRAW, the best most can hope for. Hall of Fame!"
    else:
        # Bot (O) responds.
        move = bot_move(board)
        board[move] = "O"
        state["history"].insert(0, {"by": "TicTacToeBot", "mark": "O", "cell": move, "time": stamp()})
        if winner(board) == "O":
            state.update(status="won", winner="O")
            state["games_played"] += 1
            state["bot_wins"] += 1
            msg = f"🤖 The bot wins this round. Thanks for playing, @{actor}! Board resets next move."
        elif is_full(board):
            state.update(status="draw")
            state["games_played"] += 1
            state["draws"] += 1
            if actor not in state["hall_of_fame"]:
                state["hall_of_fame"].insert(0, actor)
            msg = f"🤝 Draw! Nicely held, @{actor}. Welcome to the Hall of Fame."
        else:
            msg = f"@{actor} played cell {cell + 1}; the bot replied. Your move!"

    state["history"] = state["history"][:8]
    state["last_player"] = actor
    update_readme(render_section(state))
    save_state(state)
    print(msg)
    write_output("result", msg)


if __name__ == "__main__":
    main()
