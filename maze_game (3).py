"""
A* Maze Game Solver - 20 Level Neon Maze Game
Uses A* (A-Star) Algorithm with Manhattan Distance heuristic
"""

import pygame
import sys
import heapq
import time
import math
import random

# ─────────────────────────────────────────────
#  CONSTANTS & COLORS
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 750
FPS = 60

# Neon color palette
BLACK       = (0, 0, 0)
BG_DARK     = (5, 5, 15)
WALL        = (10, 10, 25)
WALL_GLOW   = (30, 60, 120)
WHITE       = (220, 230, 255)
NEON_YELLOW = (255, 240, 0)
NEON_CYAN   = (0, 255, 240)
NEON_GREEN  = (0, 255, 100)
NEON_RED    = (255, 50, 80)
NEON_BLUE   = (50, 150, 255)
NEON_PINK   = (255, 50, 200)
NEON_ORANGE = (255, 140, 0)
PATH_COLOR  = (0, 200, 255)
PATH_GLOW   = (0, 80, 120)
VISITED_CLR = (20, 40, 80)
PANEL_BG    = (8, 8, 22)
PANEL_BORD  = (40, 80, 160)
GRAY        = (80, 90, 120)
DARK_GRAY   = (30, 35, 55)

# Game states
STATE_START  = "start"
STATE_GAME   = "game"
STATE_SOLVE  = "solve"
STATE_WIN    = "win"
STATE_DONE   = "done"   # level complete, show next button

