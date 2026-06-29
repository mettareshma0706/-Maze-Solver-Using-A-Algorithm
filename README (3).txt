# A* Maze Solver — 20 Levels

## FILES IN THIS FOLDER

| File               | What it is                              |
|--------------------|-----------------------------------------|
| maze_game.py       | ⭐ Python/Pygame desktop game           |
| index.html         | 🌐 Web version — open in browser        |
| style.css          | 🎨 Web version styles                   |
| game.js            | ⚙️  Web version JavaScript logic        |
| requirements.txt   | Python dependency (pygame)              |
| run_windows.bat    | Windows: double-click to install & run  |
| run_mac_linux.sh   | Mac/Linux: run in terminal              |

---

## HOW TO RUN — WEB VERSION (easiest, no install)
Just open index.html in any modern browser.
Chrome / Firefox / Edge all work.

---

## HOW TO RUN — PYTHON/PYGAME VERSION

### Windows
Double-click run_windows.bat

### Mac / Linux
  chmod +x run_mac_linux.sh
  ./run_mac_linux.sh

### Manual
  pip install pygame
  python maze_game.py

---

## CONTROLS
| Key              | Action                        |
|------------------|-------------------------------|
| Arrow Keys / WASD| Move player manually          |
| SOLVE button     | Watch A* find the path        |
| RESET            | Restart current level         |
| NEXT LEVEL       | Go to next (after solving)    |
| ESC              | Return to menu (Python ver.)  |

## HOW A* WORKS
1. Start from green cell
2. Uses Manhattan Distance heuristic: |Δrow| + |Δcol|
3. Blue cells = explored/visited by A*
4. Yellow cells = optimal shortest path
5. Score = max(100, 1000 - seconds × 10) per level
