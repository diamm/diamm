"""Decode -> lossless TIFF -> GraphicsMagick rotate -> Part 1 JPEG 2000.

No shell interpolation, image-sized Python buffers, HTTP framework, shared
working directories, or process-wide cwd/environment changes.
"""

import json
import logging
import os
import re
import shutil
import stat
import struct
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Self

from django.conf import settings

type PathInput = str | os.PathLike[str]
# ExifTool values include scalars, arrays and nested structured XMP objects.
type Metadata = dict[str, Any]
type ContainerHeader = tuple[int, int, int, bytes]
type FileFingerprint = tuple[int, int, int, int]

log = logging.getLogger("diamm")
CONTAINERS: set[str] = {".jp2", ".jpx"}


class RotationError(RuntimeError):
    """An operation failed; a staged output was not published."""


def _path_text(value: PathInput) -> str:
    if isinstance(value, str):
        return value
    return os.fspath(value)


def check_rotation_access(path: Path) -> Path:
    """Advisory permission checks; actual filesystem operations may still fail."""
    effective_ids = os.access in os.supports_effective_ids
    if not os.access(path, os.R_OK, effective_ids=effective_ids):
        raise RotationError(
            f"No read access to image file for the current process account: {path}"
        )
    if not os.access(path.parent, os.W_OK | os.X_OK, effective_ids=effective_ids):
        raise RotationError(
            f"No write/search access to image directory for the current process account: {path.parent}"
        )
    return path


@dataclass(frozen=True)
class Tools:
    """Trusted executable configuration, not settings supplied by web clients."""

    expand: str = "kdu_expand"
    compress: str = "kdu_compress"
    gm: str = "gm"
    exiftool: str = "exiftool"

    def validate(self) -> Self:
        for executable in (self.expand, self.compress, self.gm, self.exiftool):
            if shutil.which(executable) is None:
                raise RotationError(
                    f"executable not found or not executable: {executable}; "
                    "check the configured path and execute permission"
                )
        return self


@dataclass(frozen=True)
class RotationResult:
    input_path: Path
    output_path: Path
    rotation: int
    width: int
    height: int


@dataclass(frozen=True)
class _RasterSpec:
    width: int
    height: int
    samples: bytes

    @property
    def components(self) -> int:
        return len(self.samples) // 3

    @property
    def bits(self) -> int:
        return (self.samples[0] & 0x7F) + 1


