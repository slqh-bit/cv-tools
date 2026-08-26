import numpy as np, cv2
from src.core.loader import ImageLoader
from src.filters.clahe import apply_clahe
from src.filters.noise_analysis import estimate_noise
from guided_clahe import tile_demand_map
from clahe_lut import clahe_guided

def metrics(before, after):
    a = cv2.cvtColor(before, cv2.COLOR_RGB2LAB)[:, :, 0]
    b = cv2.cvtColor(after, cv2.COLOR_RGB2LAB)[:, :, 0]
    return (float(b.std() / a.std()),
            float(estimate_noise(after) / max(estimate_noise(before), 0.3)))

paths = ['cctv/darkest.jpg', 'cctv/flattest.jpg', 'cctv/softest.jpg',
         'cctv/brightest.jpg', 'cctv/sharpest.jpg', 'cctv/most_blown.jpg',
         'reference/building.jpg', 'reference/lena.png']

deltas = []
print('image             contraste  bruit dirigee  bruit uniforme  gain')
for rel in paths:
    img = cv2.resize(ImageLoader('validation/corpus/' + rel).load(), (512, 384),
                     interpolation=cv2.INTER_AREA)
    grid = np.arange(0.5, 6.01, 0.25)
    cs, ns = [], []
    for clip in grid:
        c, n = metrics(img, apply_clahe(img, clip_limit=float(clip), tile_grid_size=8))
        cs.append(c); ns.append(n)
    cs, ns = np.array(cs), np.array(ns)

    demand = tile_demand_map(img, 8)
    clip_map = 0.5 + (6.0 - 0.5) * demand
    gc, gn = metrics(img, clahe_guided(img, clip_map))

    name = rel.split('/')[-1]
    if not (cs.min() <= gc <= cs.max()):
        print(f'{name:17} x{gc:5.3f}  hors de la plage uniforme [{cs.min():.3f}, {cs.max():.3f}]')
        continue
    equiv = float(np.interp(gc, cs, ns))
    delta = (equiv - gn) / equiv * 100
    deltas.append(delta)
    print(f'{name:17} x{gc:5.3f}     x{gn:5.3f}         x{equiv:5.3f}      {delta:+5.1f}%')

if deltas:
    print(f'\nMoyenne : {np.mean(deltas):+.1f}% de bruit en moins a contraste egal '
          f'({sum(d > 0 for d in deltas)}/{len(deltas)} images)')
