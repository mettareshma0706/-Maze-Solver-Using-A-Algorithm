/**
 * A* Maze Solver — game.js
 * Full 20-level neon maze game with A* pathfinding
 * Heuristic: Manhattan Distance
 */

"use strict";

// ─────────────────────────────────────────────
//  COLORS
// ─────────────────────────────────────────────
console.log("JS LOADED");
const C = {
  bg:        "#03030a",
  wall:      "#0a0a19",
  wallGlow:  "#1e3c78",
  open:      "#0c0c1c",
  start:     "#00ff64",
  startBg:   "#002810",
  end:       "#ff3250",
  endBg:     "#280a10",
  path:      "#fff000",
  pathBg:    "#282000",
  visited:   "#143050",
  player:    "#00fff0",
  playerCore:"#dce6ff",
  panelBord: "#2850a0",
};

// ─────────────────────────────────────────────
//  MAZE LEVEL DATA (levels 1-3 hand-crafted)
// ─────────────────────────────────────────────
const LEVEL1 = {
  grid:[
    [1,1,1,1,1,1,1,1,1],
    [1,0,0,0,1,0,0,0,1],
    [1,0,1,0,1,0,1,0,1],
    [1,0,1,0,0,0,1,0,1],
    [1,0,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,1],
    [1,1,1,0,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1],
  ], start:[1,1], end:[7,7]
};

const LEVEL2 = {
  grid:[
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
  ], start:[1,1], end:[9,9]
};

const LEVEL3 = {
  grid:[
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
  ], start:[1,1], end:[11,11]
};

// ─────────────────────────────────────────────
//  MAZE GENERATOR (recursive backtracking)
// ─────────────────────────────────────────────
function generateMaze(rows, cols, complexity) {
  const grid = Array.from({length: rows}, () => Array(cols).fill(1));

  function carve(r, c) {
    const dirs = [[0,2],[0,-2],[2,0],[-2,0]].sort(() => Math.random()-0.5);
    for (const [dr,dc] of dirs) {
      const nr = r+dr, nc = c+dc;
      if (nr>0 && nr<rows-1 && nc>0 && nc<cols-1 && grid[nr][nc]===1) {
        grid[r+Math.floor(dr/2)][c+Math.floor(dc/2)] = 0;
        grid[nr][nc] = 0;
        carve(nr, nc);
      }
    }
  }

  grid[1][1] = 0;
  carve(1, 1);
  grid[rows-2][cols-2] = 0;
  grid[rows-2][cols-3] = 0;
  grid[rows-3][cols-2] = 0;

  // Extra openings for complexity
  const extra = Math.floor(rows * cols * complexity * 0.05);
  for (let i = 0; i < extra; i++) {
    const r = 1 + Math.floor(Math.random()*(rows-2));
    const c = 1 + Math.floor(Math.random()*(cols-2));
    grid[r][c] = 0;
  }
  return grid;
}

// ─────────────────────────────────────────────
//  BUILD ALL 20 LEVELS
// ─────────────────────────────────────────────
function buildLevels() {
  const levels = [LEVEL1, LEVEL2, LEVEL3];
  const sizes = [
    [13,13],[15,15],[15,15],[17,17],[17,17],
    [19,19],[19,19],[21,21],[21,21],[23,23],
    [23,23],[25,25],[25,25],[27,27],[27,27],[29,29],[29,29]
  ];
  sizes.forEach(([r,c], i) => {
    const g = generateMaze(r, c, 0.3 + i*0.04);
    levels.push({ grid:g, start:[1,1], end:[r-2, c-2] });
  });
  return levels;
}

