// The Keeping Oak: the OAK project mark, drawn with simulated dry media.
//
// One seeded oak geometry feeds every output: the 16:9 artwork, the
// medallion mark, the flat favicons, and the one-ink print mark.
// The module runs in a browser and in Node. Each render function takes
// makeCanvas(w, h), which returns a canvas with a 2D context.

// ---------------------------------------------------------------- utilities

export function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function makeNoise(seed) {
  const r = mulberry32(seed);
  const perm = [...Array(256).keys()];
  for (let i = 255; i > 0; i--) {
    const j = Math.floor(r() * (i + 1));
    [perm[i], perm[j]] = [perm[j], perm[i]];
  }
  const P = new Uint16Array(512);
  for (let i = 0; i < 512; i++) P[i] = perm[i & 255];
  const V = new Float32Array(256).map(() => r());
  function n2(x, y) {
    const xi = Math.floor(x), yi = Math.floor(y);
    const xf = x - xi, yf = y - yi;
    const X = xi & 255, Y = yi & 255;
    const a = V[P[P[X] + Y]], b = V[P[P[X + 1] + Y]];
    const c = V[P[P[X] + Y + 1]], d = V[P[P[X + 1] + Y + 1]];
    const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  }
  function fbm(x, y, oct = 4) {
    let s = 0, amp = 0.5, f = 1, norm = 0;
    for (let i = 0; i < oct; i++) {
      s += amp * n2(x * f + i * 17.3, y * f + i * 9.1);
      norm += amp; amp *= 0.5; f *= 2.03;
    }
    return s / norm;
  }
  return { n2, fbm };
}

const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const mix = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
const css = (c) => `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})`;
const clamp = (v, a = 0, b = 1) => (v < a ? a : v > b ? b : v);
const smooth = (a, b, v) => { const t = clamp((v - a) / (b - a)); return t * t * (3 - 2 * t); };
const lift = (c, k) => [c[0] * k, c[1] * k, c[2] * k];

function ramp(stops, t) {
  if (t <= stops[0][0]) return stops[0][1];
  for (let i = 1; i < stops.length; i++) {
    if (t <= stops[i][0]) {
      const [t0, c0] = stops[i - 1], [t1, c1] = stops[i];
      return mix(c0, c1, smooth(0, 1, (t - t0) / (t1 - t0)));
    }
  }
  return stops[stops.length - 1][1];
}

// Pigments. One box of sticks and pencils serves every output.
export const INK = {
  paper: hex('#2c2738'),
  woodDark: hex('#16131d'), woodMid: hex('#2a2230'), woodWarm: hex('#5e3d2c'),
  leafDeep: hex('#0e1217'), leafDark: hex('#141b20'), leafMid: hex('#1e292e'),
  leafOlive: hex('#2b3227'), leafCool: hex('#3a4562'),
  rimWarm: hex('#f6b25f'), rimHot: hex('#ffe4a8'), rimRose: hex('#e4866a'), rimCool: hex('#9590c4'),
  chalk: hex('#f4ead6'), earth: hex('#19141f'), night: hex('#0c0a12'),
};

// ------------------------------------------------------------ the studio
//
// A Studio owns the sheet of paper. Every layer of marks is drawn on a
// scratch canvas, then pressed into the paper tooth: pigment stays on the
// peaks of the grain, and harder pressure reaches into the valleys. The
// grain is the same sheet for every layer, as on real paper. A slow
// pressure field changes per layer, as a hand changes pressure.

export class Studio {
  constructor(makeCanvas, W, H, seed, opt = {}) {
    Object.assign(this, { W, H, mk: makeCanvas });
    this.canvas = makeCanvas(W, H); this.ctx = this.canvas.getContext('2d');
    this.lay = makeCanvas(W, H); this.lctx = this.lay.getContext('2d');
    this.msk = makeCanvas(W, H); this.mctx = this.msk.getContext('2d');
    this.r = mulberry32(seed);
    this.noise = makeNoise(seed * 7 + 3);
    this.grain = opt.grain ?? Math.max(1, Math.min(W, H) / 1300);
    this.clipFn = null;
    this.buildTooth();
    this.img = this.mctx.createImageData(W, H);
    this.img.data.fill(255);
  }

  buildTooth() {
    const { W, H } = this, n = this.noise.n2, g = this.grain;
    const N = W * H, T = new Float32Array(N);
    let sum = 0, sq = 0;
    for (let y = 0, i = 0; y < H; y++) {
      const Y = y / g;
      for (let x = 0; x < W; x++, i++) {
        const X = x / g;
        // fine tooth, mid tooth, and long paper fibres
        const v = 0.52 * n(X * 0.8, Y * 0.8) + 0.28 * n(X * 0.3 + 50, Y * 0.3 + 11)
          + 0.2 * n(X * 0.04 + 9, Y * 0.5 + 3);
        T[i] = v; sum += v; sq += v * v;
      }
    }
    const mean = sum / N, sd = Math.sqrt(sq / N - mean * mean) || 1;
    this.tooth = new Uint8Array(N);
    for (let i = 0; i < N; i++) this.tooth[i] = clamp(128 + ((T[i] - mean) / sd) * 42, 0, 255);
    this.lowA = new Uint8Array(N); this.lowB = new Uint8Array(N);
    const sA = Math.max(W, H) * 0.09, sB = Math.max(W, H) * 0.035;
    for (let y = 0, i = 0; y < H; y++) {
      for (let x = 0; x < W; x++, i++) {
        this.lowA[i] = clamp(this.noise.fbm(x / sA, y / sA, 3) * 255 * 1.3 - 38, 0, 255);
        this.lowB[i] = clamp(n(x / sB + 300, y / sB + 70) * 255, 0, 255);
      }
    }
  }

  applyMask(p, vary) {
    const d = this.img.data, T = this.tooth, A = this.lowA, B = this.lowB, r = this.r;
    const th = 128 + (0.5 - p) * 4 * 42, soft = 16;
    const wa = (r() - 0.5) * 2 * vary * 50, wb = (r() - 0.5) * 2 * vary * 30;
    for (let i = 0, j = 3; i < T.length; i++, j += 4) {
      const v = T[i] + ((A[i] - 128) / 128) * wa + ((B[i] - 128) / 128) * wb;
      const a = (v - th + soft) / (2 * soft);
      d[j] = a <= 0 ? 0 : a >= 1 ? 255 : a * 255;
    }
    this.mctx.putImageData(this.img, 0, 0);
  }

  // o.pressure: 0..1, how deep pigment reaches into the tooth (1 = solid)
  // o.smudge: finger blend radius in px; o.mode: composite mode
  layer(o, fn) {
    const { W, H } = this, c = this.lctx;
    c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.clearRect(0, 0, W, H); c.restore();
    c.save(); fn(c, this.r); c.restore();
    const p = o.pressure ?? 0.8;
    if (p < 0.999) {
      this.applyMask(p, o.vary ?? 1);
      c.save(); c.globalAlpha = 1; c.globalCompositeOperation = 'destination-in';
      c.drawImage(this.msk, 0, 0); c.restore();
    }
    const m = this.ctx;
    m.save();
    if (this.clipFn && !o.noClip) this.clipFn(m);
    m.globalAlpha = o.alpha ?? 1;
    m.globalCompositeOperation = o.mode ?? 'source-over';
    if (o.smudge) m.filter = `blur(${o.smudge.toFixed(1)}px)`;
    m.drawImage(this.lay, 0, 0);
    m.restore();
  }
}

// --------------------------------------------------------------- marks

// A tapered mark along a quadratic curve: one touch of a stick or pencil.
function ribbon(c, x0, y0, qx, qy, x1, y1, w, taper = 0.6, n = 7) {
  const L = [], R = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n, u = 1 - t;
    const x = u * u * x0 + 2 * u * t * qx + t * t * x1;
    const y = u * u * y0 + 2 * u * t * qy + t * t * y1;
    let tx = 2 * u * (qx - x0) + 2 * t * (x1 - qx), ty = 2 * u * (qy - y0) + 2 * t * (y1 - qy);
    const tl = Math.hypot(tx, ty) || 1; tx /= tl; ty /= tl;
    const hw = 0.5 * w * Math.pow(Math.sin(Math.PI * (0.06 + 0.88 * t)), taper) * (1.1 - 0.3 * t);
    L.push(x - ty * hw, y + tx * hw); R.push(x + ty * hw, y - tx * hw);
  }
  c.beginPath(); c.moveTo(L[0], L[1]);
  for (let i = 2; i < L.length; i += 2) c.lineTo(L[i], L[i + 1]);
  for (let i = R.length - 2; i >= 0; i -= 2) c.lineTo(R[i], R[i + 1]);
  c.closePath(); c.fill();
}

// A mark centred on (x, y). bend curves it sideways, as a wrist does.
function mark(c, x, y, ang, len, w, bend = 0, taper = 0.6) {
  const dx = (Math.cos(ang) * len) / 2, dy = (Math.sin(ang) * len) / 2;
  ribbon(c, x - dx, y - dy, x - dy * bend * 2, y + dx * bend * 2, x + dx, y + dy, w, taper, len > 60 ? 10 : 5);
}

