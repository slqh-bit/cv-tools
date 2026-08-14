"""
Generate synthetic test images for the cv-tools test suite.

These stand in for the low-quality CCTV stills the toolkit targets: dark,
low-contrast, noisy frames where CLAHE and levels adjustments have visible
effect. Run from the project root:

    python samples/generate_samples.py
"""

from pathlib import Path

import cv2
import numpy as np

SAMPLES_DIR = Path(__file__).parent


def _license_plate_scene(width: int = 640, height: int = 480) -> np.ndarray:
    """A dark scene with a small high-detail region, like a plate at distance."""
    rng = np.random.default_rng(42)
    image = np.zeros((height, width, 3), dtype=np.float32)

    # Vignetted background gradient
    yy, xx = np.mgrid[0:height, 0:width]
    gradient = 40 + 30 * (yy / height) + 15 * np.sin(xx / 80.0)
    for channel in range(3):
        image[:, :, channel] = gradient

    # Slight color cast, as from sodium street lighting
    image[:, :, 0] *= 1.15
    image[:, :, 2] *= 0.85

    # Vehicle body block
    cv2.rectangle(image, (140, 200), (500, 400), (58, 60, 64), -1)

    # Plate: bright rectangle with dark characters
    cv2.rectangle(image, (270, 300), (380, 336), (120, 120, 115), -1)
    for i, char in enumerate("AB 123 CD"):
        cv2.putText(image, char, (276 + i * 12, 326),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (35, 35, 35), 1, cv2.LINE_AA)

    # Headlights
    cv2.circle(image, (185, 330), 22, (150, 148, 130), -1)
    cv2.circle(image, (455, 330), 22, (150, 148, 130), -1)

    # Sensor noise
    image += rng.normal(0, 6.0, image.shape)

    return np.clip(image, 0, 255).astype(np.uint8)