def _run(command: Sequence[PathInput], *, timeout: float) -> bytes:
    argv = [_path_text(it) for it in command]
    try:
        result = subprocess.run(  # noqa: S603 -- executable configuration is trusted.
            argv,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise RotationError(
            f"{argv[0]} exceeded the {timeout:g}-second stage timeout"
        ) from error
    except OSError as error:
        raise RotationError(f"cannot launch {argv[0]}: {error}") from error
    if result.returncode:
        details = (
            (result.stderr + b"\n" + result.stdout)
            .decode("utf-8", errors="replace")
            .strip()
        )
        raise RotationError(f"{argv[0]} failed (exit {result.returncode}):\n{details}")
    return result.stdout


def _json_record(data: bytes) -> Metadata:
    try:
        records = json.loads(data)
    except (ValueError, UnicodeError) as error:
        raise RotationError(f"invalid ExifTool JSON: {error}") from error
    if (
        not isinstance(records, list)
        or len(records) != 1
        or not isinstance(records[0], dict)
    ):
        raise RotationError("expected one ExifTool JSON record")
    record = records[0]
    if any(key.rsplit(":", 1)[-1] in ("Error", "Warning") for key in record):
        raise RotationError(
            "ExifTool reported a metadata warning/error; refusing automatic replacement"
        )
    return {key: value for key, value in record.items() if key != "SourceFile"}


def _inspect(path: Path, tools: Tools, timeout: float) -> Metadata:
    return _json_record(
        _run(
            [
                tools.exiftool,
                "-j",
                "-n",
                "-FileType",
                "-ImageWidth",
                "-ImageHeight",
                "-NumberOfComponents",
                "-BitsPerComponent",
                "-BitsPerSample",
                "-SamplesPerPixel",
                "-SampleFormat",
                "-Orientation",
                "-XResolution",
                "-YResolution",
                "-ResolutionUnit",
                path,
            ],
            timeout=timeout,
        )
    )


def _metadata(path: Path, tools: Tools, timeout: float) -> Metadata:
    return _json_record(
        _run(
            [
                tools.exiftool,
                "-j",
                "-G1",
                "-n",
                "-struct",
                "-a",
                "-EXIF:All",
                "-XMP:All",
                "-IPTC:All",
                path,
            ],
            timeout=timeout,
        )
    )


def _icc(path: Path, tools: Tools, timeout: float) -> bytes:
    return _run([tools.exiftool, "-b", "-ICC_Profile", path], timeout=timeout)


def _check_icc(path: Path, expected: bytes, tools: Tools, timeout: float) -> Path:
    if _icc(path, tools, timeout) != expected:
        raise RotationError(f"ICC profile was lost or changed in {path.name}")
    return path


def _container_header(path: Path) -> ContainerHeader:
    """Inspect the first SIZ, without decoding pixels or loading the codestream.

    Reject multi-image/fragmented compositions rather than silently rotate only
    their first layer. Nonempty single-layer headers are left to Kakadu.
    """
    with path.open("rb") as stream:
        start, end = _find_codestream(stream, os.fstat(stream.fileno()).st_size)
        data = _read_siz(stream, start, end)
    return _parse_siz(data)


def _read_box(stream: BinaryIO, position: int, size: int) -> tuple[bytes, int, int]:
    """Return a box's type, payload start and end without reading its payload."""
    if size - position < 8:
        raise RotationError("truncated JPEG 2000 box header")
    stream.seek(position)
    header = stream.read(8)
    if len(header) != 8:
        raise RotationError("truncated JPEG 2000 box header")
    length, kind = struct.unpack(">I4s", header)
    header_length = 8
    if length == 1:
        extended_length = stream.read(min(8, size - position - 8))
        if len(extended_length) != 8:
            raise RotationError("truncated extended box header")
        length = struct.unpack(">Q", extended_length)[0]
        header_length = 16
    elif length == 0:
        length = size - position
    if not header_length <= length <= size - position:
        raise RotationError("invalid JPEG 2000 box length")
    return kind, position + header_length, position + length


def _find_codestream(stream: BinaryIO, size: int) -> tuple[int, int]:
    """Scan box headers and reject unsupported multi-image compositions."""
    position, layer_headers, stream_headers = 0, 0, 0
    codestreams: list[tuple[int, int]] = []
    while position < size:
        kind, start, position = _read_box(stream, position, size)
        if kind in {b"ftbl", b"dtbl", b"comp", b"copt", b"inst"}:
            raise RotationError(
                "fragmented or composed/multi-frame JPEG 2000 is not supported"
            )
        if kind == b"jp2c":
            codestreams.append((start, position))
        layer_headers += kind == b"jplh"
        stream_headers += kind == b"jpch"
    if len(codestreams) != 1 or layer_headers > 1 or stream_headers > 1:
        raise RotationError(
            "only a single contiguous codestream / single image is supported"
        )
    return codestreams[0]


def _read_siz(stream: BinaryIO, start: int, end: int) -> bytes:
    """Read only the bounded SIZ segment, never the pixel codestream."""
    stream.seek(start)
    header = stream.read(min(42, end - start))
    if len(header) != 42 or header[:4] != b"\xffO\xffQ":
        raise RotationError("missing JPEG 2000 SOC/SIZ header")
    length = struct.unpack_from(">H", header, 4)[0]
    if length < 38 or start + 4 + length > end:
        raise RotationError("invalid JPEG 2000 SIZ component table")
    components = stream.read(length - 38)
    if len(components) != length - 38:
        raise RotationError("invalid JPEG 2000 SIZ component table")
    return header + components


def _parse_siz(data: bytes) -> ContainerHeader:
    """Validate the in-memory SIZ data independently of the open file."""
    if len(data) < 42 or data[:4] != b"\xffO\xffQ":
        raise RotationError("missing JPEG 2000 SOC/SIZ header")
    length, profile = struct.unpack_from(">HH", data, 4)
    xs, ys, xo, yo = struct.unpack_from(">4I", data, 8)
    count = struct.unpack_from(">H", data, 40)[0]
    if count <= 0 or length != 38 + 3 * count or len(data) != 4 + length:
        raise RotationError("invalid JPEG 2000 SIZ component table")
    if xs <= xo or ys <= yo:
        raise RotationError("invalid JPEG 2000 geometry")
    return xs - xo, ys - yo, profile, data[42:]


def _check_tiff(
    path: Path, spec: _RasterSpec, tools: Tools, timeout: float
) -> Metadata:
    info = _inspect(path, tools, timeout)
    if info.get("FileType") != "TIFF":
        raise RotationError(f"{path.name} is not a TIFF")
    if (info.get("ImageWidth"), info.get("ImageHeight")) != (spec.width, spec.height):
        raise RotationError(f"unexpected TIFF dimensions in {path.name}")
    if info.get("SamplesPerPixel", 1) != spec.components:
        raise RotationError("TIFF component count changed")
    sample_bits = info.get("BitsPerSample")
    if isinstance(sample_bits, str):
        try:
            sample_bits = [int(value) for value in sample_bits.split()]
        except ValueError as error:
            raise RotationError("invalid TIFF sample precision metadata") from error
    elif isinstance(sample_bits, int):
        sample_bits = [sample_bits]
    if (
        not isinstance(sample_bits, list)
        or not sample_bits
        or any(value != spec.bits for value in sample_bits)
    ):
        raise RotationError("TIFF sample precision changed")
    sample_format = info.get("SampleFormat", 1)
    if isinstance(sample_format, str):
        try:
            sample_format = [int(value) for value in sample_format.split()]
        except ValueError as error:
            raise RotationError("invalid TIFF sample format metadata") from error
    if isinstance(sample_format, int):
        sample_format = [sample_format]
    if not isinstance(sample_format, list) or any(
        value != 1 for value in sample_format
    ):
        raise RotationError("TIFF samples are not unsigned integers")
    return info


def _expected_metadata(
    metadata: Mapping[str, Any], width: int, height: int, rotation: int
) -> Metadata:
    expected = dict(metadata)
    for key in expected:
        tag = key.rsplit(":", 1)[-1]
        if tag in {"ImageWidth", "ExifImageWidth", "PixelXDimension"}:
            expected[key] = width
        elif tag in {"ImageHeight", "ExifImageHeight", "PixelYDimension"}:
            expected[key] = height
        elif tag == "Orientation":
            expected[key] = 1
    if rotation in (90, 270):
        for key in expected:
            if key.endswith(":XResolution"):
                y = key[: -len("XResolution")] + "YResolution"
                if y not in expected:
                    raise RotationError("incomplete EXIF/XMP resolution metadata")
                expected[key], expected[y] = expected[y], expected[key]
    return expected


def _copy_metadata(
    source: Path,
    output: Path,
    original: Mapping[str, Any],
    expected: Mapping[str, Any],
    tools: Tools,
    timeout: float,
) -> Path:
    command: list[PathInput] = [
        tools.exiftool,
        "-overwrite_original",
        "-TagsFromFile",
        source,
        "-EXIF:All",
        "-XMP:All",
        "-IPTC:All",
    ]
    for key, value in expected.items():
        if original[key] != value:
            # Names are supplied by ExifTool, not a user-provided command line.
            command.append(f"-{key}={value}")
    if original:
        _run(command + [output], timeout=timeout)
        restored = _metadata(output, tools, timeout)
        missing = sorted(
            key
            for key, value in expected.items()
            if key not in restored or restored[key] != value
        )
        if missing:
            raise RotationError(
                "descriptive metadata could not be preserved: " + ", ".join(missing)
            )
    return output


def _fingerprint(path: Path) -> FileFingerprint:
    info = path.stat()
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def _decode_tiff(
    source: Path,
    decoded: Path,
    spec: _RasterSpec,
    profile: bytes,
    tools: Tools,
    timeout: float,
) -> tuple[Path, Metadata]:
    _run([tools.expand, "-i", source, "-o", decoded], timeout=timeout)
    info = _check_tiff(decoded, spec, tools, timeout)
    if _icc(decoded, tools, timeout) != profile:
        icc_file = decoded.parent / "source.icc"
        icc_file.write_bytes(profile)
        assignment = f"-ICC_Profile<={icc_file}" if profile else "-ICC_Profile="
        _run(
            [tools.exiftool, "-overwrite_original", assignment, decoded],
            timeout=timeout,
        )
    return _check_icc(decoded, profile, tools, timeout), info


def _restore_tiff_density(
    path: Path, info: Metadata, rotation: int, tools: Tools, timeout: float
) -> Path:
    if "XResolution" not in info or "YResolution" not in info:
        return path
    # Restore the original density explicitly, exchanging axes for quarter-turns.
    x_key, y_key = (
        ("YResolution", "XResolution")
        if rotation in (90, 270)
        else ("XResolution", "YResolution")
    )
    _run(
        [
            tools.exiftool,
            "-overwrite_original",
            f"-XResolution={info[x_key]}",
            f"-YResolution={info[y_key]}",
            path,
        ],
        timeout=timeout,
    )
    return path


def _rotate_tiff(
    decoded: Path,
    rotated: Path,
    rotation: int,
    spec: _RasterSpec,
    profile: bytes,
    tools: Tools,
    timeout: float,
) -> Path:
    if spec.bits == 16:
        version = _run([tools.gm, "version"], timeout=timeout).decode("utf-8", errors="replace")
        quantum = re.search(r"(?im)^\s*Quantum Depth\s*:?\s*(\d+)\b", version)
        if quantum is None or int(quantum[1]) < 16:
            raise RotationError("16-bit images require a GraphicsMagick Q16 or higher build")
    _run(
        [
            tools.gm,
            "convert",
            decoded,
            "-rotate", str(rotation),
            "-type", "TrueColor" if spec.components == 3 else "Grayscale",
            "-depth", str(spec.bits),
            "-compress", "None",
            rotated,
        ],
        timeout=timeout,
    )
    _ = _check_tiff(rotated, spec, tools, timeout)
    return _check_icc(rotated, profile, tools, timeout)


def _encode_jpeg2000(rotated: Path, staged: Path, tools: Tools, timeout: float) -> Path:
    _run(
        [
            tools.compress,
            "-i",
            rotated,
            "-o",
            staged,
            "Sprofile=PROFILE2",
            "Creversible=yes",
            "Clevels=5",
            "Cblk={64,64}",
            "Cprecincts={256,256},{256,256},{128,128}",
            "Cuse_sop=yes",
            "Corder=LRCP",
            "ORGgen_plt=yes",
            "ORGtparts=R",
            "-rate",
            "-,1,0.5,0.25",
        ],
        timeout=timeout,
    )
    if not staged.is_file() or staged.stat().st_size <= 0:
        raise RotationError("encoder produced no output")
    return staged


def _check_jpeg2000(
    path: Path, spec: _RasterSpec, profile: bytes, tools: Tools, timeout: float
) -> Path:
    width, height, coding_profile, samples = _container_header(path)
    if (width, height) != (spec.width, spec.height) or samples != spec.samples:
        raise RotationError(
            "JPEG 2000 output dimensions or component precision changed"
        )
    if coding_profile != 0:
        raise RotationError("encoder did not produce unrestricted Part 1 JPEG 2000")
    info = _inspect(path, tools, timeout)
    expected_type = "JP2" if path.suffix.lower() == ".jp2" else "JPX"
    if info.get("FileType") != expected_type:
        raise RotationError("encoded container does not match the output suffix")
    return _check_icc(path, profile, tools, timeout)


def _publish_output(
    staged: Path,
    source: Path,
    output: Path,
    original_fingerprint: FileFingerprint,
    original_mode: int,
) -> Path:
    if _fingerprint(source) != original_fingerprint:
        raise RotationError(
            "input changed during processing; destination was not replaced"
        )
    try:
        if source == output:
            staged.chmod(original_mode)
            os.replace(staged, output)
        else:
            # No-clobber publication, even if OUTPUT appeared while encoding.
            os.link(staged, output)
    except OSError as error:
        raise RotationError(f"cannot publish output {output}: {error}") from error
    return output


def rotate_image(
    input_path: PathInput,
    rotation: int,
    output_path: PathInput | None = None,
    *,
    tools: Tools | None = None,
    timeout: float = 600,
    max_pixels: int = 500_000_000,
) -> RotationResult:
    """Rotate a single image clockwise, preserving exact unsigned 8/16-bit samples.

    This is blocking work; web applications should call it from a bounded worker
    queue and authorize input/output paths independently. Each call has its own
    private workspace. A separate output must not exist. With no output, atomic
    replacement occurs only after all checks succeed. Exceptions leave the
    original/destination unchanged before publication.

    Raises RotationError for validation/tool failures and publication errors.
    Other filesystem errors propagate as OSError with their original context.
    """
    if type(rotation) is not int or rotation not in (90, 180, 270):
        raise RotationError("rotation must be 90, 180, or 270 clockwise degrees")
    if not (timeout > 0 and max_pixels > 0):
        raise RotationError("timeout and max_pixels must be positive")
    source = Path(os.path.abspath(os.path.expanduser(_path_text(input_path))))
    if source.is_symlink():
        raise RotationError("symbolic-link input is not supported")
    if not source.is_file():
        raise RotationError(f"input is not a regular file: {source}")
    source = source.resolve()
    if output_path is None:
        output = source
    else:
        output_text = _path_text(output_path)
        if not output_text:
            raise RotationError("output filename must not be empty")
        output = Path(os.path.abspath(os.path.expanduser(output_text)))
        if not output.parent.is_dir():
            raise RotationError("output directory does not exist")
        output = output.parent.resolve() / output.name
    if (
        source.suffix.lower() not in CONTAINERS
        or output.suffix.lower() not in CONTAINERS
    ):
        raise RotationError("input/output suffix must be .jp2, .jpx, or .jpf")
    in_place = source == output
    if not in_place and (output.exists() or output.is_symlink()):
        raise RotationError(f"output already exists: {output}")
    config = (
        tools
        or Tools(
            expand=settings.KDU_EXPAND,
            compress=settings.KDU_COMPRESS,
            gm=settings.GM,
            exiftool=settings.EXIFTOOL,
        )
    ).validate()
    original_fingerprint = _fingerprint(source)
    original_mode = stat.S_IMODE(source.stat().st_mode)

    width, height, _, samples = _container_header(source)
    components = len(samples) // 3
    bits = (samples[0] & 0x7F) + 1
    if width * height > max_pixels:
        raise RotationError(f"image exceeds the {max_pixels}-pixel limit")
    if components not in (1, 3):
        raise RotationError("only grayscale/RGB images without alpha are supported")
    if bits not in (8, 16) or any(
        samples[i] != bits - 1 for i in range(0, len(samples), 3)
    ):
        raise RotationError(
            "only uniform unsigned 8-bit or 16-bit components are supported"
        )
    if any(
        value != 1
        for i in range(0, len(samples), 3)
        for value in samples[i + 1 : i + 3]
    ):
        raise RotationError("subsampled components are not supported")
    info = _inspect(source, config, timeout)
    if info.get("FileType") not in ("JP2", "JPX", "JPF"):
        raise RotationError("input is not JP2/JPX")
    if (info.get("ImageWidth"), info.get("ImageHeight")) != (width, height):
        raise RotationError("ExifTool dimensions disagree with JPEG 2000 header")
    metadata = _metadata(source, config, timeout)
    if any(
        value != 1
        for key, value in metadata.items()
        if key.rsplit(":", 1)[-1] == "Orientation"
    ):
        raise RotationError("non-normal stored Orientation requires explicit handling")
    profile = _icc(source, config, timeout)
    result_width, result_height = (
        (height, width) if rotation in (90, 270) else (width, height)
    )
    expected_metadata = _expected_metadata(
        metadata, result_width, result_height, rotation
    )
    source_spec = _RasterSpec(width, height, samples)
    output_spec = _RasterSpec(result_width, result_height, samples)

    with tempfile.TemporaryDirectory(
        prefix=".diamm-imageops-", dir=output.parent
    ) as directory:
        work = Path(directory)
        decoded, rotated = work / "decoded.tif", work / "rotated.tif"
        staged = work / ("output" + output.suffix.lower())
        log.info("Decoding JPEG 2000 to lossless TIFF: %s", source)
        decoded, tiff_info = _decode_tiff(
            source, decoded, source_spec, profile, config, timeout
        )
        log.info("Rotating TIFF %s degrees with GraphicsMagick: %s", rotation, source)
        rotated = _rotate_tiff(
            decoded, rotated, rotation, output_spec, profile, config, timeout
        )
        rotated = _restore_tiff_density(rotated, tiff_info, rotation, config, timeout)
        log.info("Encoding lossless Part 1 JPEG 2000: %s", source)
        staged = _encode_jpeg2000(rotated, staged, config, timeout)
        staged = _check_jpeg2000(staged, output_spec, profile, config, timeout)
        log.info("Copying descriptive metadata: %s", source)
        staged = _copy_metadata(
            source, staged, metadata, expected_metadata, config, timeout
        )
        staged = _check_jpeg2000(staged, output_spec, profile, config, timeout)
        published = _publish_output(
            staged, source, output, original_fingerprint, original_mode
        )
    return RotationResult(source, published, rotation, result_width, result_height)
