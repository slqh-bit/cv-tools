"""CLAHE avec un clip_limit propre a chaque tuile.

Le melange d'images CLAHE calculees a des forces differentes ne realise PAS
une CLAHE a clip variable: moyenner deux courbes tonales differentes donne une
courbe plus plate que chacune des deux. Il faut faire varier le clip a
l'interieur de l'algorithme, sur les LUT, avant l'interpolation.
"""
import numpy as np
import cv2


def _tile_lut(tile: np.ndarray, clip: float) -> np.ndarray:
    """LUT d'egalisation d'une tuile - meme arithmetique qu'OpenCV.

    Reproduit CLAHE_CalcLut_Body: limite entiere, redistribution par lots avec
    le reste etale, puis cumul mis a l'echelle par l'aire de la tuile (sans
    recaler sur le premier niveau, contrairement a une egalisation classique).
    """
    area = tile.size
    hist = np.bincount(tile.ravel(), minlength=256).astype(np.int64)

    if clip > 0.0:
        limit = max(int(clip * area / 256.0), 1)
        clipped = int(np.maximum(hist - limit, 0).sum())
        hist = np.minimum(hist, limit)

        batch, residual = divmod(clipped, 256)
        hist += batch
        if residual:
            step = max(256 // residual, 1)
            idx = np.arange(0, 256, step)[:residual]
            hist[idx] += 1

    return np.clip(np.round(hist.cumsum() * (255.0 / area)), 0, 255).astype(np.uint8)


def clahe_variable(channel: np.ndarray, clip_map: np.ndarray) -> np.ndarray:
    """Egalise un canal 8 bits, une force par tuile, LUT interpolees.

    Args:
        channel: canal 8 bits (h, w)
        clip_map: (grid, grid), le clip_limit voulu pour chaque tuile
    """
    grid_y, grid_x = clip_map.shape
    h, w = channel.shape
    th, tw = h // grid_y, w // grid_x

    luts = np.empty((grid_y, grid_x, 256), np.uint8)
    for i in range(grid_y):
        for j in range(grid_x):
            y1 = i * th if i < grid_y - 1 else i * th
            y2 = (i + 1) * th if i < grid_y - 1 else h
            x2 = (j + 1) * tw if j < grid_x - 1 else w
            luts[i, j] = _tile_lut(channel[y1:y2, j * tw:x2], float(clip_map[i, j]))

    # position de chaque pixel dans la grille des centres de tuiles
    ty = (np.arange(h) + 0.5) / th - 0.5
    tx = (np.arange(w) + 0.5) / tw - 0.5
    # Clamper *apres* avoir pris le voisin, pas avant: sinon la premiere
    # demi-tuile melange les tuiles 0 et 1 alors qu'OpenCV n'utilise que la 0.
    by, bx = np.floor(ty), np.floor(tx)
    i0 = np.clip(by, 0, grid_y - 1).astype(np.intp)
    j0 = np.clip(bx, 0, grid_x - 1).astype(np.intp)
    i1 = np.clip(by + 1, 0, grid_y - 1).astype(np.intp)
    j1 = np.clip(bx + 1, 0, grid_x - 1).astype(np.intp)
    fy = np.clip(ty - by, 0, 1)[:, None]
    fx = np.clip(tx - bx, 0, 1)[None, :]

    v = channel
    a = luts[i0[:, None], j0[None, :], v].astype(np.float64)
    b = luts[i0[:, None], j1[None, :], v].astype(np.float64)
    c = luts[i1[:, None], j0[None, :], v].astype(np.float64)
    d = luts[i1[:, None], j1[None, :], v].astype(np.float64)
    top = a * (1 - fx) + b * fx
    bot = c * (1 - fx) + d * fx
    return np.clip(np.round(top * (1 - fy) + bot * fy), 0, 255).astype(np.uint8)


def clahe_guided(image: np.ndarray, clip_map: np.ndarray) -> np.ndarray:
    """Applique clahe_variable sur le L de LAB, comme le mode 'lab' existant."""
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    lab[:, :, 0] = clahe_variable(lab[:, :, 0], clip_map)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
