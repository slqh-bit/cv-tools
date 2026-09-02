"""
Mesures pour docs/measure_3d.fr.md.

Tout le document s'appuie sur ce script : chaque chiffre cite y est produit
ici, sur une camera synthetique dont on connait la verite terrain, pour qu'on
puisse contester les nombres plutot que de les croire.

    python validation/measure_3d_study.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cv_tools.filters.measure_3d import (          # noqa: E402
    horizon_from_lines,
    measure_height,
    resolve_horizon,
    vanishing_point,
)


class Camera:
    """Stenope regardant le plan Z=0. Monde : X droite, Y avant, Z haut."""

    def __init__(self, pitch_degrees=18.0, roll_degrees=0.0,
                 camera_height=2500.0, focal=900.0, width=1920, height=1080):
        self.height_mm = camera_height
        self.K = np.array([[focal, 0.0, width / 2],
                           [0.0, focal, height / 2],
                           [0.0, 0.0, 1.0]])
        pitch = np.radians(pitch_degrees)
        roll = np.radians(roll_degrees)
        # Camera regardant +Y, inclinee vers le bas de `pitch`
        R_pitch = np.array([[1, 0, 0],
                            [0, np.cos(pitch), -np.sin(pitch)],
                            [0, np.sin(pitch), np.cos(pitch)]])
        R_axis = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
        R_roll = np.array([[np.cos(roll), -np.sin(roll), 0],
                           [np.sin(roll), np.cos(roll), 0],
                           [0, 0, 1]])
        self.R = R_roll @ R_pitch @ R_axis
        centre = np.array([0.0, 0.0, camera_height])
        self.P = self.K @ np.hstack([self.R, (-self.R @ centre).reshape(3, 1)])

    def project(self, point):
        h = self.P @ np.array([point[0], point[1], point[2], 1.0])
        return h[:2] / h[2]

    def pole(self, x, y, height):
        """Base et sommet d'un mat vertical de `height` pose en (x, y)."""
        return self.project((x, y, 0.0)), self.project((x, y, height))

    @property
    def horizon(self):
        """Horizon exact du plan Z=0 : l'image de la droite a l'infini."""
        return self.P[:, :3] @ np.array([0.0, 0.0, 1.0])

    @property
    def vertical_point(self):
        return self.P[:, :3] @ np.array([0.0, 0.0, 1.0])

    def ground_lines(self, offsets, y_near, y_far):
        """Droites au sol paralleles a Y, une par decalage en X."""
        out = []
        for x in offsets:
            near = self.project((x, y_near, 0.0))
            far = self.project((x, y_far, 0.0))
            out.append((near[0], near[1], far[0], far[1]))
        return out


def rule(title):
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def m1_origin_dependence():
    rule("M1  Le point de fuite depend-il de l'origine de l'image ?")
    lines = [(100, 100, 300, 200), (100, 500, 300, 400), (100, 300, 300, 305)]

    def vp(ls):
        v = vanishing_point(ls)
        return v[:2] / v[2]

    base = vp(lines)
    print(f"  reference                       ({base[0]:9.3f}, {base[1]:9.3f})")
    for shift in (960, 1920, 3840):
        moved = [(a + shift, b + shift, c + shift, d + shift) for a, b, c, d in lines]
        m = vp(moved) - shift
        print(f"  origine decalee de {shift:5d} px    ({m[0]:9.3f}, {m[1]:9.3f})"
              f"   derive {np.hypot(*(m - base)):6.3f} px")
    print("\n  Les lignes ne sont pas normalisees avant la SVD, donc la solution")
    print("  des moindres carres se deplace avec le coin haut-gauche de l'image.")


def m2_clicked_length():
    rule("M2  La longueur du segment clique change-t-elle le resultat ?")
    a = (100, 100, 300, 200)
    b = (100, 500, 300, 400)

    def vp(ls):
        v = vanishing_point(ls)
        return v[:2] / v[2]

    print(f"  a et b seules                   {vp([a, b])[1]:9.3f}  (y du point de fuite)")
    for label, c in (("segment long  (200 px)", (100, 300, 300, 305)),
                     ("segment moyen (100 px)", (100, 300, 200, 302.5)),
                     ("segment court ( 40 px)", (100, 300, 140, 301.0))):
        print(f"  + une 3e droite, {label}: {vp([a, b, c])[1]:9.3f}")
    print("\n  C'est la meme droite a chaque fois, cliquee plus ou moins long.")
    print("  Son influence sur les moindres carres varie pourtant du simple au")
    print("  quintuple, sans que ce soit ecrit nulle part.")