function paint(c, col, a) { c.fillStyle = css(col); c.globalAlpha = clamp(a); }

// A filled tapered limb from a list of [x, y, width] points.
function limbPath(c, pts) {
  const L = [], R = [];
  for (let i = 0; i < pts.length; i++) {
    const p = pts[Math.max(0, i - 1)], q = pts[Math.min(pts.length - 1, i + 1)];
    let tx = q[0] - p[0], ty = q[1] - p[1];
    const tl = Math.hypot(tx, ty) || 1; tx /= tl; ty /= tl;
    const [x, y, w] = pts[i];
    L.push([x - ty * w / 2, y + tx * w / 2]); R.push([x + ty * w / 2, y - tx * w / 2]);
  }
  c.beginPath(); c.moveTo(...L[0]);
  for (const p of L) c.lineTo(...p);
  for (let i = R.length - 1; i >= 0; i--) c.lineTo(...R[i]);
  c.closePath();
}

// Sample a tapered limb along a cubic curve, with a small hand wobble.
function cubicLimb(a, b, c, d, n, w0, w1, r, wob = 0.006) {
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n, u = 1 - t;
    const x = u * u * u * a[0] + 3 * u * u * t * b[0] + 3 * u * t * t * c[0] + t * t * t * d[0];
    const y = u * u * u * a[1] + 3 * u * u * t * b[1] + 3 * u * t * t * c[1] + t * t * t * d[1];
    const k = Math.sin(Math.PI * t);
    pts.push([x + (r() - 0.5) * wob * k, y + (r() - 0.5) * wob * k, w0 + (w1 - w0) * Math.pow(t, 0.7)]);
  }
  return pts;
}

// ------------------------------------------------------------ the oak
//
// Units: the trunk base is (0, 0) and up is -y. The crown is about 2.5
// units wide and 1.56 units tall: wider than tall, like an old field oak.
// The crown is ten foliage masses, and each mass is a cluster of clumps.
// Clumps have domed tops and flat undersides, like summer clouds.

const LOBES = [
  [-0.98, -0.62, 0.27, 0], [-0.70, -0.90, 0.33, 0], [-0.34, -1.13, 0.33, 0],
  [0.05, -1.22, 0.34, 0], [0.43, -1.10, 0.32, 0], [0.76, -0.87, 0.32, 0],
  [1.02, -0.60, 0.26, 0], [-0.36, -0.80, 0.29, 1], [0.34, -0.82, 0.29, 1], [0.0, -0.95, 0.29, 1],
];

export function buildOak(seed = 11) {
  const r = mulberry32(seed);
  const J = (a) => (r() - 0.5) * a;
  const lobes = LOBES.map(([x, y, rad, inner]) => ({
    x: x + J(0.06), y: y + J(0.05), r: rad * (0.94 + r() * 0.12), inner: !!inner,
  }));
  const clumps = [];
  lobes.forEach((L, li) => {
    clumps.push({ x: L.x, y: L.y - L.r * 0.12, r: L.r * 0.66, li, ph: r() * 6.3, ph2: r() * 6.3, main: true });
    const n = 5 + Math.round(L.r * 16);
    for (let i = 0; i < n; i++) {
      const a = r() * Math.PI * 2, d = Math.sqrt(r()) * L.r * 0.62;
      const x = L.x + Math.cos(a) * d * 1.15;
      let y = L.y + Math.sin(a) * d * 0.85;
      const floor = L.y + L.r * 0.28;
      if (y > floor) y = floor - r() * 0.04;
      clumps.push({ x, y, r: L.r * (0.34 + r() * 0.2), li, ph: r() * 6.3, ph2: r() * 6.3 });
    }
  });

  const trunk = [];
  for (let i = 0; i <= 30; i++) {
    const t = i / 30;
    trunk.push([-0.022 * Math.sin(t * Math.PI) + 0.01 * t, -0.45 * t, 0.15 + 0.13 * Math.pow(1 - t, 4)]);
  }

  const limbs = lobes.map((L) => {
    const sx = clamp(L.x * 0.05, -0.05, 0.05), sy = -0.38 - r() * 0.07;
    const ex = L.x * 0.93, ey = L.y + L.r * 0.32, dx = ex - sx;
    const low = ey > -0.75;
    const c1 = [sx + dx * 0.28, sy - (low ? 0.1 : 0.22) - r() * 0.06];
    const c2 = [sx + dx * 0.72, ey + (low ? 0.14 : 0.08)];
    return cubicLimb([sx, sy], c1, c2, [ex, ey], 28, L.inner ? 0.05 : 0.068, 0.022, r);
  });

  const twigs = [];
  for (const k of clumps) {
    if (k.main) continue;
    const limb = limbs[k.li];
    const a = limb[Math.floor((0.6 + r() * 0.35) * (limb.length - 1))];
    const e = [k.x, k.y + k.r * 0.3];
    twigs.push(cubicLimb(a, [a[0] + (e[0] - a[0]) * 0.3, a[1] - 0.05], [e[0], e[1] + 0.05], e, 10, 0.017, 0.006, r, 0.008));
  }

  // buttress roots at the trunk foot
  const flare = [[-1, 0.34, 0.1], [-0.55, 0.2, 0.07], [0.45, 0.22, 0.08], [1, 0.36, 0.1], [0.08, 0.12, 0.06]].map(
    ([dir, len, w]) => {
      const sx = dir * 0.05, ex = dir * len;
      return cubicLimb([sx, -0.04], [sx + (ex - sx) * 0.35, -0.01], [sx + (ex - sx) * 0.75, 0.02], [ex, 0.035], 14, w, 0.008, r, 0.004);
    });

  // the roots under the ground, a mirror of the crown
  const deep = [];
  function grow(x, y, a, len, w, depth) {
    const pts = []; let cx = x, cy = y, ca = a; const N = 16;
    for (let i = 0; i <= N; i++) {
      pts.push([cx, cy, w * (1 - 0.8 * (i / N))]);
      ca += J(0.26) + (Math.PI / 2 - ca) * 0.018;
      if (cy < 0.06) ca = clamp(ca, 0.12, Math.PI - 0.12);
      cx += (Math.cos(ca) * len) / N; cy += (Math.sin(ca) * len) / N;
    }
    deep.push({ pts, depth });
    if (depth < 3) {
      const kids = depth === 0 ? 2 : 1 + (r() < 0.6 ? 1 : 0);
      for (let k = 0; k < kids; k++) {
        const i = Math.floor((0.35 + r() * 0.5) * N);
        const side = k % 2 ? 1 : -1;
        grow(pts[i][0], pts[i][1], ca + side * (0.4 + r() * 0.5), len * 0.62, pts[i][2] * 0.7, depth + 1);
      }
    }
  }
  [[0.12, 0.78], [0.5, 0.7], [0.98, 0.58], [1.55, 0.5], [2.15, 0.6], [2.62, 0.72], [3.0, 0.8]].forEach(([a, len], i) =>
    grow((i - 3) * 0.035, 0.02, a + J(0.1), len * (0.9 + r() * 0.2), 0.055, 0));

  return { lobes, clumps, trunk, limbs, twigs, flare, deep };
}

function clumpR(k, a) { return k.r * (1 + 0.1 * Math.sin(3 * a + k.ph) + 0.06 * Math.sin(5 * a + k.ph2)); }

// Signed distance-like field of the crown, in units. Positive is inside.
function crownField(oak) {
  const ks = oak.clumps;
  return (x, y) => {
    let m = -9;
    for (let i = 0; i < ks.length; i++) {
      const k = ks[i], dx = x - k.x, dy = y - k.y;
      if (Math.abs(dx) > k.r * 1.25 + 0.2 || Math.abs(dy) > k.r * 1.25 + 0.2) continue;
      const f = clumpR(k, Math.atan2(dy, dx)) - Math.hypot(dx, dy);
      if (f > m) m = f;
    }
    return m;
  };
}

function lobedPath(c, k, P, s, grow = 0) {
  c.beginPath();
  for (let i = 0; i <= 40; i++) {
    const a = (i / 40) * Math.PI * 2, rr = clumpR(k, a) + grow;
    const [x, y] = P(k.x + Math.cos(a) * rr, k.y + Math.sin(a) * rr);
    i ? c.lineTo(x, y) : c.moveTo(x, y);
  }
  c.closePath();
}

function crownBox(oak) {
  let x0 = 9, x1 = -9, y0 = 9, y1 = -9;
  for (const k of oak.clumps) {
    x0 = Math.min(x0, k.x - k.r * 1.2); x1 = Math.max(x1, k.x + k.r * 1.2);
    y0 = Math.min(y0, k.y - k.r * 1.2); y1 = Math.max(y1, k.y + k.r * 1.2);
  }
  return { x0, x1, y0, y1 };
}

