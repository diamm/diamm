"""Optional real-tool pixel/ICC checks using generated TIFFs, not server images."""

import shutil
import struct
import tempfile
import unittest
from pathlib import Path

from PIL import ImageCms

from diamm.imageops import Tools
from diamm.imageops.rotation import _RasterSpec, _rotate_tiff, _run


def reference_rotation(samples: tuple[int, ...], components: int, angle: int) -> tuple[int, ...]:
    width, height = 3, 2
    rotated = [0] * len(samples)
    for y in range(height):
        for x in range(width):
            if angle == 90:
                pixel = x * height + height - 1 - y
            elif angle == 180:
                pixel = (height - 1 - y) * width + width - 1 - x
            else:
                pixel = (width - 1 - x) * height + y
            start = (y * width + x) * components
            rotated[pixel * components:(pixel + 1) * components] = samples[start:start + components]
    return tuple(rotated)


@unittest.skipUnless(
    shutil.which("gm") and shutil.which("exiftool"),
    "GraphicsMagick and ExifTool are required for real-tool TIFF tests",
)
class GraphicsMagickIntegrationTests(unittest.TestCase):
    def test_exact_8_and_16_bit_grayscale_rgb_pixels_and_icc(self):
        tools = Tools(gm=shutil.which("gm") or "gm", exiftool=shutil.which("exiftool") or "exiftool")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
            icc_file = root / "source.icc"
            icc_file.write_bytes(profile)
            for bits in (8, 16):
                for components in (1, 3):
                    samples = tuple((i * 7919 + 1) % (1 << bits) for i in range(6 * components))
                    fmt = f">{len(samples)}{'B' if bits == 8 else 'H'}"
                    raw = root / "input.raw"
                    raw.write_bytes(struct.pack(fmt, *samples))
                    source = root / "source.tif"
                    kind = "rgb" if components == 3 else "gray"
                    command = [
                        tools.gm, "convert", "-size", "3x2", "-depth", str(bits),
                        "-endian", "MSB", f"{kind}:{raw}",
                    ]
                    if components == 3:
                        command += ["-profile", icc_file]
                    _ = _run(command + ["-compress", "None", source], timeout=30)
                    for angle in (90, 180, 270):
                        with self.subTest(bits=bits, components=components, angle=angle):
                            rotated = root / "rotated.tif"
                            width, height = (3, 2) if angle == 180 else (2, 3)
                            spec = _RasterSpec(width, height, bytes([bits - 1, 1, 1]) * components)
                            _ = _rotate_tiff(
                                source, rotated, angle, spec,
                                profile if components == 3 else b"", tools, 30,
                            )
                            output = root / "output.raw"
                            _ = _run([
                                tools.gm, "convert", rotated, "-depth", str(bits),
                                "-endian", "MSB", f"{kind}:{output}",
                            ], timeout=30)
                            self.assertEqual(
                                struct.unpack(fmt, output.read_bytes()),
                                reference_rotation(samples, components, angle),
                            )