// ─────────────────────────────────────────────
//  A* ALGORITHM — Manhattan Distance heuristic
// ─────────────────────────────────────────────
function astar(grid, start, end) {
  const rows = grid.length, cols = grid[0].length;
  const key  = (r,c) => r*1000+c;
  const heur = (a,b) => Math.abs(a[0]-b[0]) + Math.abs(a[1]-b[1]);

  // Min-heap via sorted array (small mazes fine; for large we use a simple heap)
  class MinHeap {
    constructor() { this.h = []; }
    push(item) {
      this.h.push(item);
      this.h.sort((a,b) => a.f - b.f);  // simple sort-based heap
    }
    pop() { return this.h.shift(); }
    get size() { return this.h.length; }
  }

  const heap    = new MinHeap();
  const gScore  = new Map();
  const cameFrom= new Map();
  const closed  = new Set();
  const visited = [];

  gScore.set(key(...start), 0);
  heap.push({ f: heur(start,end), g:0, r:start[0], c:start[1], parent:null });

  while (heap.size > 0) {
    const { g, r, c, parent } = heap.pop();
    const k = key(r,c);

    if (closed.has(k)) continue;
    closed.add(k);
    cameFrom.set(k, parent);
    visited.push([r,c]);

    if (r===end[0] && c===end[1]) {
      // Reconstruct path
      const path = [];
      let cur = k;
      while (cur !== null) {
        const cr = Math.floor(cur/1000), cc = cur%1000;
        path.unshift([cr,cc]);
        cur = cameFrom.get(cur);
      }
      return { path, visited };
    }

    for (const [dr,dc] of [[-1,0],[1,0],[0,-1],[0,1]]) {
      const nr=r+dr, nc=c+dc;
      if (nr>=0 && nr<rows && nc>=0 && nc<cols && grid[nr][nc]===0) {
        const nk = key(nr,nc);
        if (!closed.has(nk)) {
          const ng = g+1;
          if (ng < (gScore.get(nk) ?? Infinity)) {
            gScore.set(nk, ng);
            heap.push({ f: ng+heur([nr,nc],end), g:ng, r:nr, c:nc, parent:k });
          }
        }
      }
    }
  }
  return { path:[], visited };
}

// ─────────────────────────────────────────────
//  PARTICLE SYSTEM
// ─────────────────────────────────────────────
class Particle {
  constructor(x, y, color) {
    this.x = x; this.y = y;
    this.vx = (Math.random()-0.5)*4;
    this.vy = -(0.5 + Math.random()*3);
    this.life = 30 + Math.random()*40;
    this.maxLife = this.life;
    this.color = color;
    this.r = 2 + Math.random()*4;
  }
  update() { this.x+=this.vx; this.y+=this.vy; this.vy+=0.07; this.life--; }
  draw(ctx) {
    const a = this.life/this.maxLife;
    ctx.globalAlpha = a;
    ctx.fillStyle = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r, 0, Math.PI*2);
    ctx.fill();
    ctx.globalAlpha = 1;
  }
  get alive() { return this.life > 0; }
}

