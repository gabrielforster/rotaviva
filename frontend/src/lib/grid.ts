import type { Cell, GridModel } from "@/types";

export function inBounds(g: GridModel, r: number, c: number): boolean {
  return r >= 0 && r < g.cells.length && c >= 0 && c < (g.cells[0]?.length ?? 0);
}

export function isFree(g: GridModel, r: number, c: number): boolean {
  return inBounds(g, r, c) && g.cells[r][c] === ".";
}

export function cellCenter(g: GridModel, cell: Cell): [number, number] {
  const s = g.cell_size;
  return [cell.col * s + s / 2, cell.row * s + s / 2];
}

const key = (r: number, c: number) => `${r},${c}`;

/**
 * Shortest 4-connected path between two free cells, inclusive of both ends, or
 * null if unreachable. Length matches the backend's matrix entry by construction
 * (both are BFS shortest paths on the same grid).
 */
export function bfsPath(g: GridModel, from: Cell, to: Cell): Cell[] | null {
  if (!isFree(g, from.row, from.col) || !isFree(g, to.row, to.col)) return null;
  const start = key(from.row, from.col);
  const goal = key(to.row, to.col);
  const prev = new Map<string, string | null>([[start, null]]);
  const queue: Cell[] = [from];
  while (queue.length) {
    const cur = queue.shift()!;
    if (key(cur.row, cur.col) === goal) break;
    const nbrs: Cell[] = [
      { row: cur.row - 1, col: cur.col },
      { row: cur.row + 1, col: cur.col },
      { row: cur.row, col: cur.col - 1 },
      { row: cur.row, col: cur.col + 1 },
    ];
    for (const nb of nbrs) {
      if (!isFree(g, nb.row, nb.col)) continue;
      const k = key(nb.row, nb.col);
      if (prev.has(k)) continue;
      prev.set(k, key(cur.row, cur.col));
      queue.push(nb);
    }
  }
  if (!prev.has(goal)) return null;
  const path: Cell[] = [];
  let cur: string | null = goal;
  while (cur) {
    const [r, c] = cur.split(",").map(Number);
    path.push({ row: r, col: c });
    cur = prev.get(cur) ?? null;
  }
  return path.reverse();
}