def m3_pitch_without_vertical_point():
    rule("M3  Cout d'omettre le point de fuite vertical, selon le tangage")
    print("  (reference 1800 mm a 9 m, cible 1750 mm a 14 m, camera a 2,5 m)")
    print(f"  {'tangage':>8} {'exact':>10} {'sans v':>10} {'erreur':>10}")
    for pitch in (0.0, 5.0, 10.0, 18.0, 25.0):
        cam = Camera(pitch_degrees=pitch)
        ref = cam.pole(-900, 9000, 1800.0)
        base, top = cam.pole(600, 14000, 1750.0)
        common = dict(base=base, top=top, reference_base=ref[0],
                      reference_top=ref[1], reference_height=1800.0,
                      horizon=cam.horizon)
        exact = measure_height(vertical_point=cam.vertical_point, **common)['height']
        naive = measure_height(vertical_point=None, **common)['height']
        print(f"  {pitch:7.0f}° {exact:9.1f} {naive:9.1f} {naive - exact:+9.1f} mm")


def m4_distance():
    rule("M4  Erreur selon l'eloignement, a bruit de clic constant (1 px)")
    cam = Camera(pitch_degrees=18.0)
    ref = cam.pole(-900, 9000, 1800.0)
    print(f"  {'distance':>9} {'hauteur px':>11} {'mm par px':>10} {'base-horizon':>13}")
    line = resolve_horizon(cam.horizon)
    for y in (5000, 9000, 14000, 22000, 35000):
        base, top = cam.pole(600, y, 1750.0)
        r = measure_height(base=base, top=top, reference_base=ref[0],
                           reference_top=ref[1], reference_height=1800.0,
                           horizon=cam.horizon, vertical_point=cam.vertical_point)
        y_h = -(line[0] * base[0] + line[2]) / line[1]
        print(f"  {y/1000:8.0f}m {base[1]-top[1]:10.1f} "
              f"{r['uncertainty_per_pixel']:9.1f} {base[1]-y_h:12.1f} px")


def m5_horizon_error():
    rule("M5  Cout d'un horizon mal place")
    cam = Camera(pitch_degrees=18.0)
    ref = cam.pole(-900, 9000, 1800.0)
    base, top = cam.pole(600, 14000, 1750.0)
    line = resolve_horizon(cam.horizon)
    truth = measure_height(base=base, top=top, reference_base=ref[0],
                           reference_top=ref[1], reference_height=1800.0,
                           horizon=cam.horizon,
                           vertical_point=cam.vertical_point)['height']
    print(f"  verite terrain 1750 mm, mesure exacte {truth:.1f} mm")
    print(f"  {'decalage':>10} {'hauteur':>10} {'erreur':>10} {'sensibilite rapportee':>24}")
    for delta in (1, 5, 10, 25, 50, 100):
        shifted = np.array([line[0], line[1], line[2] - line[1] * delta])
        r = measure_height(base=base, top=top, reference_base=ref[0],
                           reference_top=ref[1], reference_height=1800.0,
                           horizon=shifted, vertical_point=cam.vertical_point)
        print(f"  {delta:8d} px {r['height']:9.1f} {r['height']-truth:+9.1f} "
              f"{r['horizon_uncertainty_per_pixel']:20.2f} mm/px")


def m6_centre_of_gravity():
    rule("M6  Le pied ou le centre de gravite ? (technique Amped FIVE)")
    cam = Camera(pitch_degrees=18.0)
    ref = cam.pole(-900, 9000, 1800.0)
    print("  Marcheur : pieds ecartes de `ecart` mm le long de la marche,")
    print("  sommet du crane a l'aplomb du milieu.")
    print(f"  {'ecart':>7} {'talon avant':>13} {'talon arriere':>15} {'milieu':>10}")
    for ecart in (0, 300, 600, 900):
        y_mid = 14000.0
        top = cam.project((600, y_mid, 1750.0))
        rows = []
        for name, y in (("avant", y_mid - ecart / 2),
                        ("arriere", y_mid + ecart / 2),
                        ("milieu", y_mid)):
            b = cam.project((600, y, 0.0))
            h = measure_height(base=b, top=top, reference_base=ref[0],
                               reference_top=ref[1], reference_height=1800.0,
                               horizon=cam.horizon,
                               vertical_point=cam.vertical_point)['height']
            rows.append(h)
        print(f"  {ecart:5d}mm {rows[0]:12.1f} {rows[1]:14.1f} {rows[2]:9.1f}")
    print("\n  Le milieu est la verite ; un talon est faux des que les pieds")
    print("  sont ecartes, et l'ecart d'un pas normal est de 600 a 900 mm.")


def m7_line_separation(trials=400, noise=1.0, seed=7):
    rule(f"M7  Ecartement des droites de calibration ({trials} tirages, "
         f"bruit de clic {noise} px)")
    cam = Camera(pitch_degrees=18.0)
    ref = cam.pole(-900, 9000, 1800.0)
    base, top = cam.pole(600, 14000, 1750.0)
    rng = np.random.default_rng(seed)
    print(f"  {'ecartement':>11} {'erreur mediane':>16} {'90e centile':>13}")
    for sep in (200, 600, 1500, 3000, 6000):
        errs = []
        for _ in range(trials):
            lines = cam.ground_lines((-sep / 2, sep / 2), 6000, 30000)
            noisy = [tuple(np.array(l) + rng.normal(0, noise, 4)) for l in lines]
            try:
                h = measure_height(base=base, top=top, reference_base=ref[0],
                                   reference_top=ref[1], reference_height=1800.0,
                                   horizon=horizon_from_lines(noisy),
                                   vertical_point=cam.vertical_point)['height']
            except ValueError:
                continue
            errs.append(abs(h - 1750.0))
        errs = np.array(errs)
        print(f"  {sep:8d} mm {np.median(errs):13.1f} mm {np.percentile(errs, 90):10.1f} mm")