// ─────────────────────────────────────────────
//  GAME ENGINE
// ─────────────────────────────────────────────
class MazeGame {
  constructor() {
    // DOM
    this.screens = {
      start: document.getElementById("screen-start"),
      game:  document.getElementById("screen-game"),
      win:   document.getElementById("screen-win"),
    };
    this.mazeCanvas = document.getElementById("maze-canvas");
    this.ctx        = this.mazeCanvas.getContext("2d");
    this.bgCanvas   = document.getElementById("bg-canvas");
    this.bgCtx      = this.bgCanvas.getContext("2d");
    this.winCanvas  = document.getElementById("win-canvas");
    this.winCtx     = this.winCanvas.getContext("2d");

    // UI labels
    this.lblLevel = document.getElementById("lbl-level");
    this.lblTime  = document.getElementById("lbl-time");
    this.lblScore = document.getElementById("lbl-score");
    this.lblGrid  = document.getElementById("lbl-grid");
    this.statusMsg= document.getElementById("status-msg");
    this.winScore = document.getElementById("win-score");

    // Buttons
    document.getElementById("btn-play")   .onclick = () => this.startGame();
    document.getElementById("btn-solve")  .onclick = () => this.startSolve();
    document.getElementById("btn-reset")  .onclick = () => this.resetLevel();
    document.getElementById("btn-next")   .onclick = () => this.nextLevel();
    document.getElementById("btn-menu")   .onclick = () => this.showScreen("start");
    document.getElementById("btn-restart").onclick = () => this.restartAll();
    document.getElementById("btn-win-menu").onclick= () => this.showScreen("start");

    // Keyboard
    window.addEventListener("keydown", e => this.onKey(e));

    // State
    this.levels     = buildLevels();
    this.levelIdx   = 0;
    this.totalScore = 0;
    this.particles  = [];
    this.state      = "start"; // start | game | solve | done | win
    this.t          = 0;
    this.raf        = null;

    // Solve animation
    this.solveVisited = [];
    this.solvePath    = [];
    this.animVIdx     = 0;
    this.animPIdx     = 0;
    this.visitedDone  = false;
    this.visitedSet   = new Set();
    this.pathSet      = new Set();
    this.animDelay    = 2;
    this.animTick     = 0;

    // Resize
    window.addEventListener("resize", () => this.onResize());
    this.onResize();

    this.showScreen("start");
    requestAnimationFrame(ts => this.loop(ts));
  }

  // ── Screen management ──────────────────────
  showScreen(name) {
    Object.values(this.screens).forEach(s => s.classList.remove("active"));
    this.screens[name].classList.add("active");
    this.state = name === "game" ? "game" : name;
  }

