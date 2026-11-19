// Render every brand asset to ./out. Usage: node render.mjs [--quick]
import { createCanvas } from '@napi-rs/canvas';
import { writeFileSync, mkdirSync } from 'node:fs';
import { renderHero, renderMark, renderIcon, renderMono, downsample } from './oak.js';

const mk = (w, h) => createCanvas(w, h);
const quick = process.argv.includes('--quick');
const only = process.argv.find((a) => a.startsWith('--only='))?.slice(7);
const out = new URL('./out/', import.meta.url).pathname;
mkdirSync(out, { recursive: true });
const save = (name, c) => { writeFileSync(out + name, c.toBuffer('image/png')); console.log('wrote', name, `${c.width}x${c.height}`); };
// An ICO file that holds PNG images, one directory entry for each size.
function ico(pngs, sizes) {
  const head = Buffer.alloc(6 + 16 * pngs.length);
  head.writeUInt16LE(0, 0); head.writeUInt16LE(1, 2); head.writeUInt16LE(pngs.length, 4);
  let off = head.length;
  pngs.forEach((b, i) => {
    const e = 6 + 16 * i;
    head.writeUInt8(sizes[i] % 256, e); head.writeUInt8(sizes[i] % 256, e + 1);
    head.writeUInt16LE(1, e + 4); head.writeUInt16LE(32, e + 6);
    head.writeUInt32LE(b.length, e + 8); head.writeUInt32LE(off, e + 12);
    off += b.length;
  });
  return Buffer.concat([head, ...pngs]);
}
const timed = (label, fn) => { const t = Date.now(); const r = fn(); console.log(label, ((Date.now() - t) / 1000).toFixed(1) + 's'); return r; };

if (!only || only === 'hero') {
  const [W, H] = quick ? [1920, 1080] : [3840, 2160];
  save('oak-hero.png', timed('hero', () => renderHero(mk, W, H)));
}
if (!only || only === 'mark') {
  const big = timed('mark', () => renderMark(mk, quick ? 1024 : 4096));
  save(`oak-mark-${big.width}.png`, big);
  if (!quick) for (const S of [2048, 1024, 512]) save(`oak-mark-${S}.png`, downsample(mk, big, S));
  // 128 to 256: a separate render, so the marks stay legible after reduction
  const mid = timed('mark-mid', () => renderMark(mk, 1024));
  for (const S of [256, 192, 128]) save(`oak-mark-${S}.png`, downsample(mk, mid, S));
  // Apple touch icon: opaque, because iOS fills transparency with black
  const t = mk(180, 180), x = t.getContext('2d');
  x.fillStyle = '#1b1726'; x.fillRect(0, 0, 180, 180);
  x.drawImage(downsample(mk, mid, 164), 8, 8);
  save('apple-touch-icon.png', t);
}
if (!only || only === 'icon') {
  const icons = [16, 32, 48, 64].map((S) => { const c = renderIcon(mk, S); save(`favicon-${S}.png`, c); return c; });
  writeFileSync(out + 'favicon.ico', ico(icons.slice(0, 3).map((c) => c.toBuffer('image/png')), [16, 32, 48]));
  console.log('wrote favicon.ico');
  save('oak-mono-4096.png', renderMono(mk, quick ? 1024 : 4096));
}