// Paint the oak. T maps units to pixels: { ox, oy, s }.
// env: { sun: [px, py], skyAt(x, y) -> rgb, detail }
function paintOak(st, oak, T, env) {
  const { s } = T, det = env.detail ?? 1;
  const P = (x, y) => [T.ox + x * s, T.oy + y * s];
  const sun = [(env.sun[0] - T.ox) / s, (env.sun[1] - T.oy) / s];
  const F = crownField(oak);
  const sunW = (x, y) => Math.exp(-Math.hypot(x - sun[0], y - sun[1]) / 0.95);
  const box = crownBox(oak);
  const px = (pts) => pts.map(([x, y, w]) => [T.ox + x * s, T.oy + y * s, w * s]);

  const clumpsIn = (inner) => oak.clumps
    .filter((k) => oak.lobes[k.li].inner === inner)
    .sort((a, b) => a.y - b.y);

  function foliage(list) {
    st.layer({ pressure: 1 }, (c) => {
      paint(c, INK.leafDeep, 1);
      for (const k of list) { lobedPath(c, k, P, s); c.fill(); }
    });
    st.layer({ pressure: 0.93, vary: 0.6 }, (c, r) => {
      const J = (a) => (r() - 0.5) * a;
      for (const k of list) {
        const n = Math.round(det * 2.4 * Math.PI * k.r * k.r / (0.034 * 0.012 * 0.6));
        for (let i = 0; i < n; i++) {
          const a = r() * Math.PI * 2, d = Math.sqrt(r()) * clumpR(k, a) * 0.98;
          const ux = k.x + Math.cos(a) * d, uy = k.y + Math.sin(a) * d;
          const v = (uy - k.y) / k.r;
          const tone = clamp(0.4 - v * 0.5 + J(0.35));
          let col = tone < 0.5 ? mix(INK.leafDeep, INK.leafDark, tone * 2) : mix(INK.leafDark, INK.leafMid, (tone - 0.5) * 2);
          if (v < -0.4 && r() < 0.45) col = mix(col, INK.leafCool, 0.2 + 0.3 * r() * (-v));
          if (r() < 0.12) col = mix(col, INK.leafOlive, 0.6);
          const len = (0.02 + r() * 0.03) * s;
          paint(c, col, 0.5 + 0.5 * r());
          mark(c, ...P(ux, uy), a + Math.PI / 2 + J(1.3), len, len * (0.28 + r() * 0.22), J(0.6), 0.5);
        }
      }
    });
  }

  function woodLayer(limbs, base, smallMarks) {
    st.layer({ pressure: 1 }, (c) => {
      paint(c, base, 1);
      for (const L of limbs) { limbPath(c, L); c.fill(); }
    });
    st.layer({ pressure: 0.72 }, (c, r) => {
      const J = (a) => (r() - 0.5) * a;
      for (const L of limbs) {
        let len = 0;
        for (let i = 1; i < L.length; i++) len += Math.hypot(L[i][0] - L[i - 1][0], L[i][1] - L[i - 1][1]);
        const avgW = L.reduce((a, p) => a + p[2], 0) / L.length;
        const n = Math.round(det * 2.2 * len * avgW / ((smallMarks ? 0.012 : 0.04) * 0.007 * s * s));
        for (let j = 0; j < n; j++) {
          const i = Math.floor(r() * (L.length - 1));
          const p = L[i], q = L[i + 1];
          const ang = Math.atan2(q[1] - p[1], q[0] - p[0]);
          const nx = -Math.sin(ang), ny = Math.cos(ang);
          const o = J(2) * 0.95, t = r();
          const x = p[0] + (q[0] - p[0]) * t + nx * o * p[2] / 2, y = p[1] + (q[1] - p[1]) * t + ny * o * p[2] / 2;
          const ux = (x - T.ox) / s, uy = (y - T.oy) / s;
          const side = Math.sign(o) || 1;
          const face = (nx * side * (sun[0] - ux) + ny * side * (sun[1] - uy)) / (Math.hypot(sun[0] - ux, sun[1] - uy) || 1);
          const sw = sunW(ux, uy);
          let col = mix(INK.woodDark, INK.woodMid, r());
          let a = 0.35 + 0.4 * r();
          if (Math.abs(o) > 0.55 && face > 0.1 && r() < 0.35 + sw) {
            col = mix(INK.woodWarm, INK.rimWarm, clamp(sw * face * 1.4));
            a = 0.3 + 0.6 * sw;
          } else if (r() < 0.25) { col = INK.night; a = 0.6; }
          paint(c, col, a);
          const ml = (smallMarks ? 0.012 : 0.03 + r() * 0.05) * s;
          mark(c, x, y, ang + J(0.15), ml, Math.max(1, (0.004 + r() * 0.006) * s), J(0.2), 0.7);
        }
      }
    });
    // graphite contours and the warm edge where the low sun touches the bark
    st.layer({ pressure: 0.78 }, (c, r) => {
      for (const L of limbs) {
        for (const side of [-1, 1]) {
          for (let i = 0; i < L.length - 1; i++) {
            const p = L[i], q = L[i + 1];
            const ang = Math.atan2(q[1] - p[1], q[0] - p[0]);
            const nx = -Math.sin(ang) * side, ny = Math.cos(ang) * side;
            const x0 = p[0] + nx * p[2] / 2, y0 = p[1] + ny * p[2] / 2;
            const x1 = q[0] + nx * q[2] / 2, y1 = q[1] + ny * q[2] / 2;
            const ux = (x0 - T.ox) / s, uy = (y0 - T.oy) / s;
            const dl = Math.hypot(sun[0] - ux, sun[1] - uy) || 1;
            const face = (nx * (sun[0] - ux) + ny * (sun[1] - uy)) / dl;
            const sw = sunW(ux, uy);
            if (r() < 0.8) {
              paint(c, INK.night, 0.7);
              ribbon(c, x0, y0, (x0 + x1) / 2, (y0 + y1) / 2, x1, y1, Math.max(1, 0.0035 * s), 0.3, 3);
            }
            if (face > 0.15 && r() < 0.9) {
              const k = clamp(face * (0.25 + sw * 1.3));
              paint(c, mix(INK.rimRose, INK.rimHot, clamp(sw * 1.2)), k);
              const ix = -nx * Math.max(1, 0.003 * s), iy = -ny * Math.max(1, 0.003 * s);
              ribbon(c, x0 + ix, y0 + iy, (x0 + x1) / 2 + ix, (y0 + y1) / 2 + iy, x1 + ix, y1 + iy, Math.max(1, 0.005 * s * (0.5 + k)), 0.3, 3);
            }
          }
        }
      }
    });
  }

  // 1. the far side of the crown
  foliage(clumpsIn(true));
  // 2. twigs, seen only in the gaps
  woodLayer(oak.twigs.map(px), INK.woodDark, true);
  // 3. trunk, limbs and root flare
  woodLayer([px(oak.trunk), ...oak.limbs.map(px), ...(env.flare === false ? [] : oak.flare.map(px))], INK.woodDark, false);
  // 4. the near side of the crown
  foliage(clumpsIn(false));

  // 5. leaves that break the silhouette
  const edge = [];
  const tries = Math.round(det * 90000);
  {
    const r = st.r;
    for (let i = 0; i < tries; i++) {
      const ux = box.x0 + r() * (box.x1 - box.x0), uy = box.y0 + r() * (box.y1 - box.y0);
      const f = F(ux, uy);
      if (f > -0.03 && f < 0.03) edge.push([ux, uy, f]);
    }
  }
  st.layer({ pressure: 0.85 }, (c, r) => {
    for (const [ux, uy, f] of edge) {
      if (f > 0.005 || r() < 0.4) continue;
      const len = (0.01 + r() * 0.02) * s;
      paint(c, r() < 0.5 ? INK.leafDeep : INK.leafDark, 0.85);
      mark(c, ...P(ux, uy), r() * Math.PI * 2, len, len * 0.45, (r() - 0.5) * 0.8, 0.5);
    }
  });

  // 6. the rim of light around the crown, in coloured pencil
  const normal = (x, y) => {
    const e = 0.008, gx = F(x + e, y) - F(x - e, y), gy = F(x, y + e) - F(x, y - e);
    const l = Math.hypot(gx, gy) || 1;
    return [-gx / l, -gy / l];
  };
  const lit = [];
  for (const [ux, uy, f] of edge) {
    if (f < -0.004 || f > 0.026) continue;
    const [nx, ny] = normal(ux, uy);
    const dl = Math.hypot(sun[0] - ux, sun[1] - uy) || 1;
    const face = (nx * (sun[0] - ux) + ny * (sun[1] - uy)) / dl;
    const sw = sunW(ux, uy);
    const warm = clamp(face * 0.8 + 0.25) * (0.3 + 0.9 * sw) + Math.max(0, ny) * 0.25;
    const cool = Math.max(0, -ny) * 0.3 * (1 - sw);
    lit.push({ ux, uy, f, nx, ny, warm, cool, sw });
  }
  st.layer({ pressure: 0.66 }, (c, r) => {
    for (const p of lit) {
      const depth = 1 - clamp(p.f / 0.026);
      const ang = Math.atan2(p.ny, p.nx) + Math.PI / 2 + (r() - 0.5) * 0.9;
      const len = (0.008 + r() * 0.018) * s;
      if (p.warm * depth > r() * 1.05) {
        paint(c, mix(INK.rimRose, p.sw > 0.55 ? INK.rimHot : INK.rimWarm, clamp(p.sw * 1.5)), (0.4 + 0.6 * r()) * clamp(p.warm));
        mark(c, ...P(p.ux, p.uy), ang, len, Math.max(1, len * 0.3), (r() - 0.5) * 0.6, 0.6);
      } else if (p.cool * depth > r() * 1.3) {
        paint(c, INK.rimCool, 0.18 + 0.2 * r());
        mark(c, ...P(p.ux, p.uy), ang, len, Math.max(1, len * 0.25), (r() - 0.5) * 0.6, 0.6);
      }
    }
  });

  // 7. light through the leaves: small windows near the sun
  const holes = [];
  for (let i = 0; i < 4000 && holes.length < Math.round(10 + 10 * det); i++) {
    const ux = box.x0 + st.r() * (box.x1 - box.x0), uy = -0.5 - st.r() * 0.6;
    const f = F(ux, uy);
    if (f > 0.02 && f < 0.07 && st.r() < sunW(ux, uy) * 1.4) holes.push([ux, uy]);
  }
  st.layer({ pressure: 0.7 }, (c, r) => {
    for (const [ux, uy] of holes) {
      const n = 5 + Math.floor(r() * 9);
      for (let i = 0; i < n; i++) {
        const x = ux + (r() - 0.5) * 0.03, y = uy + (r() - 0.5) * 0.02;
        const [X, Y] = P(x, y);
        paint(c, mix(env.skyAt(X, Y), INK.rimHot, 0.25), 0.55 + 0.4 * r());
        mark(c, X, Y, r() * 6.3, (0.005 + r() * 0.01) * s, (0.003 + r() * 0.005) * s, 0.3, 0.5);
      }
    }
  });

  // 8. halation: the warm light that bleeds over the dark edges
  st.layer({ pressure: 0.9, smudge: Math.max(1, 0.012 * s), mode: 'screen', alpha: 0.7 }, (c, r) => {
    for (const p of lit) {
      if (p.warm < 0.55 || r() < 0.55) continue;
      paint(c, mix(INK.rimRose, INK.rimWarm, p.sw), 0.12 * p.warm * (0.4 + p.sw));
      mark(c, ...P(p.ux, p.uy), r() * 6.3, 0.05 * s, 0.025 * s, 0, 0.4);
    }
    for (const [ux, uy] of holes) {
      paint(c, INK.rimWarm, 0.28);
      mark(c, ...P(ux, uy), r() * 6.3, 0.06 * s, 0.05 * s, 0, 0.3);
    }
  });
}

