# Multiplayer Minesweeper (Python Final Version)

This project is a **turn-based multiplayer Minesweeper server** implemented in Python using **TCP sockets** and **threading**. Players connect to the server, take turns uncovering tiles on a shared Minesweeper board, and the game ends when a player steps on a mine or all safe tiles are discovered.

---

## Gameplay Overview

- Players take turns uncovering cells on a shared game board.
- The first player chooses the difficulty and generates the board.
- Each player selects a character (e.g., `A`, `B`, `C`) that marks their moves on the board.
- The server manages:
  - Turn order
  - Game state (board and moves)
  - Win/loss conditions
  - Broadcasting updates to all players

---

## Game Rules

- Cells can be:
  - `0`: empty
  - `1`: mine
  - `2`: discovered
- The game ends when:
  - A mine is uncovered → loss
  - All safe cells are discovered → win

---

## Difficulty Levels

| Difficulty   | Board Size | Mines |
|--------------|------------|-------|
| Principiante | 9 x 9      | 10    |
| Avanzado     | 16 x 16    | 40    |
| Prueba       | 3 x 3      | 4     |

---

## How It Works

### Server Responsibilities

- Accepts TCP connections from players.
- Uses a **barrier** to wait until all players are connected before starting the game.
- Assigns turn order using **semaphores**.
- Manages game state and communication using threads.
- Sends real-time updates to all players after each move.

### Communication

- Each move is sent in the format: `(xx,yy)`
- Server responds with a code:

| Code | Meaning                           |
|------|-----------------------------------|
| `0`  | It's your turn                    |
| `1`  | You won!                          |
| `2`  | Valid move                        |
| `3`  | Invalid coordinates               |
| `4`  | Mine hit — game over              |
| `5`  | Cell already selected             |

```bash
python servidor.py <host> <port> <num_players>
python cliente.py