# ─────────────────────────────────────────────
#  20 HAND-CRAFTED MAZE LEVELS
#  0 = open, 1 = wall, S = start, E = end
# ─────────────────────────────────────────────
def make_levels():
    levels = []

    # Level 1 – 9×9 trivial
    levels.append({
        "grid": [
            [1,1,1,1,1,1,1,1,1],
            [1,0,0,0,1,0,0,0,1],
            [1,0,1,0,1,0,1,0,1],
            [1,0,1,0,0,0,1,0,1],
            [1,0,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,1],
            [1,1,1,0,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1],
        ],
        "start": (1,1), "end": (7,7)
    })

    # Level 2 – 11×11
    levels.append({
        "grid": [
            [1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,1,0,0,0,1],
            [1,0,1,1,1,0,1,0,1,0,1],
            [1,0,1,0,0,0,1,0,1,0,1],
            [1,0,1,0,1,1,1,0,1,0,1],
            [1,0,0,0,1,0,0,0,1,0,1],
            [1,1,1,0,1,0,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1],
        ],
        "start": (1,1), "end": (9,9)
    })

    # Level 3 – 13×13
    levels.append({
        "grid": [
            [1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,1],
            [1,0,1,0,1,0,1,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,1,1,1,0,1,0,1],
            [1,0,0,0,0,0,0,0,1,0,1,0,1],
            [1,1,1,1,1,1,0,0,1,0,1,0,1],
            [1,0,0,0,0,1,0,1,1,0,1,0,1],
            [1,0,1,1,0,1,0,0,0,0,1,0,1],
            [1,0,1,0,0,1,1,1,1,1,1,0,1],
            [1,0,1,0,1,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,1,1,1,1,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "start": (1,1), "end": (11,11)
    })

    # Levels 4-20: procedurally generated with increasing complexity
    sizes = [
        (13,13),(15,15),(15,15),(17,17),(17,17),
        (19,19),(19,19),(21,21),(21,21),(23,23),
        (23,23),(25,25),(25,25),(27,27),(27,27),(29,29),(29,29)
    ]
    for i, (rows, cols) in enumerate(sizes):
        grid = generate_maze(rows, cols, complexity=0.3 + i*0.04)
        levels.append({
            "grid": grid,
            "start": (1, 1),
            "end": (rows-2, cols-2)
        })

    return levels


def generate_maze(rows, cols, complexity=0.5):
    """Generate a random maze using recursive backtracking."""
    grid = [[1]*cols for _ in range(rows)]
    
    def carve(r, c):
        dirs = [(0,2),(0,-2),(2,0),(-2,0)]
        random.shuffle(dirs)
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            if 0 < nr < rows-1 and 0 < nc < cols-1 and grid[nr][nc] == 1:
                grid[r+dr//2][c+dc//2] = 0
                grid[nr][nc] = 0
                carve(nr, nc)

    grid[1][1] = 0
    sys.setrecursionlimit(10000)
    carve(1, 1)
    
    # Ensure end is reachable
    grid[rows-2][cols-2] = 0
    grid[rows-2][cols-3] = 0
    grid[rows-3][cols-2] = 0
    
    # Add extra openings proportional to complexity
    extra = int(rows * cols * complexity * 0.05)
    for _ in range(extra):
        r = random.randrange(1, rows-1)
        c = random.randrange(1, cols-1)
        grid[r][c] = 0

    return grid


# ─────────────────────────────────────────────
#  A* PATHFINDING ALGORITHM
# ─────────────────────────────────────────────
def astar(grid, start, end):
    """
    A* algorithm using Manhattan Distance heuristic.
    Returns (path, visited_order) where path is list of (r,c) tuples.
    visited_order is the exploration order for animation.
    """
    rows = len(grid)
    cols = len(grid[0])

    def heuristic(a, b):
        # Manhattan Distance
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Priority queue: (f_score, g_score, node, parent)
    open_heap = []
    heapq.heappush(open_heap, (heuristic(start, end), 0, start, None))

    came_from = {}      # node -> parent
    g_score = {start: 0}
    closed_set = set()
    visited_order = []

    while open_heap:
        f, g, current, parent = heapq.heappop(open_heap)

        if current in closed_set:
            continue

        came_from[current] = parent
        closed_set.add(current)
        visited_order.append(current)

        if current == end:
            # Reconstruct path
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return path, visited_order

        r, c = current
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                neighbor = (nr, nc)
                if neighbor not in closed_set:
                    new_g = g + 1
                    if new_g < g_score.get(neighbor, float('inf')):
                        g_score[neighbor] = new_g
                        f_new = new_g + heuristic(neighbor, end)
                        heapq.heappush(open_heap, (f_new, new_g, neighbor, current))

    return [], visited_order  # No path found


# ─────────────────────────────────────────────
#  DRAWING HELPERS
# ─────────────────────────────────────────────
def draw_glow_rect(surf, color, rect, radius=4, glow_radius=8, alpha=80):
    """Draw a rectangle with a glow effect."""
    glow_surf = pygame.Surface((rect[2]+glow_radius*2, rect[3]+glow_radius*2), pygame.SRCALPHA)
    glow_color = (*color, alpha)
    pygame.draw.rect(glow_surf, glow_color,
                     (glow_radius, glow_radius, rect[2], rect[3]), border_radius=radius+2)
    surf.blit(glow_surf, (rect[0]-glow_radius, rect[1]-glow_radius))
    pygame.draw.rect(surf, color, rect, border_radius=radius)


def draw_text_glow(surf, text, font, color, pos, glow_color=None, glow_dist=2, center=True):
    """Render text with optional glow halo."""
    if glow_color:
        for dx in range(-glow_dist, glow_dist+1):
            for dy in range(-glow_dist, glow_dist+1):
                if dx == 0 and dy == 0:
                    continue
                gsurf = font.render(text, True, glow_color)
                if center:
                    r = gsurf.get_rect(center=(pos[0]+dx, pos[1]+dy))
                else:
                    r = gsurf.get_rect(topleft=(pos[0]+dx, pos[1]+dy))
                surf.blit(gsurf, r)
    tsurf = font.render(text, True, color)
    if center:
        r = tsurf.get_rect(center=pos)
    else:
        r = tsurf.get_rect(topleft=pos)
    surf.blit(tsurf, r)


def draw_neon_button(surf, rect, text, font, active=True, hovered=False):
    """Draw a neon-styled button."""
    color = NEON_CYAN if active else GRAY
    bg    = (0, 30, 50) if (active and hovered) else PANEL_BG
    border_col = color if active else DARK_GRAY

    pygame.draw.rect(surf, bg, rect, border_radius=8)
    pygame.draw.rect(surf, border_col, rect, 2, border_radius=8)

    if active and hovered:
        draw_glow_rect(surf, color, rect, radius=8, glow_radius=6, alpha=50)

    txt_col = color if active else GRAY
    glow = (0, 200, 200) if (active and hovered) else None
    draw_text_glow(surf, text, font, txt_col,
                   (rect[0]+rect[2]//2, rect[1]+rect[3]//2),
                   glow_color=glow, glow_dist=2)


# ─────────────────────────────────────────────
#  PARTICLE SYSTEM
# ─────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -0.5)
        self.life = random.randint(30, 60)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05
        self.life -= 1

    def draw(self, surf):
        alpha = int(255 * self.life / self.max_life)
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surf.blit(s, (int(self.x)-self.size, int(self.y)-self.size))

    def alive(self):
        return self.life > 0


# ─────────────────────────────────────────────
#  MAIN GAME CLASS
# ─────────────────────────────────────────────
class MazeGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("★ A* MAZE SOLVER ★  |  20 Levels")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock  = pygame.time.Clock()

        # Fonts
        self.font_huge  = pygame.font.SysFont("consolas", 72, bold=True)
        self.font_large = pygame.font.SysFont("consolas", 36, bold=True)
        self.font_med   = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 18)

        self.levels     = make_levels()
        self.level_idx  = 0
        self.state      = STATE_START
        self.particles  = []

        # Score & timer
        self.score      = 0
        self.level_time = 0.0
        self.timer_start= 0.0
        self.total_score= 0

        # Solve animation
        self.solve_visited  = []  # visited cells to animate
        self.solve_path     = []  # final path cells
        self.anim_visited_i = 0
        self.anim_path_i    = 0
        self.anim_visited_done = False
        self.anim_delay     = 0   # ticks between frames
        self.anim_tick      = 0

        # Player manual movement
        self.player_pos = None

        # Hover tracking for buttons
        self.mouse_pos = (0, 0)

        # Pulse animation time
        self.t = 0.0

        self._load_level(0)

    # ── Level loading ───────────────────────────
    def _load_level(self, idx):
        self.level_idx  = idx
        lvl             = self.levels[idx]
        self.grid       = lvl["grid"]
        self.rows       = len(self.grid)
        self.cols       = len(self.grid[0])
        self.start      = lvl["start"]
        self.end        = lvl["end"]
        self.player_pos = list(self.start)

        # Reset solve state
        self.solve_visited  = []
        self.solve_path     = []
        self.anim_visited_i = 0
        self.anim_path_i    = 0
        self.anim_visited_done = False
        self.anim_tick      = 0

        # Speed: faster on higher levels
        self.anim_delay = max(1, 4 - idx // 5)

        # Compute maze drawing area (left 3/4 of screen)
        self.maze_area_w = int(SCREEN_W * 0.75)
        self.maze_area_h = SCREEN_H
        self.panel_x     = self.maze_area_w
        self.panel_w     = SCREEN_W - self.maze_area_w

        # Cell size to fit maze in 3/4 area with padding
        pad = 20
        cell_w = (self.maze_area_w - pad*2) // self.cols
        cell_h = (self.maze_area_h - pad*2) // self.rows
        self.cell = min(cell_w, cell_h, 35)

        # Center the maze
        total_w = self.cell * self.cols
        total_h = self.cell * self.rows
        self.maze_ox = (self.maze_area_w - total_w) // 2
        self.maze_oy = (SCREEN_H - total_h) // 2

        self.visited_set = set()
        self.path_set    = set()

        # Timer
        self.timer_start = time.time()
        self.level_time  = 0.0

    # ── Coordinate helpers ───────────────────────
    def cell_rect(self, r, c):
        x = self.maze_ox + c * self.cell
        y = self.maze_oy + r * self.cell
        return pygame.Rect(x, y, self.cell, self.cell)

    def cell_center(self, r, c):
        rect = self.cell_rect(r, c)
        return rect.centerx, rect.centery

    # ── Solve trigger ────────────────────────────
    def _start_solve(self):
        path, visited = astar(self.grid, tuple(self.start), tuple(self.end))
        self.solve_visited      = visited
        self.solve_path         = path
        self.anim_visited_i     = 0
        self.anim_path_i        = 0
        self.anim_visited_done  = False
        self.visited_set        = set()
        self.path_set           = set()
        self.state              = STATE_SOLVE

    # ── Main loop ────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.t += dt
            self.mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                self._handle_event(event)

            self._update()
            self._draw()
            pygame.display.flip()

    # ── Event handling ───────────────────────────
    def _handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = STATE_START

        if self.state == STATE_START:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._btn_rect("play").collidepoint(event.pos):
                    self.state = STATE_GAME
                    self._load_level(0)

        elif self.state == STATE_GAME:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._btn_rect("solve").collidepoint(event.pos):
                    self._start_solve()
                elif self._btn_rect("reset").collidepoint(event.pos):
                    self._load_level(self.level_idx)
                elif self._btn_rect("menu").collidepoint(event.pos):
                    self.state = STATE_START

            # Manual player movement (arrow keys)
            if event.type == pygame.KEYDOWN:
                r, c = self.player_pos
                moves = {pygame.K_UP:(-1,0), pygame.K_DOWN:(1,0),
                         pygame.K_LEFT:(0,-1), pygame.K_RIGHT:(0,1),
                         pygame.K_w:(-1,0), pygame.K_s:(1,0),
                         pygame.K_a:(0,-1), pygame.K_d:(0,1)}
                if event.key in moves:
                    dr, dc = moves[event.key]
                    nr, nc = r+dr, c+dc
                    if (0 <= nr < self.rows and 0 <= nc < self.cols
                            and self.grid[nr][nc] == 0):
                        self.player_pos = [nr, nc]
                        # Spawn particles
                        cx, cy = self.cell_center(nr, nc)
                        for _ in range(5):
                            self.particles.append(Particle(cx, cy, NEON_CYAN))
                        # Check win
                        if [nr, nc] == list(self.end):
                            self._level_complete()

        elif self.state == STATE_SOLVE:
            # No input during solve animation
            pass

        elif self.state == STATE_DONE:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._btn_rect("next").collidepoint(event.pos):
                    if self.level_idx + 1 < len(self.levels):
                        self.state = STATE_GAME
                        self._load_level(self.level_idx + 1)
                    else:
                        self.state = STATE_WIN
                elif self._btn_rect("reset").collidepoint(event.pos):
                    self.state = STATE_GAME
                    self._load_level(self.level_idx)
                elif self._btn_rect("menu").collidepoint(event.pos):
                    self.state = STATE_START

        elif self.state == STATE_WIN:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._btn_rect("restart").collidepoint(event.pos):
                    self.total_score = 0
                    self.state = STATE_GAME
                    self._load_level(0)
                elif self._btn_rect("menu").collidepoint(event.pos):
                    self.state = STATE_START

    # ── Update logic ─────────────────────────────
    def _update(self):
        # Update particles
        self.particles = [p for p in self.particles if p.alive()]
        for p in self.particles:
            p.update()

        if self.state == STATE_GAME:
            self.level_time = time.time() - self.timer_start

        elif self.state == STATE_SOLVE:
            self.anim_tick += 1
            if self.anim_tick >= self.anim_delay:
                self.anim_tick = 0

                if not self.anim_visited_done:
                    # Animate visited cells
                    if self.anim_visited_i < len(self.solve_visited):
                        cell = self.solve_visited[self.anim_visited_i]
                        if cell != self.start and cell != self.end:
                            self.visited_set.add(cell)
                        self.anim_visited_i += 1
                    else:
                        self.anim_visited_done = True
                        self.visited_set.clear()
                else:
                    # Animate path
                    if self.anim_path_i < len(self.solve_path):
                        cell = self.solve_path[self.anim_path_i]
                        self.path_set.add(cell)
                        # Particles on path reveal
                        cx, cy = self.cell_center(*cell)
                        if random.random() < 0.4:
                            self.particles.append(Particle(cx, cy, NEON_YELLOW))
                        self.anim_path_i += 1
                    else:
                        # Done solving
                        self._level_complete()

    def _level_complete(self):
        self.level_time = time.time() - self.timer_start
        # Score: base 1000, minus 1 per second, minimum 100
        lvl_score = max(100, 1000 - int(self.level_time * 10))
        self.total_score += lvl_score
        # Celebration particles
        ex, ey = self.cell_center(*self.end)
        for _ in range(60):
            col = random.choice([NEON_YELLOW, NEON_CYAN, NEON_GREEN, NEON_PINK])
            self.particles.append(Particle(ex, ey, col))
        self.state = STATE_DONE

    # ── Button rectangles ────────────────────────
    def _btn_rect(self, name):
        px = self.panel_x + 10
        pw = self.panel_w - 20
        bh = 44
        by = {
            "solve":   560,
            "reset":   615,
            "next":    560,
            "menu":    670,
            "play":    (SCREEN_H//2 + 40),
            "restart": (SCREEN_H//2 + 130),
        }
        y = by.get(name, 600)
        return pygame.Rect(px, y, pw, bh)

    # ── Drawing ──────────────────────────────────
    def _draw(self):
        self.screen.fill(BG_DARK)

        if self.state == STATE_START:
            self._draw_start_screen()
        elif self.state == STATE_WIN:
            self._draw_win_screen()
        else:
            self._draw_maze()
            self._draw_panel()
            for p in self.particles:
                p.draw(self.screen)

    # ── Start screen ─────────────────────────────
    def _draw_start_screen(self):
        # Animated grid background
        for r in range(0, SCREEN_H, 40):
            alpha = int(30 + 15*math.sin(self.t + r*0.05))
            pygame.draw.line(self.screen, (0, alpha, alpha*2), (0, r), (SCREEN_W, r))
        for c in range(0, SCREEN_W, 40):
            alpha = int(30 + 15*math.sin(self.t*0.7 + c*0.05))
            pygame.draw.line(self.screen, (0, alpha, alpha*2), (c, 0), (c, SCREEN_H))

        # Title
        pulse = 0.5 + 0.5*math.sin(self.t * 2)
        col = (
            int(200 + 55*pulse),
            int(220 + 35*pulse),
            0
        )
        draw_text_glow(self.screen, "A★  MAZE  SOLVER",
                       self.font_huge, col,
                       (SCREEN_W//2, SCREEN_H//2 - 120),
                       glow_color=(80, 80, 0), glow_dist=4)

        draw_text_glow(self.screen, "20 LEVELS  ·  A* PATHFINDING  ·  NEON EDITION",
                       self.font_small, NEON_CYAN,
                       (SCREEN_W//2, SCREEN_H//2 - 50),
                       glow_color=(0, 80, 80), glow_dist=2)

        draw_text_glow(self.screen, "Arrow Keys / WASD  to move manually",
                       self.font_small, GRAY,
                       (SCREEN_W//2, SCREEN_H//2 + 5))

        draw_text_glow(self.screen, "Press SOLVE for A* auto-solve",
                       self.font_small, GRAY,
                       (SCREEN_W//2, SCREEN_H//2 + 30))

        # Play button
        br = self._btn_rect("play")
        hov = br.collidepoint(self.mouse_pos)
        draw_neon_button(self.screen, br, "▶  PLAY", self.font_large, active=True, hovered=hov)

        # Footer
        draw_text_glow(self.screen, "ESC = Menu  |  Press SOLVE to watch A* in action",
                       self.font_small, DARK_GRAY,
                       (SCREEN_W//2, SCREEN_H - 30))

    # ── Win screen ───────────────────────────────
    def _draw_win_screen(self):
        for _ in range(3):
            x = random.randint(0, SCREEN_W)
            y = random.randint(0, SCREEN_H)
            col = random.choice([NEON_YELLOW, NEON_CYAN, NEON_GREEN])
            self.particles.append(Particle(x, y, col))
        for p in self.particles:
            p.update()
            p.draw(self.screen)

        draw_text_glow(self.screen, "YOU WIN!", self.font_huge,
                       NEON_YELLOW, (SCREEN_W//2, SCREEN_H//2 - 150),
                       glow_color=(100,100,0), glow_dist=5)

        draw_text_glow(self.screen, "ALL 20 LEVELS COMPLETE",
                       self.font_large, NEON_CYAN,
                       (SCREEN_W//2, SCREEN_H//2 - 70))

        draw_text_glow(self.screen, f"TOTAL SCORE: {self.total_score}",
                       self.font_large, NEON_GREEN,
                       (SCREEN_W//2, SCREEN_H//2))

        br = self._btn_rect("restart")
        hov = br.collidepoint(self.mouse_pos)
        draw_neon_button(self.screen, br, "↺  PLAY AGAIN", self.font_med, active=True, hovered=hov)

        bm = self._btn_rect("menu")
        hov2 = bm.collidepoint(self.mouse_pos)
        bm2 = pygame.Rect(SCREEN_W//2 - 110, SCREEN_H//2 + 130, 220, 44)
        draw_neon_button(self.screen, bm2, "⌂  MENU", self.font_med, active=True, hovered=hov2)

    # ── Maze drawing ─────────────────────────────
    def _draw_maze(self):
        # Maze background
        pygame.draw.rect(self.screen, (3, 3, 10),
                         (0, 0, self.maze_area_w, SCREEN_H))

        for r in range(self.rows):
            for c in range(self.cols):
                rect = self.cell_rect(r, c)
                pos  = (r, c)
                cell_val = self.grid[r][c]

                if cell_val == 1:
                    # Wall with subtle glow
                    pygame.draw.rect(self.screen, WALL, rect)
                    # Inner bright border
                    pygame.draw.rect(self.screen, WALL_GLOW, rect, 1)
                else:
                    # Open cell
                    if pos == tuple(self.start):
                        col = NEON_GREEN
                        pygame.draw.rect(self.screen, (0, 40, 20), rect)
                        draw_glow_rect(self.screen, col, rect, radius=2, glow_radius=4, alpha=120)
                        pygame.draw.rect(self.screen, col, rect, 2)
                    elif pos == tuple(self.end):
                        col = NEON_RED
                        pygame.draw.rect(self.screen, (40, 10, 10), rect)
                        draw_glow_rect(self.screen, col, rect, radius=2, glow_radius=4, alpha=120)
                        pygame.draw.rect(self.screen, col, rect, 2)
                    elif pos in self.path_set:
                        # Solved path – neon yellow
                        pygame.draw.rect(self.screen, (40, 35, 0), rect)
                        draw_glow_rect(self.screen, NEON_YELLOW, rect, radius=0, glow_radius=3, alpha=80)
                        pygame.draw.rect(self.screen, NEON_YELLOW, rect.inflate(-self.cell//3, -self.cell//3))
                    elif pos in self.visited_set:
                        # A* exploration – dark blue
                        pygame.draw.rect(self.screen, VISITED_CLR, rect)
                    else:
                        pygame.draw.rect(self.screen, (12, 12, 28), rect)

        # Draw player
        if self.state in (STATE_GAME, STATE_DONE):
            pr, pc = self.player_pos
            cx, cy = self.cell_center(pr, pc)
            pulse  = 0.5 + 0.5*math.sin(self.t * 4)
            radius = int(self.cell * 0.35 + 2*pulse)
            # Glow
            gs = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (0, 200, 255, 60), (radius*2, radius*2), radius*2)
            self.screen.blit(gs, (cx-radius*2, cy-radius*2))
            # Body
            pygame.draw.circle(self.screen, NEON_CYAN, (cx, cy), radius)
            pygame.draw.circle(self.screen, WHITE, (cx, cy), max(2, radius//3))

        # Start/End labels
        sr, sc = self.start
        er, ec = self.end
        sx, sy = self.cell_center(sr, sc)
        ex, ey = self.cell_center(er, ec)
        draw_text_glow(self.screen, "S", self.font_small, NEON_GREEN,
                       (sx, sy), glow_color=(0,80,30), glow_dist=1)
        draw_text_glow(self.screen, "E", self.font_small, NEON_RED,
                       (ex, ey), glow_color=(80,0,20), glow_dist=1)

        # Maze border glow
        mw = self.cols * self.cell
        mh = self.rows * self.cell
        border_rect = pygame.Rect(self.maze_ox-2, self.maze_oy-2, mw+4, mh+4)
        pygame.draw.rect(self.screen, PANEL_BORD, border_rect, 2, border_radius=4)

    # ── Side panel ───────────────────────────────
    def _draw_panel(self):
        px = self.panel_x
        pw = self.panel_w

        # Panel background
        panel_surf = pygame.Surface((pw, SCREEN_H), pygame.SRCALPHA)
        panel_surf.fill((8, 8, 22, 220))
        self.screen.blit(panel_surf, (px, 0))
        pygame.draw.line(self.screen, PANEL_BORD, (px, 0), (px, SCREEN_H), 2)

        cx = px + pw // 2

        # Level number
        draw_text_glow(self.screen, f"LEVEL", self.font_small, GRAY, (cx, 35))
        draw_text_glow(self.screen, f"{self.level_idx+1:02d}",
                       self.font_huge, NEON_YELLOW, (cx, 95),
                       glow_color=(80,80,0), glow_dist=4)
        draw_text_glow(self.screen, f"/ 20", self.font_small, GRAY, (cx, 145))

        # Divider
        pygame.draw.line(self.screen, PANEL_BORD, (px+15, 165), (px+pw-15, 165), 1)

        # Timer
        elapsed = self.level_time if self.state in (STATE_DONE,) else time.time()-self.timer_start
        mins = int(elapsed) // 60
        secs = int(elapsed) % 60
        draw_text_glow(self.screen, "TIME", self.font_small, GRAY, (cx, 200))
        draw_text_glow(self.screen, f"{mins:02d}:{secs:02d}",
                       self.font_large, NEON_CYAN, (cx, 235))

        # Score
        pygame.draw.line(self.screen, PANEL_BORD, (px+15, 270), (px+pw-15, 270), 1)
        draw_text_glow(self.screen, "SCORE", self.font_small, GRAY, (cx, 295))
        draw_text_glow(self.screen, f"{self.total_score}", self.font_large, NEON_GREEN, (cx, 330))

        # Maze info
        pygame.draw.line(self.screen, PANEL_BORD, (px+15, 360), (px+pw-15, 360), 1)
        draw_text_glow(self.screen, f"GRID", self.font_small, GRAY, (cx, 385))
        draw_text_glow(self.screen, f"{self.rows}×{self.cols}", self.font_med, WHITE, (cx, 410))

        # A* legend
        draw_text_glow(self.screen, "A* LEGEND", self.font_small, GRAY, (cx, 445))
        legend_items = [
            (NEON_GREEN, "Start"),
            (NEON_RED,   "End"),
            (NEON_YELLOW,"Path"),
            (VISITED_CLR,"Explored"),
        ]
        for i, (col, label) in enumerate(legend_items):
            lx = px + 18
            ly = 465 + i * 22
            pygame.draw.rect(self.screen, col, (lx, ly, 14, 14))
            draw_text_glow(self.screen, label, self.font_small, GRAY,
                           (lx + 80, ly + 7))

        # Status message
        pygame.draw.line(self.screen, PANEL_BORD, (px+15, 545), (px+pw-15, 545), 1)

        if self.state == STATE_SOLVE:
            pulse = 0.5 + 0.5*math.sin(self.t * 5)
            col = (int(0+255*pulse), int(200+55*pulse), 0)
            draw_text_glow(self.screen, "SOLVING...", self.font_med, col, (cx, 550))

        elif self.state == STATE_DONE:
            draw_text_glow(self.screen, "✓ SOLVED!", self.font_med, NEON_GREEN,
                           (cx, 550), glow_color=(0,80,0), glow_dist=2)

        # Buttons
        if self.state == STATE_GAME:
            sr = self._btn_rect("solve")
            draw_neon_button(self.screen, sr, "▷  SOLVE (A*)", self.font_med,
                             active=True, hovered=sr.collidepoint(self.mouse_pos))
            rr = self._btn_rect("reset")
            draw_neon_button(self.screen, rr, "↺  RESET", self.font_med,
                             active=True, hovered=rr.collidepoint(self.mouse_pos))
            mr = self._btn_rect("menu")
            draw_neon_button(self.screen, mr, "⌂  MENU", self.font_med,
                             active=True, hovered=mr.collidepoint(self.mouse_pos))

        elif self.state == STATE_DONE:
            has_next = self.level_idx + 1 < len(self.levels)
            nr = self._btn_rect("next")
            draw_neon_button(self.screen, nr, "→  NEXT LEVEL", self.font_med,
                             active=has_next, hovered=nr.collidepoint(self.mouse_pos))
            rr = self._btn_rect("reset")
            draw_neon_button(self.screen, rr, "↺  RETRY", self.font_med,
                             active=True, hovered=rr.collidepoint(self.mouse_pos))
            mr = self._btn_rect("menu")
            draw_neon_button(self.screen, mr, "⌂  MENU", self.font_med,
                             active=True, hovered=mr.collidepoint(self.mouse_pos))

        elif self.state == STATE_SOLVE:
            # Greyed out during solve
            draw_neon_button(self.screen, self._btn_rect("solve"), "SOLVING...",
                             self.font_med, active=False)

        # Controls hint at bottom
        pygame.draw.line(self.screen, PANEL_BORD, (px+15, SCREEN_H-70), (px+pw-15, SCREEN_H-70), 1)
        draw_text_glow(self.screen, "WASD / ↑↓←→", self.font_small, DARK_GRAY, (cx, SCREEN_H-50))
        draw_text_glow(self.screen, "Manual movement", self.font_small, DARK_GRAY, (cx, SCREEN_H-28))


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    game = MazeGame()
    game.run()