  startGame() {
    this.totalScore = 0;
    this.levelIdx   = 0;
    this.showScreen("game");
    // Delay so the screen is visible and wrap has real dimensions
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        this.loadLevel(0);
      });
    });
  }

  restartAll() {
    this.startGame();
  }

  // ── Level management ───────────────────────
  loadLevel(idx) {
    this.levelIdx = idx;
    const lvl     = this.levels[idx];
    this.grid     = lvl.grid;
    this.rows     = this.grid.length;
    this.cols     = this.grid[0].length;
    this.startPos = [...lvl.start];
    this.endPos   = [...lvl.end];
    this.playerPos= [...lvl.start];

    this.solveVisited= [];
    this.solvePath   = [];
    this.animVIdx    = 0;
    this.animPIdx    = 0;
    this.visitedDone = false;
    this.visitedSet  = new Set();
    this.pathSet     = new Set();
    this.animDelay   = Math.max(1, 4 - Math.floor(idx/5));
    this.animTick    = 0;
    this.state       = "game";

    this.timerStart  = performance.now();
    this.levelTime   = 0;

    // Update panel labels
    this.lblLevel.textContent = String(idx+1).padStart(2,"0");
    this.lblGrid.textContent  = `${this.rows}×${this.cols}`;
    this.statusMsg.textContent = "";
    this.statusMsg.className   = "status-msg";
    document.getElementById("btn-solve").disabled = false;
    document.getElementById("btn-next") .disabled = true;

    this.computeCellSize();
  }

  resetLevel() {
    this.loadLevel(this.levelIdx);
  }

  nextLevel() {
    if (this.levelIdx+1 < this.levels.length) {
      this.showScreen("game");
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          this.loadLevel(this.levelIdx+1);
        });
      });
    } else {
      this.winScore.textContent = `TOTAL SCORE: ${this.totalScore}`;
      this.showScreen("win");
    }
  }

  // ── Cell geometry ──────────────────────────
  computeCellSize() {
    const wrap = document.getElementById("maze-wrap");
    const W    = (wrap.clientWidth  || window.innerWidth  * 0.75) - 20;
    const H    = (wrap.clientHeight || window.innerHeight) - 20;
    const cw   = Math.floor(W / this.cols);
    const ch   = Math.floor(H / this.rows);
    this.cell  = Math.min(cw, ch, 52);
    const tw   = this.cell * this.cols;
    const th   = this.cell * this.rows;
    this.mazeCanvas.width  = tw;
    this.mazeCanvas.height = th;
    this.ox = 0; this.oy = 0;  // canvas is centered via CSS flex
  }

  onResize() {
    // BG canvas
    this.bgCanvas.width  = window.innerWidth;
    this.bgCanvas.height = window.innerHeight;
    this.winCanvas.width  = window.innerWidth;
    this.winCanvas.height = window.innerHeight;
    if (this.grid) this.computeCellSize();
  }

  cellKey(r,c) { return r*1000+c; }

  // ── Solve trigger ──────────────────────────
  startSolve() {
    if (this.state !== "game") return;
    const result = astar(this.grid, this.startPos, this.endPos);
    this.solveVisited = result.visited;
    this.solvePath    = result.path;
    this.animVIdx     = 0;
    this.animPIdx     = 0;
    this.visitedDone  = false;
    this.visitedSet   = new Set();
    this.pathSet      = new Set();
    this.state        = "solve";
    document.getElementById("btn-solve").disabled = true;
    this.statusMsg.textContent = "SOLVING...";
    this.statusMsg.style.color = "#00fff0";
    this.statusMsg.style.textShadow = "0 0 8px #00fff0";
  }

  // ── Keyboard input ─────────────────────────
  onKey(e) {
    if (this.state !== "game") return;
    const moves = {
      ArrowUp:[-1,0], ArrowDown:[1,0], ArrowLeft:[0,-1], ArrowRight:[0,1],
      w:[-1,0], s:[1,0], a:[0,-1], d:[0,1],
      W:[-1,0], S:[1,0], A:[0,-1], D:[0,1],
    };
    if (!moves[e.key]) return;
    e.preventDefault();
    const [dr,dc] = moves[e.key];
    const nr = this.playerPos[0]+dr, nc = this.playerPos[1]+dc;
    if (nr>=0 && nr<this.rows && nc>=0 && nc<this.cols && this.grid[nr][nc]===0) {
      this.playerPos = [nr,nc];
      // Particles
      const {x,y} = this.cellCenter(nr,nc);
      for (let i=0;i<6;i++) this.particles.push(new Particle(x,y,"#00fff0"));
      // Win check
      if (nr===this.endPos[0] && nc===this.endPos[1]) this.levelComplete();
    }
  }

  cellCenter(r,c) {
    return {
      x: this.mazeCanvas.offsetLeft + c*this.cell + this.cell/2,
      y: this.mazeCanvas.offsetTop  + r*this.cell + this.cell/2,
    };
  }

  // ── Level complete ─────────────────────────
  levelComplete() {
    this.levelTime  = (performance.now() - this.timerStart) / 1000;
    const lvlScore  = Math.max(100, 1000 - Math.floor(this.levelTime*10));
    this.totalScore+= lvlScore;
    this.state      = "done";
    this.statusMsg.textContent = "✓ SOLVED!";
    this.statusMsg.style.color = "#00ff64";
    this.statusMsg.style.textShadow = "0 0 10px #00ff64";
    document.getElementById("btn-next").disabled = false;
    document.getElementById("btn-solve").disabled= true;
    this.lblScore.textContent = this.totalScore;
    // Particles burst at end cell
    const {x,y} = this.cellCenter(...this.endPos);
    const cols = ["#fff000","#00fff0","#00ff64","#ff32c8"];
    for (let i=0;i<60;i++) this.particles.push(new Particle(x,y, cols[i%4]));
  }

  // ── Main loop ──────────────────────────────
  loop(ts) {
    this.t = ts / 1000;
    this.update(ts);
    this.draw(ts);
    requestAnimationFrame(t => this.loop(t));
  }

  update(ts) {
    // Particles
    this.particles = this.particles.filter(p => p.alive);
    this.particles.forEach(p => p.update());

    // Timer
    if (this.state === "game") {
      const elapsed = (ts - this.timerStart) / 1000;
      const m = Math.floor(elapsed/60), s = Math.floor(elapsed%60);
      this.lblTime.textContent = `${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
    }

    // Solve animation
    if (this.state === "solve") {
      this.animTick++;
      if (this.animTick >= this.animDelay) {
        this.animTick = 0;
        if (!this.visitedDone) {
          if (this.animVIdx < this.solveVisited.length) {
            const [r,c] = this.solveVisited[this.animVIdx++];
            const k = this.cellKey(r,c);
            if (!(r===this.startPos[0]&&c===this.startPos[1]) &&
                !(r===this.endPos[0]  &&c===this.endPos[1])) {
              this.visitedSet.add(k);
            }
          } else {
            this.visitedDone = true;
            this.visitedSet.clear();
          }
        } else {
          if (this.animPIdx < this.solvePath.length) {
            const [r,c] = this.solvePath[this.animPIdx++];
            this.pathSet.add(this.cellKey(r,c));
            const {x,y} = this.cellCenter(r,c);
            if (Math.random()<0.4) this.particles.push(new Particle(x,y,"#fff000"));
          } else {
            this.levelComplete();
          }
        }
      }
    }
  }

  // ── Drawing ────────────────────────────────
  draw(ts) {
    if (this.state === "start" || this.state === "start-screen") {
      this.drawBg(this.bgCtx, this.bgCanvas.width, this.bgCanvas.height);
      return;
    }
    if (this.state === "win") {
      this.drawWinBg();
      return;
    }
    if (this.grid) this.drawMaze(ts);
  }

  // Animated grid background for start/win
  drawBg(ctx, W, H) {
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle = "#05050f";
    ctx.fillRect(0,0,W,H);
    const step = 40;
    for (let y=0; y<H; y+=step) {
      const a = 0.05 + 0.04*Math.sin(this.t + y*0.05);
      ctx.strokeStyle = `rgba(0,${Math.floor(a*500)},${Math.floor(a*1000)},${a})`;
      ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke();
    }
    for (let x=0; x<W; x+=step) {
      const a = 0.05 + 0.04*Math.sin(this.t*0.7 + x*0.05);
      ctx.strokeStyle = `rgba(0,${Math.floor(a*500)},${Math.floor(a*1000)},${a})`;
      ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke();
    }
  }

  drawWinBg() {
    const ctx = this.winCtx, W = this.winCanvas.width, H = this.winCanvas.height;
    ctx.fillStyle = "rgba(5,5,15,0.3)";
    ctx.fillRect(0,0,W,H);
    for (let i=0;i<3;i++) {
      const x = Math.random()*W, y = Math.random()*H;
      const col = ["#fff000","#00fff0","#00ff64"][i];
      this.particles.push(new Particle(x,y,col));
    }
    this.particles.forEach(p => p.draw(ctx));
  }

  roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x+r, y);
    ctx.lineTo(x+w-r, y);
    ctx.quadraticCurveTo(x+w, y, x+w, y+r);
    ctx.lineTo(x+w, y+h-r);
    ctx.quadraticCurveTo(x+w, y+h, x+w-r, y+h);
    ctx.lineTo(x+r, y+h);
    ctx.quadraticCurveTo(x, y+h, x, y+h-r);
    ctx.lineTo(x, y+r);
    ctx.quadraticCurveTo(x, y, x+r, y);
    ctx.closePath();
  }

  drawMaze(ts) {
    const ctx  = this.ctx;
    const cs   = this.cell;
    const W    = this.mazeCanvas.width;
    const H    = this.mazeCanvas.height;
    const rad  = Math.max(2, cs * 0.18);

    // Background
    ctx.fillStyle = "#03030a";
    ctx.fillRect(0,0,W,H);

    // Subtle grid lines on floor
    ctx.strokeStyle = "rgba(20,30,60,0.6)";
    ctx.lineWidth = 0.5;
    for (let r=0; r<this.rows; r++) {
      for (let c=0; c<this.cols; c++) {
        if (this.grid[r][c] === 0) {
          ctx.strokeRect(c*cs, r*cs, cs, cs);
        }
      }
    }

    // Draw cells
    for (let r=0; r<this.rows; r++) {
      for (let c=0; c<this.cols; c++) {
        const x = c*cs, y = r*cs;
        const k = this.cellKey(r,c);
        const isStart = r===this.startPos[0] && c===this.startPos[1];
        const isEnd   = r===this.endPos[0]   && c===this.endPos[1];

        if (this.grid[r][c] === 1) {
          // Wall — rich dark blue with inner glow edge
          const wallGrad = ctx.createLinearGradient(x, y, x+cs, y+cs);
          wallGrad.addColorStop(0, "#0d1230");
          wallGrad.addColorStop(1, "#060818");
          ctx.fillStyle = wallGrad;
          ctx.fillRect(x, y, cs, cs);

          // Bright neon top/left edges for 3D feel
          ctx.strokeStyle = "rgba(60,100,220,0.5)";
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.moveTo(x, y+cs); ctx.lineTo(x, y); ctx.lineTo(x+cs, y);
          ctx.stroke();

          // Darker bottom/right edges
          ctx.strokeStyle = "rgba(10,15,50,0.8)";
          ctx.beginPath();
          ctx.moveTo(x+cs, y); ctx.lineTo(x+cs, y+cs); ctx.lineTo(x, y+cs);
          ctx.stroke();

        } else if (isStart) {
          // Start cell — glowing green
          ctx.fillStyle = "#001a0a";
          ctx.fillRect(x, y, cs, cs);
          const pad = 3;
          ctx.shadowColor = C.start;
          ctx.shadowBlur  = 18;
          ctx.fillStyle   = "#003318";
          this.roundRect(ctx, x+pad, y+pad, cs-pad*2, cs-pad*2, rad);
          ctx.fill();
          ctx.strokeStyle = C.start;
          ctx.lineWidth   = 2;
          this.roundRect(ctx, x+pad, y+pad, cs-pad*2, cs-pad*2, rad);
          ctx.stroke();
          ctx.shadowBlur  = 0;

        } else if (isEnd) {
          // End cell — glowing red/pink
          ctx.fillStyle = "#1a0005";
          ctx.fillRect(x, y, cs, cs);
          const pad = 3;
          ctx.shadowColor = C.end;
          ctx.shadowBlur  = 20;
          ctx.fillStyle   = "#2d000a";
          this.roundRect(ctx, x+pad, y+pad, cs-pad*2, cs-pad*2, rad);
          ctx.fill();
          ctx.strokeStyle = C.end;
          ctx.lineWidth   = 2;
          this.roundRect(ctx, x+pad, y+pad, cs-pad*2, cs-pad*2, rad);
          ctx.stroke();
          ctx.shadowBlur  = 0;

        } else if (this.pathSet.has(k)) {
          // Path — bright neon yellow trail
          ctx.fillStyle = "#1a1600";
          ctx.fillRect(x, y, cs, cs);
          const pad = Math.floor(cs / 3);
          const pathGrad = ctx.createRadialGradient(x+cs/2,y+cs/2,0,x+cs/2,y+cs/2,cs/2);
          pathGrad.addColorStop(0, "#ffff44");
          pathGrad.addColorStop(1, "#aa8800");
          ctx.fillStyle   = pathGrad;
          ctx.shadowColor = "#fff000";
          ctx.shadowBlur  = 14;
          this.roundRect(ctx, x+pad, y+pad, cs-pad*2, cs-pad*2, 3);
          ctx.fill();
          ctx.shadowBlur  = 0;

        } else if (this.visitedSet.has(k)) {
          // Visited — deep blue tint
          ctx.fillStyle = "#0a1828";
          ctx.fillRect(x, y, cs, cs);
          ctx.fillStyle = "rgba(20,60,100,0.5)";
          this.roundRect(ctx, x+2, y+2, cs-4, cs-4, 2);
          ctx.fill();

        } else {
          // Open floor — very dark with subtle texture
          ctx.fillStyle = "#080814";
          ctx.fillRect(x, y, cs, cs);
        }
      }
    }

    // S / E labels
    const fontSize = Math.max(10, Math.floor(cs * 0.42));
    ctx.textAlign    = "center";
    ctx.textBaseline = "middle";
    ctx.font         = `bold ${fontSize}px 'Orbitron', sans-serif`;

    ctx.fillStyle   = C.start;
    ctx.shadowColor = C.start; ctx.shadowBlur = 12;
    ctx.fillText("S", this.startPos[1]*cs+cs/2, this.startPos[0]*cs+cs/2);
    ctx.shadowBlur = 0;

    ctx.fillStyle   = C.end;
    ctx.shadowColor = C.end; ctx.shadowBlur = 12;
    ctx.fillText("E", this.endPos[1]*cs+cs/2, this.endPos[0]*cs+cs/2);
    ctx.shadowBlur = 0;

    // Player (manual)
    if (this.state === "game" || this.state === "done") {
      const [pr,pc] = this.playerPos;
      const px = pc*cs+cs/2, py = pr*cs+cs/2;
      const pulse  = 0.5 + 0.5*Math.sin(this.t*5);
      const radius = cs*0.32 + 2*pulse;

      // Outer soft glow
      const outerGrad = ctx.createRadialGradient(px,py,0,px,py,radius*3);
      outerGrad.addColorStop(0,"rgba(0,255,240,0.25)");
      outerGrad.addColorStop(1,"rgba(0,255,240,0)");
      ctx.fillStyle = outerGrad;
      ctx.beginPath(); ctx.arc(px,py,radius*3,0,Math.PI*2); ctx.fill();

      // Body glow
      ctx.shadowColor = "#00fff0";
      ctx.shadowBlur  = 18;
      const playerGrad = ctx.createRadialGradient(px-radius*0.2,py-radius*0.2,0,px,py,radius);
      playerGrad.addColorStop(0,"#aaffff");
      playerGrad.addColorStop(0.5,"#00fff0");
      playerGrad.addColorStop(1,"#0088aa");
      ctx.fillStyle   = playerGrad;
      ctx.beginPath(); ctx.arc(px,py,radius,0,Math.PI*2); ctx.fill();
      ctx.shadowBlur  = 0;

      // Bright core dot
      ctx.fillStyle = "#ffffff";
      ctx.beginPath(); ctx.arc(px,py,Math.max(2,radius*0.28),0,Math.PI*2); ctx.fill();
    }

    // Maze outer border with glow
    ctx.shadowColor = "#2850a0";
    ctx.shadowBlur  = 12;
    ctx.strokeStyle = "#3060c0";
    ctx.lineWidth   = 3;
    ctx.strokeRect(1,1,W-2,H-2);
    ctx.shadowBlur  = 0;
    ctx.strokeStyle = C.panelBord;
    ctx.lineWidth   = 2;
    ctx.strokeRect(1,1,W-2,H-2);

    // Draw particles on the canvas (offset-corrected)
    const wrapRect = document.getElementById("maze-wrap").getBoundingClientRect();
    const canRect  = this.mazeCanvas.getBoundingClientRect();
    const offX     = canRect.left - wrapRect.left;
    const offY     = canRect.top  - wrapRect.top;
    // We draw particles on the overlay (use absolute positions)
    // Particles already use absolute page coords, skip on maze canvas
  }
}

// ─────────────────────────────────────────────
//  BOOT
// ─────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  window._game = new MazeGame();
});