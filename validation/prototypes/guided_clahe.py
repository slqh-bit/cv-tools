"""Prototype: CLAHE dirigee par l'histogramme local de chaque tuile."""
import numpy as np, cv2
from cv_tools.filters.noise_analysis import estimate_noise
from cv_tools.filters.clahe import apply_clahe


def tile_demand_map(image, grid=8):
    """Combien chaque tuile *merite* d'etre amplifiee, entre 0 et 1.

    Deux facteurs, et il faut les deux:

      besoin  - l'histogramme de la tuile est-il comprime ? Une tuile deja
                contrastee n'a rien a gagner; une tuile terne en a besoin.
      surete  - ce qu'on amplifierait est-il du signal ? Ecart-type sur sigma
                de bruit. Une tuile terne *parce qu'elle est vide* (le ciel)
                a un mauvais score et ne doit pas etre touchee.

    C'est le croisement des deux qui designe le cas interessant en forensique:
    un detail faible mais reel - un visage dans l'ombre.

    Les deux facteurs sont normalises par rang dans l'image, donc la carte ne
    depend pas de l'exposition absolue de la scene.
    """
    lab_l = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)[:, :, 0]
    h, w = lab_l.shape
    th, tw = h // grid, w // grid
    spread = np.zeros((grid, grid), np.float64)
    snr = np.zeros((grid, grid), np.float64)
    for i in range(grid):
        for j in range(grid):
            tile = lab_l[i * th:(i + 1) * th, j * tw:(j + 1) * tw]
            spread[i, j] = tile.std()
            snr[i, j] = tile.std() / max(estimate_noise(tile), 0.5)

    def rank01(a):
        order = a.ravel().argsort().argsort().astype(np.float64)
        return (order / max(order.max(), 1)).reshape(a.shape)

    besoin = 1.0 - rank01(spread)
    surete = rank01(snr)
    return besoin * surete


def guided_clahe(image, clip_low=1.0, clip_high=4.0, grid=8):
    """Melange des CLAHE a plusieurs forces, pondere par la carte de demande.

    Chaque composante est monotone par tuile et les poids sont fixes
    spatialement, donc le resultat reste monotone en chaque point - ce qui
    compte pour la defendabilite forensique.
    """
    demand = tile_demand_map(image, grid)
    clip_map = clip_low + (clip_high - clip_low) * demand

    h, w = image.shape[:2]
    smooth = cv2.resize(clip_map.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)

    levels = np.linspace(clip_low, clip_high, 5)
    step = levels[1] - levels[0]
    out = np.zeros(image.shape, np.float64)
    weight_total = np.zeros((h, w), np.float64)
    for clip in levels:
        wgt = np.clip(1.0 - np.abs(smooth - clip) / step, 0.0, 1.0)
        if wgt.max() <= 0:
            continue
        out += apply_clahe(image, clip_limit=float(clip), tile_grid_size=grid).astype(np.float64) * wgt[..., None]
        weight_total += wgt
    out /= np.maximum(weight_total, 1e-6)[..., None]
    return np.clip(out, 0, 255).astype(np.uint8), clip_map


def measure(before, after):
    """Metriques globales, independantes de la formule de decision.

    Mesurer le contraste sur les tuiles que la formule choisit d'amplifier
    serait circulaire. On mesure donc sur l'image entiere.
    """
    l_in = cv2.cvtColor(before, cv2.COLOR_RGB2LAB)[:, :, 0]
    l_out = cv2.cvtColor(after, cv2.COLOR_RGB2LAB)[:, :, 0]
    return (float(l_out.std() / l_in.std()),
            float(estimate_noise(after) / max(estimate_noise(before), 0.3)))
