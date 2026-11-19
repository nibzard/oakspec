# The Keeping Oak

The OAK project mark. An old field oak stands on a hill at dusk with the
sun low behind it. An empty swing hangs from the long left limb. Dandelion
seeds drift toward the tree. In the medallion mark, the roots glow in the
earth below the tree, so the earth holds as much as the crown.

## Concept

OAK is shared memory, kept for others. The oak keeps it: what grows above
is held below. The swing is the memory of somebody who was there. The
seeds are wishes on their way. The scene shows the moment after sunset that
you want to keep.

## Materials

Every mark is drawn in code on simulated paper. No image assets are used.

- **Soft pastel**: the sky, the hills, and the foliage masses. Wide marks,
  some blended with a finger (blur after the paper tooth takes pigment).
- **Charcoal**: the trunk, the limbs, the ring, and the dark edges of the
  sheet.
- **Colored pencil**: the warm rim of light, the bark, the grass, and the
  roots.
- **Graphite**: the broken contours of the trunk and the limbs.
- **Chalk**: the stars, the moon, the seeds, and the path.

The paper has a fixed tooth: fine grain, mid grain, and long fibers. Each
layer of marks is pressed into that tooth. Light pressure leaves pigment
only on the peaks, and heavy pressure fills the valleys. Pressure also
drifts across the sheet from layer to layer, as a hand does.

## Assets

Run `npm install`, then `npm run render`. The files go to `out/`.

| File | Use |
| --- | --- |
| `oak-hero.png` | The artwork, 3840 × 2160 |
| `oak-mark-4096.png` | The medallion mark, for print and merch |
| `oak-mark-2048.png` to `oak-mark-128.png` | The mark for screens |
| `apple-touch-icon.png` | iOS home screen, 180 px, opaque |
| `favicon.ico`, `favicon-16.png` to `favicon-64.png` | Browser icons |
| `oak-mono-4096.png` | One ink on transparency, for screen print and embroidery |

Small icons cannot hold paper grain, so `favicon-*` and `oak-mono-*` draw
the same oak geometry as flat shapes. At 32 px and below, the crown uses
only its ten large masses, and the trunk is thicker.

To draw in a browser, serve this folder (for example,
`python3 -m http.server`) and open `index.html`. Each output has an
**Export PNG** button.

All randomness is seeded, so every run gives the same image. To get a
different tree, change the seed in `render.mjs` or `index.html`.