// A little warm light with a soft halo: a firefly, or a kept memory.
function glowLights(st, pts, u, warmth = 1) {
  st.layer({ pressure: 0.9, smudge: 7 * u, mode: 'screen' }, (c, r) => {
    for (const [x, y, k] of pts) { paint(c, INK.rimWarm, 0.32 * k * warmth); mark(c, x, y, r() * 6, 26 * u * k, 22 * u * k, 0, 0.3); }
  });
  st.layer({ pressure: 0.72 }, (c, r) => {
    for (const [x, y, k] of pts) { paint(c, mix(INK.rimWarm, INK.rimHot, r()), 0.9); mark(c, x, y, r() * 6, 5 * u * k, 4 * u * k, 0, 0.3); }
  });
}

// ------------------------------------------------------------ the artwork

export function renderHero(makeCanvas, W = 3840, H = 2160, seed = 11, onStep = () => {}) {
  const st = new Studio(makeCanvas, W, H, seed);
  const u = W / 3840, r = st.r, J = (a) => (r() - 0.5) * a;
  const { fbm } = st.noise;
  const oak = buildOak(seed);
  const crestX = 0.55 * W, crestY = 0.735 * H;
  const s = 0.388 * H;
  const T = { ox: crestX, oy: crestY + 6 * u, s };
  const sun = [T.ox - 0.5 * s, 0.664 * H], sunR = 72 * u;

  const skyStops = [
    [0.0, hex('#11142c')], [0.17, hex('#1c2045')], [0.36, hex('#3b335f')], [0.5, hex('#74486a')],
    [0.6, hex('#b0606a')], [0.67, hex('#dc8a5e')], [0.72, hex('#f4bc78')],
  ];
  const skyAt = (x, y) => {
    let col = ramp(skyStops, y / H);
    const d = Math.hypot(x - sun[0], (y - sun[1]) * 1.6) / H;
    col = mix(col, hex('#ffe2a2'), 0.75 * Math.exp(-d * 4.2));
    return lift(col, 1 - 0.18 * Math.abs(x - sun[0]) / W);
  };
  const hill = (x) => {
    const dx = (x - crestX) / W;
    return crestY + (dx < 0 ? 0.24 : 0.3) * H * dx * dx * 2.6 + (fbm(x / (0.12 * W), 4.2, 3) - 0.5) * 26 * u;
  };

  st.ctx.fillStyle = css(INK.paper); st.ctx.fillRect(0, 0, W, H);

  // sky: blended under-layer, then visible strokes, then strokes that circle the sun
  st.layer({ pressure: 0.97, smudge: 22 * u, vary: 0.5 }, (c) => {
    for (let i = 0; i < 1300; i++) {
      const x = r() * W, y = r() * 0.8 * H;
      const ds = clamp(Math.hypot(x - sun[0], y - sun[1]) / (0.3 * W));
      paint(c, skyAt(x, y + J(40 * u)), 0.9);
      mark(c, x, y, J(0.08), (300 + r() * 800) * u * (0.35 + 0.65 * ds), (50 + r() * 90) * u, J(0.06), 0.3);
    }
  });
  onStep('sky base');
  st.layer({ pressure: 0.56 }, (c) => {
    for (let i = 0; i < 2600; i++) {
      const x = r() * W, y = Math.pow(r(), 0.8) * 0.78 * H;
      paint(c, lift(skyAt(x, y + J(90 * u)), 0.95 + r() * 0.15), 0.35 + 0.35 * r());
      mark(c, x, y, J(0.12), (120 + r() * 380) * u, (12 + r() * 30) * u, J(0.12), 0.5);
    }
  });
  st.layer({ pressure: 0.66 }, (c) => {
    for (let i = 0; i < 900; i++) {
      const rho = sunR * 1.15 + Math.pow(r(), 1.6) * 0.5 * H;
      const a0 = r() * Math.PI * 2, span = Math.min(0.7, ((90 + r() * 260) * u) / rho);
      const am = a0 + span / 2;
      if (Math.abs(Math.cos(am)) * 0.5 > Math.abs(Math.sin(am)) * 0.9) continue;
      const x0 = sun[0] + Math.cos(a0) * rho, y0 = sun[1] + Math.sin(a0) * rho * 0.5;
      const x1 = sun[0] + Math.cos(a0 + span) * rho, y1 = sun[1] + Math.sin(a0 + span) * rho * 0.5;
      const k = rho / Math.cos(span / 2);
      const qx = sun[0] + Math.cos(am) * k, qy = sun[1] + Math.sin(am) * k * 0.5;
      if (qy > 0.78 * H) continue;
      paint(c, lift(skyAt(qx, qy), 1.04 + r() * 0.1), 0.25 + 0.35 * r());
      ribbon(c, x0, y0, qx, qy, x1, y1, (8 + r() * 24) * u, 0.5, 9);
    }
  });

  // clouds lit from below
  const bands = [[0.2, 0.535, 0.3, 1], [0.08, 0.47, 0.17, 0.7], [0.8, 0.505, 0.24, 0.8], [0.35, 0.625, 0.16, 1.2], [0.9, 0.39, 0.12, 0.5]];
  st.layer({ pressure: 0.6, smudge: 3 * u }, (c) => {
    for (const [bx, by, bl, k] of bands) {
      for (let i = 0; i < 70 * k; i++) {
        const x = (bx + J(bl)) * W, y = by * H + J(26 * u) * k;
        const below = y > by * H;
        const sw = Math.exp(-Math.abs(x - sun[0]) / (0.35 * W));
        paint(c, below ? mix(INK.rimRose, INK.rimHot, sw) : mix(hex('#5c4468'), INK.rimRose, sw * 0.6), 0.35 + 0.4 * r());
        mark(c, x, y, J(0.05), (60 + r() * 240) * u, (5 + r() * 14) * u, J(0.05), 0.5);
      }
    }
  });

  // stars and a new moon
  st.layer({ pressure: 0.6 }, (c) => {
    for (let i = 0; i < 300; i++) {
      const x = r() * W, y = Math.pow(r(), 1.9) * 0.52 * H;
      if (Math.hypot(x - sun[0], y - sun[1]) < 0.35 * H) continue;
      const z = (1.6 + Math.pow(r(), 3) * 3.4) * u;
      paint(c, INK.chalk, 0.4 + 0.6 * r() * (1 - y / (0.52 * H)));
      mark(c, x, y, r() * 3, z * 1.6, z, 0.2, 0.3);
      if (r() < 0.05) {
        paint(c, INK.chalk, 0.5);
        mark(c, x, y, 0, z * 9, z * 0.6, 0, 0.8); mark(c, x, y, Math.PI / 2, z * 9, z * 0.6, 0, 0.8);
      }
    }
  });
  const moon = [0.892 * W, 0.115 * H], mR = 30 * u;
  st.layer({ pressure: 0.9, smudge: 26 * u, mode: 'screen', alpha: 0.5 }, (c) => {
    paint(c, hex('#8b86b8'), 0.6); c.beginPath(); c.arc(...moon, mR * 3, 0, 7); c.fill();
  });
  st.layer({ pressure: 0.8 }, (c) => {
    paint(c, INK.chalk, 1); c.beginPath(); c.arc(...moon, mR, 0, 7); c.fill();
    c.globalCompositeOperation = 'destination-out';
    c.beginPath(); c.arc(moon[0] + mR * 0.42, moon[1] - mR * 0.2, mR * 0.92, 0, 7); c.fill();
  });

  // the sun, low and half sunk behind the far hills
  st.layer({ pressure: 0.92, smudge: 90 * u, mode: 'screen', alpha: 0.85 }, (c) => {
    paint(c, hex('#ffcf86'), 0.55); c.beginPath(); c.ellipse(...sun, sunR * 5, sunR * 3.6, 0, 0, 7); c.fill();
  });
  st.layer({ pressure: 0.9, smudge: 2 * u }, (c) => {
    paint(c, hex('#fff1cc'), 1); c.beginPath(); c.arc(...sun, sunR, 0, 7); c.fill();
    for (let i = 0; i < 60; i++) {
      paint(c, mix(hex('#ffe4a8'), hex('#ffffff'), r()), 0.5);
      mark(c, sun[0] + J(sunR * 1.4), sun[1] + J(sunR * 1.4), J(0.3), (20 + r() * 50) * u, 8 * u, 0.2, 0.5);
    }
  });
  onStep('sky');

  // far, middle and near hills
  const ridges = [
    { base: 0.69, amp: 0.055, sc: 0.33, col: hex('#8e5e7c'), haze: 0.3, rim: 1 },
    { base: 0.728, amp: 0.05, sc: 0.21, col: hex('#563f69'), haze: 0.2, rim: 0.6 },
    { base: 0.77, amp: 0.045, sc: 0.15, col: hex('#2d2642'), haze: 0.05, rim: 0.35 },
  ];
  ridges.forEach((R, ri) => {
    const ry = (x) => (R.base + R.amp * (fbm(x / (R.sc * W) + ri * 40, ri * 7.7, 4) - 0.5) * 2) * H;
    const colAt = (x, y) => mix(R.col, skyAt(x, y - 30 * u), R.haze * Math.exp(-Math.abs(x - sun[0]) / (0.4 * W)));
    st.layer({ pressure: 1 }, (c) => {
      const step = 8 * u;
      for (let x = 0; x <= W; x += step) {
        paint(c, colAt(x, ry(x)), 1); c.beginPath();
        c.moveTo(x - 1, ry(x - 1)); c.lineTo(x + step + 1, ry(x + step + 1)); c.lineTo(x + step + 1, H); c.lineTo(x - 1, H); c.closePath(); c.fill();
      }
    });
    st.layer({ pressure: 0.58 }, (c) => {
      for (let i = 0; i < 700; i++) {
        const x = r() * W, y0 = ry(x), y = y0 + Math.pow(r(), 1.5) * 0.1 * H;
        paint(c, lift(colAt(x, y), 0.85 + r() * 0.3), 0.3 + 0.3 * r());
        mark(c, x, y, J(0.2) + 0.08, (40 + r() * 160) * u, (5 + r() * 12) * u, J(0.1), 0.5);
      }
      if (ri === 1) {
        for (let i = 0; i < 26; i++) {
          const x = (0.02 + r() * 0.28 + (r() < 0.3 ? 0.62 : 0)) * W, y = ry(x);
          paint(c, lift(R.col, 0.8), 0.9);
          for (let j = 0; j < 7; j++) mark(c, x + J(10 * u), y - (3 + r() * 9) * u, r() * 6, 9 * u, 7 * u, 0.3, 0.4);
        }
      }
    });
    st.layer({ pressure: 0.68 }, (c) => {
      for (let x = 0; x < W; x += 5 * u) {
        const sw = Math.exp(-Math.abs(x - sun[0]) / (0.22 * W)) * R.rim;
        if (r() > sw * 1.4) continue;
        paint(c, mix(INK.rimRose, INK.rimHot, sw), 0.3 + 0.6 * sw);
        mark(c, x, ry(x) + 2 * u, J(0.1), (14 + r() * 30) * u, (2 + 3 * sw) * u, 0, 0.5);
      }
    });
    if (ri < 2) {
      // a band of valley mist in front of this hill
      st.layer({ pressure: 0.8, smudge: 14 * u, mode: 'screen', alpha: 0.6 }, (c) => {
        for (let i = 0; i < 90; i++) {
          const x = r() * W, y = (R.base + 0.035 + J(0.02)) * H;
          paint(c, mix(hex('#8a6a9a'), INK.rimRose, Math.exp(-Math.abs(x - sun[0]) / (0.3 * W))), 0.14);
          mark(c, x, y, J(0.03), (200 + r() * 500) * u, (10 + r() * 20) * u, 0, 0.4);
        }
      });
    }
  });
  // far windows: somebody is home
  glowLights(st, [[0.165 * W, 0.795 * H, 0.9], [0.19 * W, 0.8 * H, 0.7], [0.115 * W, 0.81 * H, 0.6], [0.93 * W, 0.8 * H, 0.6]], u, 0.8);
  onStep('hills');

  // the oak's hill
  st.layer({ pressure: 1 }, (c) => {
    c.fillStyle = css(hex('#16121e')); c.beginPath(); c.moveTo(0, H);
    for (let x = 0; x <= W; x += 6 * u) c.lineTo(x, hill(x));
    c.lineTo(W, H); c.closePath(); c.fill();
  });
  st.layer({ pressure: 0.6 }, (c) => {
    for (let i = 0; i < 3200; i++) {
      const x = r() * W, y0 = hill(x), y = y0 + Math.pow(r(), 1.3) * (H - y0);
      const slope = Math.atan2(hill(x + 20 * u) - hill(x - 20 * u), 40 * u);
      const near = 1 - clamp((y - y0) / (0.12 * H));
      const col = mix(hex('#120f18'), mix(hex('#2c2a3c'), hex('#3a2b36'), Math.exp(-Math.abs(x - sun[0]) / (0.3 * W))), near * 0.8);
      paint(c, col, 0.35 + 0.35 * r());
      mark(c, x, y, slope + J(0.12), (40 + r() * 140) * u, (5 + r() * 10) * u, J(0.12), 0.5);
    }
  });

  // a pale path that climbs to the tree
  const pathPt = (t) => {
    const p = [[0.31 * W, H + 40 * u], [0.37 * W, 0.86 * H], [0.47 * W, 0.79 * H], [crestX - 30 * u, crestY + 16 * u]];
    const v = 1 - t;
    return [0, 1].map((k) => v * v * v * p[0][k] + 3 * v * v * t * p[1][k] + 3 * v * t * t * p[2][k] + t * t * t * p[3][k]);
  };
  st.layer({ pressure: 0.52 }, (c) => {
    for (let i = 0; i < 2600; i++) {
      const t = Math.pow(r(), 0.8);
      const [x, y] = pathPt(t), [x2, y2] = pathPt(Math.min(1, t + 0.01));
      const w = (330 - 310 * Math.pow(t, 0.6)) * u, o = J(2);
      const ang = Math.atan2(y2 - y, x2 - x);
      const fade = 1 - Math.pow(Math.abs(o), 3);
      paint(c, mix(hex('#4e4258'), hex('#a7807a'), t * 0.9), (0.14 + 0.28 * r()) * fade);
      mark(c, x - Math.sin(ang) * o * w / 2, y + Math.cos(ang) * o * w / 2, ang + J(0.5), (14 + r() * 50) * u * (1.2 - t), (3 + r() * 6) * u, J(0.3), 0.6);
    }
  });
  onStep('ground');

  // the oak
  paintOak(st, oak, T, { sun, skyAt, detail: 1 });
  onStep('oak');

  // the empty swing, still moving a little
  {
    const limb = oak.limbs[0];
    let best = limb[0];
    for (const p of limb) if (Math.abs(p[0] + 0.62) < Math.abs(best[0] + 0.62)) best = p;
    const ax = T.ox + best[0] * s, ay = T.oy + best[1] * s + best[2] * s * 0.35;
    const gy = hill(ax);
    const seatY = gy - 0.13 * s, drift = 0.028 * s, half = 0.05 * s;
    const ropes = [[ax - 0.042 * s, ay + 3 * u, ax - half + drift, seatY - 0.004 * s], [ax + 0.042 * s, ay - 1 * u, ax + half + drift, seatY + 0.004 * s]];
    st.layer({ pressure: 0.85 }, (c) => {
      for (const [x0, y0, x1, y1] of ropes) {
        paint(c, INK.night, 0.95);
        ribbon(c, x0, y0, (x0 + x1) / 2 + 3 * u, (y0 + y1) / 2, x1, y1, 3.2 * u, 0.15, 14);
      }
      paint(c, INK.woodDark, 1);
      const sx0 = ropes[0][2] - 0.012 * s, sx1 = ropes[1][2] + 0.012 * s;
      ribbon(c, sx0, ropes[0][3] + 3 * u, (sx0 + sx1) / 2, (ropes[0][3] + ropes[1][3]) / 2 + 4 * u, sx1, ropes[1][3] + 3 * u, 0.016 * s, 0.08, 8);
    });
    st.layer({ pressure: 0.66 }, (c) => {
      for (const [x0, y0, x1, y1] of ropes) {
        paint(c, INK.rimWarm, 0.75);
        ribbon(c, x0 + 2 * u, y0 + 8 * u, (x0 + x1) / 2 + 5 * u, (y0 + y1) / 2, x1 + 2 * u, y1, 1.8 * u, 0.4, 14);
      }
      paint(c, INK.rimHot, 0.8);
      const sx0 = ropes[0][2] - 0.012 * s, sx1 = ropes[1][2] + 0.012 * s;
      ribbon(c, sx0, ropes[0][3] - 4 * u, (sx0 + sx1) / 2, (ropes[0][3] + ropes[1][3]) / 2 - 3 * u, sx1, ropes[1][3] - 4 * u, 3 * u, 0.3, 8);
    });
  }

  // grass along the crest, backlit
  st.layer({ pressure: 0.8 }, (c) => {
    for (let x = 0; x < W; x += 2.6 * u) {
      const y = hill(x) + 4 * u, len = (6 + Math.pow(r(), 2) * 30) * u, a = -Math.PI / 2 + J(0.7);
      paint(c, hex('#100d16'), 0.9);
      ribbon(c, x, y, x + Math.cos(a) * len * 0.5 + J(4 * u), y + Math.sin(a) * len * 0.5, x + Math.cos(a) * len, y + Math.sin(a) * len, 2.4 * u, 0.3, 4);
    }
  });
  st.layer({ pressure: 0.64 }, (c) => {
    for (let x = 0; x < W; x += 2 * u) {
      const sw = Math.exp(-Math.abs(x - sun[0]) / (0.2 * W));
      if (r() > sw * 1.2) continue;
      const y = hill(x) - (2 + r() * 14) * u;
      paint(c, mix(INK.rimRose, INK.rimHot, sw), 0.4 + 0.5 * sw);
      mark(c, x, y, -Math.PI / 2 + J(0.6), (5 + r() * 9) * u, 1.6 * u, 0.2, 0.5);
    }
  });

  // the foreground: tall grass, and one dandelion clock
  const head = [0.158 * W, 0.6 * H];
  st.layer({ pressure: 0.88 }, (c) => {
    paint(c, INK.night, 1);
    const blades = (x0, x1, n, lean, hmax) => {
      for (let i = 0; i < n; i++) {
        const x = x0 + r() * (x1 - x0), len = (120 + Math.pow(r(), 1.5) * hmax) * u;
        const a = -Math.PI / 2 + lean + J(0.5);
        const ex = x + Math.cos(a) * len, ey = H + Math.sin(a) * len;
        ribbon(c, x, H + 10 * u, x + Math.cos(a) * len * 0.4, H + Math.sin(a) * len * 0.6, ex + J(60 * u), ey, (5 + r() * 7) * u, 0.25, 12);
      }
    };
    blades(-40 * u, 0.24 * W, 150, 0.15, 520);
    blades(0.84 * W, W + 40 * u, 90, -0.12, 380);
    const sx = 0.142 * W;
    ribbon(c, sx, H + 10 * u, sx + 30 * u, 0.82 * H, head[0], head[1] + 8 * u, 6 * u, 0.1, 24);
    for (let i = 0; i < 9; i++) {
      const x = 0.86 * W + r() * 0.12 * W, top = (0.66 + r() * 0.12) * H;
      ribbon(c, x, H, x - 20 * u, (H + top) / 2, x - 40 * u + J(30 * u), top, 3.5 * u, 0.1, 14);
      for (let j = 0; j < 9; j++) mark(c, x - 40 * u + J(16 * u), top + j * 9 * u, -1.2 + J(0.6), 16 * u, 5 * u, 0.3, 0.6);
    }
  });
  st.layer({ pressure: 0.66 }, (c) => {
    for (let i = 0; i < 70; i++) {
      const x = r() * 0.24 * W, y = H - (40 + r() * 420) * u;
      paint(c, mix(INK.rimRose, INK.rimWarm, r()), 0.35);
      mark(c, x, y, -1.3 + J(0.5), (20 + r() * 50) * u, 1.6 * u, 0.1, 0.6);
    }
  });
  // the clock: seeds radiate from the head, with a gap where the wind took them
  const pappus = (c, x, y, a, len, col, alpha) => {
    paint(c, col, alpha);
    const ex = x + Math.cos(a) * len, ey = y + Math.sin(a) * len;
    ribbon(c, x, y, (x + ex) / 2, (y + ey) / 2, ex, ey, 1.5 * u, 0.2, 3);
    for (let k = -3; k <= 3; k++) {
      const b = a + k * 0.32;
      mark(c, ex + Math.cos(b) * len * 0.14, ey + Math.sin(b) * len * 0.14, b, len * 0.28, 1.1 * u, 0, 0.5);
    }
  };
  st.layer({ pressure: 0.72 }, (c) => {
    for (let i = 0; i < 170; i++) {
      const a = r() * Math.PI * 2;
      if (r() < smooth(0.2, 0.9, Math.cos(a + 0.25)) * 0.85) continue;
      const lit = clamp(Math.cos(a - Math.atan2(sun[1] - head[1], sun[0] - head[0])) * 0.5 + 0.5);
      pappus(c, head[0], head[1], a, (50 + r() * 16) * u, mix(INK.chalk, INK.rimHot, lit * 0.7), 0.55 + 0.4 * r());
    }
    paint(c, INK.night, 1); c.beginPath(); c.arc(...head, 7 * u, 0, 7); c.fill();
  });
  // seeds on the wind, carried toward the oak
  const drift = [];
  for (let i = 0; i < 46; i++) {
    const t = Math.pow(r(), 0.85);
    const x = head[0] + 60 * u + t * (0.2 * W) + J(90 * u) * (0.3 + t);
    const y = head[1] - 30 * u - Math.sin(t * Math.PI * 0.9) * 0.17 * H + J(140 * u) * t;
    drift.push([x, y, 1 - t * 0.6]);
  }
  st.layer({ pressure: 0.7 }, (c) => {
    for (const [x, y, k] of drift) pappus(c, x, y, J(1) - 1.5, 22 * u * k, mix(INK.chalk, INK.rimHot, 0.4), 0.85);
  });
  st.layer({ pressure: 0.9, smudge: 6 * u, mode: 'screen' }, (c) => {
    for (const [x, y, k] of drift) { paint(c, INK.rimWarm, 0.16); mark(c, x, y - 20 * u * k, 0, 34 * u * k, 30 * u * k, 0, 0.3); }
  });

  // fireflies in the grass and under the crown
  const flies = [];
  for (let i = 0; i < 54; i++) {
    const x = T.ox + J(2.3 * s), y = T.oy - Math.pow(r(), 1.3) * 0.55 * s + 0.06 * s;
    flies.push([x, y, 0.4 + r() * 0.9]);
  }
  glowLights(st, flies, u);

  // light across everything: rays and halation from the low sun
  st.layer({ pressure: 0.95, smudge: 34 * u, mode: 'screen', alpha: 0.75 }, (c) => {
    for (const a of [-2.75, -2.45, -2.1, -1.75, -1.42, -1.05, -0.7, -0.35]) {
      const len = (0.35 + r() * 0.3) * H, a2 = a + J(0.05);
      paint(c, INK.rimHot, 0.055);
      ribbon(c, ...sun, sun[0] + Math.cos(a2) * len * 0.5, sun[1] + Math.sin(a2) * len * 0.5, sun[0] + Math.cos(a2) * len, sun[1] + Math.sin(a2) * len, (40 + r() * 70) * u, 0.4, 12);
    }
    paint(c, hex('#ffc477'), 0.22); c.beginPath(); c.ellipse(...sun, sunR * 2.6, sunR * 1.8, 0, 0, 7); c.fill();
  });

  // charcoal pushed into the edges of the sheet
  st.layer({ pressure: 0.85, smudge: 40 * u, alpha: 0.8 }, (c) => {
    for (let i = 0; i < 260; i++) {
      const side = i % 4;
      const t = r();
      const [x, y, a] = side === 0 ? [t * W, J(80 * u), 0] : side === 1 ? [t * W, H + J(60 * u), 0]
        : side === 2 ? [J(80 * u), t * H, Math.PI / 2] : [W + J(80 * u), t * H, Math.PI / 2];
      paint(c, INK.night, side === 1 ? 0.45 : 0.32);
      mark(c, x, y, a + J(0.2), (200 + r() * 500) * u, (60 + r() * 120) * u, J(0.1), 0.4);
    }
  });
  onStep('done');
  return st.canvas;
}