def _low_contrast_gray(width: int = 512, height: int = 512) -> np.ndarray:
    """Grayscale test chart compressed into a narrow tonal band."""
    image = np.zeros((height, width), dtype=np.float32)

    # Stepped wedge
    steps = 8
    for i in range(steps):
        x1 = i * width // steps
        x2 = (i + 1) * width // steps
        image[:height // 2, x1:x2] = 100 + i * 6

    # Concentric rings for local-contrast behaviour
    yy, xx = np.mgrid[0:height, 0:width]
    center_y, center_x = height * 3 // 4, width // 2
    radius = np.sqrt((yy - center_y) ** 2 + (xx - center_x) ** 2)
    image[height // 2:, :] = (118 + 10 * np.sin(radius / 12.0))[height // 2:, :]

    return np.clip(image, 0, 255).astype(np.uint8)


def _color_chart(width: int = 480, height: int = 320) -> np.ndarray:
    """Flat color patches for verifying that filters preserve channel order."""
    colors = [
        (200, 60, 60), (60, 200, 60), (60, 60, 200),
        (200, 200, 60), (200, 60, 200), (60, 200, 200),
        (230, 230, 230), (30, 30, 30),
    ]
    image = np.zeros((height, width, 3), dtype=np.uint8)
    patch_w = width // 4
    patch_h = height // 2
    for index, color in enumerate(colors):
        row, col = divmod(index, 4)
        y1, y2 = row * patch_h, (row + 1) * patch_h
        x1, x2 = col * patch_w, (col + 1) * patch_w
        image[y1:y2, x1:x2] = color
    return image


def _textured_scene(width: int = 480, height: int = 360) -> np.ndarray:
    """Textured scene used as the base for the forgery samples."""
    rng = np.random.default_rng(17)
    yy, xx = np.mgrid[0:height, 0:width]

    image = np.zeros((height, width, 3), dtype=np.float32)
    image[:, :, 0] = 120 + 40 * np.sin(xx / 40.0) + 20 * np.cos(yy / 55.0)
    image[:, :, 1] = 130 + 35 * np.sin((xx + yy) / 48.0)
    image[:, :, 2] = 110 + 30 * np.cos(xx / 33.0) + 25 * np.sin(yy / 29.0)

    # Scattered shapes so blocks have distinguishable structure
    for _ in range(14):
        cx, cy = int(rng.integers(40, width - 40)), int(rng.integers(40, height - 40))
        radius = int(rng.integers(8, 22))
        color = tuple(float(c) for c in rng.integers(30, 220, size=3))
        cv2.circle(image, (cx, cy), radius, color, -1)

    image += rng.normal(0, 3.0, image.shape)
    return np.clip(image, 0, 255).astype(np.uint8)


def _cloned_scene() -> np.ndarray:
    """Textured scene with one region copy-pasted to a second location."""
    image = _textured_scene()
    # Copy an 80x80 patch and paste it 190px to the right and 60px down
    patch = image[70:150, 60:140].copy()
    image[130:210, 250:330] = patch
    return image


def _periodic_noise_scene() -> np.ndarray:
    """Scene overlaid with a strong diagonal sinusoid, as from interference."""
    image = _textured_scene().astype(np.float32)
    height, width = image.shape[:2]
    yy, xx = np.mgrid[0:height, 0:width]

    # A single high-frequency sinusoid shows up as one peak pair in the spectrum
    pattern = 34.0 * np.sin(2 * np.pi * (xx * 0.22 + yy * 0.14))
    image += pattern[:, :, np.newaxis]

    return np.clip(image, 0, 255).astype(np.uint8)


def _write_sequence(path: Path, frames: int = 24) -> None:
    """
    Write a short AVI of a static noisy scene with one object crossing it.

    Averaging the frames should suppress the noise; taking the median should
    remove the moving object altogether.
    """
    base = _textured_scene(320, 240)
    height, width = base.shape[:2]
    rng = np.random.default_rng(23)

    writer = cv2.VideoWriter(
        str(path), cv2.VideoWriter_fourcc(*'MJPG'), 10, (width, height)
    )
    if not writer.isOpened():
        raise RuntimeError(f"Could not open video writer for {path}")

    try:
        for index in range(frames):
            frame = base.astype(np.float32) + rng.normal(0, 18.0, base.shape)
            frame = np.clip(frame, 0, 255).astype(np.uint8)
            # A bright block tracking left to right across the scene
            x = int(10 + index * (width - 60) / max(1, frames - 1))
            cv2.rectangle(frame, (x, 90), (x + 40, 140), (250, 250, 250), -1)
            writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    finally:
        writer.release()


def generate_all(output_dir: Path = SAMPLES_DIR) -> list:
    """Write every sample image and the sample video. Returns written paths."""
    output_dir.mkdir(parents=True, exist_ok=True)

    samples = {
        'cctv_dark.png': _license_plate_scene(),
        'low_contrast_gray.png': _low_contrast_gray(),
        'color_chart.png': _color_chart(),
        'cloned_region.png': _cloned_scene(),
        'periodic_noise.png': _periodic_noise_scene(),
    }

    written = []
    for name, image in samples.items():
        path = output_dir / name
        # Samples are authored in RGB; cv2.imwrite expects BGR
        out = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) if image.ndim == 3 else image
        cv2.imwrite(str(path), out)
        written.append(path)
        print(f"Wrote {path.name}  {image.shape}")

    # A JPEG original, since ELA is meaningless on anything else
    jpeg_path = output_dir / 'cloned_region.jpg'
    cv2.imwrite(str(jpeg_path), cv2.cvtColor(_cloned_scene(), cv2.COLOR_RGB2BGR),
                [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    written.append(jpeg_path)
    print(f"Wrote {jpeg_path.name}  (JPEG quality 92, for ELA)")

    video_path = output_dir / 'sequence.avi'
    _write_sequence(video_path)
    written.append(video_path)
    print(f"Wrote {video_path.name}  (24 frames, static scene + moving object)")

    return written


if __name__ == '__main__':
    generate_all()