def m8_line_count(trials=400, noise=1.0, seed=11):
    rule(f"M8  Nombre de droites ({trials} tirages, bruit {noise} px, "
         f"ecartement fixe)")
    cam = Camera(pitch_degrees=18.0)
    ref = cam.pole(-900, 9000, 1800.0)
    base, top = cam.pole(600, 14000, 1750.0)
    rng = np.random.default_rng(seed)
    print(f"  {'droites':>8} {'erreur mediane':>16} {'90e centile':>13}")
    for count in (2, 3, 4, 6):
        offsets = np.linspace(-3000, 3000, count)
        errs = []
        for _ in range(trials):
            lines = cam.ground_lines(offsets, 6000, 30000)
            noisy = [tuple(np.array(l) + rng.normal(0, noise, 4)) for l in lines]
            try:
                h = measure_height(base=base, top=top, reference_base=ref[0],
                                   reference_top=ref[1], reference_height=1800.0,
                                   horizon=horizon_from_lines(noisy),
                                   vertical_point=cam.vertical_point)['height']
            except ValueError:
                continue
            errs.append(abs(h - 1750.0))
        errs = np.array(errs)
        print(f"  {count:8d} {np.median(errs):13.1f} mm {np.percentile(errs, 90):10.1f} mm")


def m9_reference_choice(trials=400, noise=1.0, seed=3):
    rule(f"M9  Choix de la reference ({trials} tirages, bruit {noise} px)")
    cam = Camera(pitch_degrees=18.0)
    base, top = cam.pole(600, 14000, 1750.0)
    rng = np.random.default_rng(seed)
    print(f"  {'reference':>28} {'erreur mediane':>16}")
    cases = [("montant 2030 mm a 9 m", 2030.0, 9000.0),
             ("montant 2030 mm a 20 m", 2030.0, 20000.0),
             ("borne 400 mm a 9 m", 400.0, 9000.0),
             ("mire 1800 mm a 14 m (cible)", 1800.0, 14000.0)]
    for label, h_ref, y_ref in cases:
        errs = []
        for _ in range(trials):
            rb, rt = cam.pole(-900, y_ref, h_ref)
            rb = rb + rng.normal(0, noise, 2)
            rt = rt + rng.normal(0, noise, 2)
            b = base + rng.normal(0, noise, 2)
            t = top + rng.normal(0, noise, 2)
            h = measure_height(base=b, top=t, reference_base=rb, reference_top=rt,
                               reference_height=h_ref, horizon=cam.horizon,
                               vertical_point=cam.vertical_point)['height']
            errs.append(abs(h - 1750.0))
        print(f"  {label:>28} {np.median(errs):13.1f} mm")
    print("\n  Une reference courte transmet son erreur de clic amplifiee par")
    print("  le rapport des hauteurs ; une reference lointaine, par le rapport")
    print("  des distances a l'horizon.")


def m10_roll():
    rule("M10  Roulis : horizon horizontal contre horizon a deux points de fuite")
    print(f"  {'roulis':>8} {'2 directions':>14} {'1 direction':>13} {'erreur':>10}")
    for roll in (0.0, 2.0, 5.0, 10.0):
        cam = Camera(pitch_degrees=18.0, roll_degrees=roll)
        ref = cam.pole(-900, 9000, 1800.0)
        base, top = cam.pole(600, 14000, 1750.0)
        along = cam.ground_lines((-3000, 3000), 6000, 30000)
        across = []
        for y in (9000, 20000):
            near = cam.project((-4000, y, 0.0))
            far = cam.project((4000, y, 0.0))
            across.append((near[0], near[1], far[0], far[1]))
        common = dict(base=base, top=top, reference_base=ref[0],
                      reference_top=ref[1], reference_height=1800.0,
                      vertical_point=cam.vertical_point)
        two = measure_height(horizon=horizon_from_lines(along, across), **common)['height']
        one = measure_height(horizon=horizon_from_lines(along), **common)['height']
        print(f"  {roll:7.0f}° {two:13.1f} {one:12.1f} {one - two:+9.1f} mm")


if __name__ == '__main__':
    m1_origin_dependence()
    m2_clicked_length()
    m3_pitch_without_vertical_point()
    m4_distance()
    m5_horizon_error()
    m6_centre_of_gravity()
    m7_line_separation()
    m8_line_count()
    m9_reference_choice()
    m10_roll()