// ------------------------------------------------------------ the mark

// The medallion: the oak against its sun, its roots lit in the earth.
// Mark geometry, in fractions of the canvas size S.
const MARK = { R: 0.455, ground: 0.22, s: 0.65, sun: [-0.45, -0.17] };

function wobblyCircle(c, cx, cy, R, noise, amp, phase = 0) {
  c.beginPath();
  for (let i = 0; i <= 160; i++) {
    const a = (i / 160) * Math.PI * 2;
    const rr = R * (1 + amp * (noise.n2(Math.cos(a) * 2.2 + 10 + phase, Math.sin(a) * 2.2 + 10) - 0.5));
    const x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr;
    i ? c.lineTo(x, y) : c.moveTo(x, y);
  }
  c.closePath();
}

export function renderMark(makeCanvas, S = 2048, seed = 11, onStep = () => {}) {
  const st = new Studio(makeCanvas, S, S, seed + 1);
  const u = S / 2048, r = st.r, J = (a) => (r() - 0.5) * a;
  const oak = buildOak(seed);
  const cx = S / 2, cy = S / 2, R = MARK.R * S, yg = cy + MARK.ground * R, s = MARK.s * R;
  const T = { ox: cx, oy: yg + 0.012 * R, s };
  const sun = [T.ox + MARK.sun[0] * s, T.oy + MARK.sun[1] * s];
  const ground = (x) => yg + 0.075 * R * ((x - cx) / R) ** 2 + (st.noise.fbm(x / (0.3 * R), 2, 3) - 0.5) * 0.02 * R;
  const disc = (c) => { wobblyCircle(c, cx, cy, R, st.noise, 0.008); c.clip(); };
  const stops = [
    [0, hex('#fff2c8')], [0.09, hex('#ffd88c')], [0.26, hex('#f3a45c')], [0.48, hex('#cf6e5e')],
    [0.72, hex('#8a4866')], [1.0, hex('#4a3460')], [1.45, hex('#262246')],
  ];
  const skyAt = (x, y) => {
    const d = Math.hypot(x - sun[0], (y - sun[1]) * 1.15) / R;
    return lift(ramp(stops, d), 1 - 0.12 * clamp((cy - y) / R));
  };

  st.ctx.save(); disc(st.ctx); st.ctx.fillStyle = css(INK.paper); st.ctx.fillRect(0, 0, S, S); st.ctx.restore();
  st.clipFn = disc;

  // sky in rings of pastel around the sun
  st.layer({ pressure: 0.97, smudge: 16 * u, vary: 0.5 }, (c) => {
    for (let i = 0; i < 1500; i++) {
      const x = cx + J(2.1 * R), y = cy + J(2.1 * R);
      paint(c, skyAt(x, y + J(30 * u)), 0.9);
      mark(c, x, y, Math.atan2(y - sun[1], x - sun[0]) + Math.PI / 2 + J(0.3), (120 + r() * 300) * u, (30 + r() * 50) * u, J(0.1), 0.3);
    }
  });
  st.layer({ pressure: 0.6 }, (c) => {
    for (let i = 0; i < 1500; i++) {
      const rho = 0.05 * R + Math.pow(r(), 1.2) * 1.6 * R;
      const a0 = r() * Math.PI * 2, span = Math.min(0.7, ((60 + r() * 200) * u) / rho);
      const am = a0 + span / 2, k = rho / Math.cos(span / 2);
      const qx = sun[0] + Math.cos(am) * k, qy = sun[1] + Math.sin(am) * k;
      paint(c, lift(skyAt(qx, qy), 1.03 + r() * 0.12), 0.3 + 0.35 * r());
      ribbon(c, sun[0] + Math.cos(a0) * rho, sun[1] + Math.sin(a0) * rho, qx, qy,
        sun[0] + Math.cos(a0 + span) * rho, sun[1] + Math.sin(a0 + span) * rho, (6 + r() * 18) * u, 0.5, 9);
    }
  });
  st.layer({ pressure: 0.6 }, (c) => {
    for (let i = 0; i < 70; i++) {
      const x = cx + J(1.6 * R), y = cy - R + Math.pow(r(), 1.6) * 0.75 * R;
      if (Math.hypot(x - sun[0], y - sun[1]) < 0.9 * R) continue;
      const z = (2 + Math.pow(r(), 3) * 4) * u;
      paint(c, INK.chalk, 0.5 + 0.5 * r()); mark(c, x, y, r() * 3, z * 1.6, z, 0.2, 0.3);
    }
  });
  st.layer({ pressure: 0.92, smudge: 60 * u, mode: 'screen', alpha: 0.8 }, (c) => {
    paint(c, hex('#ffd08a'), 0.5); c.beginPath(); c.arc(...sun, 0.32 * R, 0, 7); c.fill();
  });
  st.layer({ pressure: 0.9, smudge: 1.5 * u }, (c) => {
    paint(c, hex('#fff3d0'), 1); c.beginPath(); c.arc(...sun, 0.075 * R, 0, 7); c.fill();
  });
  // a low far hill
  st.layer({ pressure: 1 }, (c) => {
    c.fillStyle = css(hex('#5e3d62')); c.beginPath(); c.moveTo(cx - R * 1.1, S);
    for (let x = cx - R * 1.1; x <= cx + R * 1.1; x += 4 * u) c.lineTo(x, yg - 0.05 * R - (st.noise.fbm(x / (0.25 * R), 5, 4) - 0.35) * 0.1 * R);
    c.lineTo(cx + R * 1.1, S); c.closePath(); c.fill();
  });
  st.layer({ pressure: 0.68 }, (c) => {
    for (let x = cx - R; x < cx + R; x += 4 * u) {
      const sw = Math.exp(-Math.abs(x - sun[0]) / (0.35 * R));
      if (r() > sw * 1.3) continue;
      const y = yg - 0.05 * R - (st.noise.fbm(x / (0.25 * R), 5, 4) - 0.35) * 0.1 * R;
      paint(c, mix(INK.rimRose, INK.rimHot, sw), 0.4 + 0.5 * sw);
      mark(c, x, y + 2 * u, J(0.1), (12 + r() * 24) * u, (2 + 3 * sw) * u, 0, 0.5);
    }
  });
  onStep('sky');

  // the earth, and the roots that hold the light
  st.layer({ pressure: 1 }, (c) => {
    c.fillStyle = css(INK.earth); c.beginPath(); c.moveTo(cx - R * 1.1, S);
    for (let x = cx - R * 1.1; x <= cx + R * 1.1; x += 4 * u) c.lineTo(x, ground(x));
    c.lineTo(cx + R * 1.1, S); c.closePath(); c.fill();
  });
  st.layer({ pressure: 0.58 }, (c) => {
    for (let i = 0; i < 1400; i++) {
      const x = cx + J(2 * R), y0 = ground(x), y = y0 + r() * (cy + R - y0);
      paint(c, r() < 0.15 ? hex('#3b2b2e') : mix(hex('#1e1826'), hex('#2d2336'), r()), 0.35 + 0.3 * r());
      mark(c, x, y, J(0.12), (40 + r() * 120) * u, (5 + r() * 9) * u, J(0.1), 0.5);
    }
  });
  const roots = oak.deep.map((d) => ({ depth: d.depth, pts: d.pts.map(([x, y, w]) => [T.ox + x * s, T.oy + y * s, w * s]) }));
  st.layer({ pressure: 0.9, smudge: 10 * u, mode: 'screen' }, (c) => {
    for (const d of roots) {
      paint(c, INK.rimWarm, 0.32 * (1 - d.depth * 0.2));
      limbPath(c, d.pts.map(([x, y, w]) => [x, y, w * 2.6 + 6 * u])); c.fill();
    }
  });
  st.layer({ pressure: 0.76 }, (c) => {
    for (const d of roots) {
      paint(c, mix(INK.rimWarm, hex('#c0704a'), d.depth / 3), 0.92 - d.depth * 0.17);
      limbPath(c, d.pts.map(([x, y, w]) => [x + J(1.5 * u), y + J(1.5 * u), Math.max(1.5 * u, w)])); c.fill();
    }
    for (const d of roots) {
      if (d.depth > 1) continue;
      paint(c, INK.rimHot, 0.75 - d.depth * 0.3);
      limbPath(c, d.pts.slice(0, 12).map(([x, y, w]) => [x, y, Math.max(1.2 * u, w * 0.35)])); c.fill();
    }
  });
  onStep('earth');

  paintOak(st, oak, T, { sun, skyAt, detail: 1, flare: true });

  st.layer({ pressure: 0.8 }, (c) => {
    for (let x = cx - R; x < cx + R; x += 2.4 * u) {
      const y = ground(x) + 3 * u, len = (5 + Math.pow(r(), 2) * 22) * u, a = -Math.PI / 2 + J(0.7);
      paint(c, hex('#0f0c14'), 0.9);
      ribbon(c, x, y, x + Math.cos(a) * len * 0.5, y + Math.sin(a) * len * 0.5, x + Math.cos(a) * len, y + Math.sin(a) * len, 2.2 * u, 0.3, 4);
    }
  });
  st.layer({ pressure: 0.64 }, (c) => {
    for (let x = cx - R; x < cx + R; x += 2 * u) {
      const sw = Math.exp(-Math.abs(x - sun[0]) / (0.4 * R));
      if (r() > sw * 1.2) continue;
      paint(c, mix(INK.rimRose, INK.rimHot, sw), 0.4 + 0.5 * sw);
      mark(c, x, ground(x) - (2 + r() * 10) * u, -Math.PI / 2 + J(0.6), (5 + r() * 8) * u, 1.6 * u, 0.2, 0.5);
    }
  });
  const flies = [];
  for (let i = 0; i < 16; i++) flies.push([cx + J(1.5 * R), yg - Math.pow(r(), 1.2) * 0.4 * R, 0.5 + r() * 0.7]);
  glowLights(st, flies, u * 0.9);
  st.layer({ pressure: 0.95, smudge: 30 * u, mode: 'screen', alpha: 0.7 }, (c) => {
    paint(c, hex('#ffc477'), 0.25); c.beginPath(); c.arc(...sun, 0.16 * R, 0, 7); c.fill();
  });
  onStep('oak');

  // the ring, in charcoal, with a gold pencil line inside it
  st.clipFn = null;
  st.layer({ pressure: 0.985, vary: 0.2 }, (c) => {
    c.strokeStyle = css(hex('#14111a')); c.lineWidth = 0.05 * R;
    wobblyCircle(c, cx, cy, R * 1.004, st.noise, 0.008); c.stroke();
  });
  st.layer({ pressure: 0.7 }, (c) => {
    for (let i = 0; i < 220; i++) {
      const a0 = r() * Math.PI * 2, span = 0.06 + r() * 0.12, rr = R * (1.004 + J(0.03));
      const k = rr / Math.cos(span / 2);
      paint(c, mix(hex('#14111a'), hex('#2e2538'), r()), 0.7);
      ribbon(c, cx + Math.cos(a0) * rr, cy + Math.sin(a0) * rr, cx + Math.cos(a0 + span / 2) * k, cy + Math.sin(a0 + span / 2) * k,
        cx + Math.cos(a0 + span) * rr, cy + Math.sin(a0 + span) * rr, (0.012 + r() * 0.02) * R, 0.4, 9);
    }
    for (let i = 0; i < 90; i++) {
      const a0 = (i / 90) * Math.PI * 2 + J(0.03), span = 0.075, rr = R * 0.965;
      if (r() < 0.12) continue;
      const k = rr / Math.cos(span / 2);
      const sw = clamp(0.5 + 0.5 * Math.cos(a0 - Math.atan2(sun[1] - cy, sun[0] - cx)));
      paint(c, mix(hex('#b8794f'), INK.rimHot, sw), 0.55 + 0.35 * sw);
      ribbon(c, cx + Math.cos(a0) * rr, cy + Math.sin(a0) * rr, cx + Math.cos(a0 + span / 2) * k, cy + Math.sin(a0 + span / 2) * k,
        cx + Math.cos(a0 + span) * rr, cy + Math.sin(a0 + span) * rr, 0.0065 * R, 0.3, 7);
    }
  });
  onStep('done');
  return st.canvas;
}

// ------------------------------------------------------------ flat marks

// Small icons cannot hold paper grain, so they use the same geometry as
// flat shapes, drawn at 8x and reduced. mono: one ink, for print.
function flatMark(makeCanvas, S, seed, mono) {
  const k = 8, B = S * k;
  const cv = makeCanvas(B, B), c = cv.getContext('2d');
  const noise = makeNoise(seed * 7 + 4);
  const oak = buildOak(seed);
  const small = S <= 32;
  const cx = B / 2, cy = B / 2, R = (small ? 0.47 : MARK.R) * B, yg = cy + MARK.ground * R;
  const s = (small ? 0.7 : MARK.s) * R;
  const T = { ox: cx, oy: yg + 0.012 * R, s };
  const P = (x, y) => [T.ox + x * s, T.oy + y * s];
  const px = (pts) => pts.map(([x, y, w]) => [T.ox + x * s, T.oy + y * s, w * s]);
  const sun = [T.ox + MARK.sun[0] * s, T.oy + MARK.sun[1] * s];
  const ground = (x) => yg + 0.075 * R * ((x - cx) / R) ** 2;
  const inkC = mono ? hex('#1a1520') : hex('#18131e');
  const ringW = (small ? 0.1 : S <= 64 ? 0.07 : 0.05) * R;

  c.save(); wobblyCircle(c, cx, cy, R, noise, 0.006); c.clip();
  if (!mono) {
    const g = c.createRadialGradient(...sun, 0, ...sun, R * 1.5);
    [[0, '#fff2c8'], [0.07, '#ffd88c'], [0.2, '#f3a45c'], [0.36, '#cf6e5e'], [0.6, '#8a4866'], [1, '#3a2c55']].forEach(([t, h]) => g.addColorStop(t, h));
    c.fillStyle = g; c.fillRect(0, 0, B, B);
  } else {
    c.strokeStyle = css(inkC); c.lineWidth = 0.018 * R;
    c.beginPath(); c.arc(...sun, 0.11 * R, 0, 7); c.stroke();
  }
  c.fillStyle = css(inkC);
  c.beginPath(); c.moveTo(cx - R * 1.1, B);
  for (let x = cx - R * 1.1; x <= cx + R * 1.1; x += k) c.lineTo(x, ground(x));
  c.lineTo(cx + R * 1.1, B); c.closePath(); c.fill();
  if (S >= 48) {
    // roots: lit lines in colour, knocked out of the ink in mono
    c.save();
    if (mono) c.globalCompositeOperation = 'destination-out';
    c.fillStyle = mono ? '#000' : '#eea35c';
    for (const d of oak.deep) {
      if (d.depth > (S >= 128 ? 2 : 1)) continue;
      c.globalAlpha = mono ? 1 : 1 - d.depth * 0.25;
      limbPath(c, px(d.pts).map(([x, y, w]) => [x, y, Math.max(w * (S >= 128 ? 1 : 1.6), 0.014 * R)])); c.fill();
    }
    c.restore();
  }
  // the silhouette: every clump grown a little so small sizes stay solid
  c.fillStyle = css(inkC);
  const grow = small ? 0.025 : 0.004;
  for (const kp of oak.clumps) {
    if (small && !kp.main) continue;
    lobedPath(c, small ? { ...kp, r: kp.r * 1.12 } : kp, P, s, grow); c.fill();
  }
  const limbs = [px(oak.trunk), ...oak.limbs.map(px), ...oak.flare.map(px)];
  for (const L of limbs) { limbPath(c, L.map(([x, y, w]) => [x, y, w * (small ? 1.3 : 1)])); c.fill(); }
  if (!small && !mono) {
    // a warm rim on the sun side of the trunk and the low limbs
    c.strokeStyle = '#f6b25f'; c.lineWidth = 0.012 * R; c.globalAlpha = 0.85;
    const t = px(oak.trunk);
    c.beginPath(); t.forEach(([x, y, w], i) => (i ? c.lineTo(x - w / 2 + c.lineWidth / 2, y) : c.moveTo(x - w / 2 + c.lineWidth / 2, y))); c.stroke();
    c.globalAlpha = 1;
  }
  c.restore();
  c.strokeStyle = css(inkC); c.lineWidth = ringW;
  wobblyCircle(c, cx, cy, R - ringW * 0.3, noise, 0.006); c.stroke();
  return downsample(makeCanvas, cv, S);
}

export const renderIcon = (makeCanvas, S, seed = 11) => flatMark(makeCanvas, S, seed, false);
export const renderMono = (makeCanvas, S, seed = 11) => flatMark(makeCanvas, S, seed, true);

// Halve the image until it is close to the target, for clean reduction.
export function downsample(makeCanvas, src, S) {
  let cur = src;
  while (cur.width / 2 >= S) {
    const n = makeCanvas(Math.round(cur.width / 2), Math.round(cur.height / 2)), x = n.getContext('2d');
    x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high';
    x.drawImage(cur, 0, 0, n.width, n.height); cur = n;
  }
  if (cur.width !== S) {
    const n = makeCanvas(S, Math.round((S * cur.height) / cur.width)), x = n.getContext('2d');
    x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high';
    x.drawImage(cur, 0, 0, n.width, n.height); cur = n;
  }
  return cur;
}
