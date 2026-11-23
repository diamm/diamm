"""Fast pipeline/safety tests. Real-tool tests are in test_integration.py."""

import ast
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from diamm.imageops import RotationError, Tools, plan_rotations, rotate_image
from diamm.imageops import rotation as implementation


@dataclass(frozen=True)
class FilesystemPath(os.PathLike[str]):
    path: str

    def __fspath__(self) -> str:
        return self.path


def container(width=48, height=33, bits=8, components=3, profile=0):
    def box(kind, payload):
        return struct.pack(">I4s", len(payload)+8, kind) + payload
    siz = (b"\xffO\xffQ" + struct.pack(">HH8IH", 38+3*components, profile,
           width, height, 0, 0, width, height, 0, 0, components)
           + bytes([bits-1, 1, 1])*components + b"\xff\xd9")
    return box(b"jP  ", b"\r\n\x87\n") + box(b"jp2c", siz)


class ContainerHeaderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "header.jpx"
        self.siz = container()[20:-2]
        self.expected = (48, 33, 0, bytes([7, 1, 1]) * 3)

    def parse_after_close(self, data):
        self.assertTrue(self.stream.closed)
        return self.parse_siz(data)

    def test_geometry_is_parsed_after_file_is_closed(self):
        self.path.write_bytes(container())
        self.stream = self.path.open("rb")
        self.parse_siz = implementation._parse_siz
        with patch.object(Path, "open", return_value=self.stream), \
                patch.object(implementation, "_parse_siz", side_effect=self.parse_after_close):
            self.assertEqual(implementation._container_header(self.path), self.expected)

    def test_standard_extended_and_end_of_file_boxes(self):
        payload = self.siz + b"\xff\xd9"
        for header in (
            struct.pack(">I4s", len(payload) + 8, b"jp2c"),
            struct.pack(">I4sQ", 1, b"jp2c", len(payload) + 16),
            struct.pack(">I4s", 0, b"jp2c"),
        ):
            with self.subTest(header=header):
                self.path.write_bytes(container()[:12] + header + payload)
                self.assertEqual(implementation._container_header(self.path), self.expected)

    def test_invalid_box_headers_are_rejected(self):
        for data in (
            b"short",
            struct.pack(">I4s", 1, b"jp2c") + b"short",
            struct.pack(">I4s", 7, b"jp2c"),
            struct.pack(">I4s", 100, b"jp2c"),
            container()[:12],
        ):
            with self.subTest(data=data):
                self.path.write_bytes(data)
                with self.assertRaises(RotationError):
                    implementation._container_header(self.path)

    def test_compositions_and_multiple_codestreams_are_rejected(self):
        for kind in (b"ftbl", b"dtbl", b"comp", b"copt", b"inst"):
            with self.subTest(kind=kind):
                self.path.write_bytes(container() + struct.pack(">I4s", 8, kind))
                with self.assertRaisesRegex(RotationError, "fragmented or composed"):
                    implementation._container_header(self.path)
        for extra in (
            container()[12:],
            struct.pack(">I4s", 8, b"jplh") * 2,
            struct.pack(">I4s", 8, b"jpch") * 2,
        ):
            with self.subTest(extra=extra):
                self.path.write_bytes(container() + extra)
                with self.assertRaisesRegex(RotationError, "single contiguous"):
                    implementation._container_header(self.path)

    def test_invalid_siz_data_is_rejected_without_a_file(self):
        invalid = [
            b"short", b"xxxx" + self.siz[4:], self.siz[:-1],
            self.siz[:40] + b"\x00\x00" + self.siz[42:],
            self.siz[:40] + b"\x00\x04" + self.siz[42:],
            self.siz[:8] + b"\x00\x00\x00\x00" + self.siz[12:],
        ]
        for data in invalid:
            with self.subTest(data=data):
                with self.assertRaises(RotationError):
                    implementation._parse_siz(data)

    def test_siz_read_cannot_cross_codestream_boundary(self):
        for payload in (self.siz[:20], self.siz[:-1], self.siz[:4] + b"\x00\x25" + self.siz[6:]):
            with self.subTest(payload=payload):
                self.path.write_bytes(struct.pack(">I4s", len(payload) + 8, b"jp2c") + payload)
                with self.assertRaises(RotationError):
                    implementation._container_header(self.path)

    def test_pixel_payload_is_not_read(self):
        size = 1_000_000
        with self.path.open("wb") as output:
            output.write(struct.pack(">I4s", size, b"jp2c") + self.siz)
            output.truncate(size)
        stream = self.path.open("rb")
        tracked = MagicMock(wraps=stream)
        tracked.__enter__.return_value = tracked
        tracked.__exit__.side_effect = stream.__exit__
        with patch.object(Path, "open", return_value=tracked):
            self.assertEqual(implementation._container_header(self.path), self.expected)
        reads = [call.args[0] for call in tracked.read.call_args_list]
        self.assertEqual(reads, [8, 42, 9])
        self.assertTrue(stream.closed)


class RotationTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name).resolve()
        self.source = self.root / "source image.jpx"
        self.original = container()
        self.source.write_bytes(self.original)
        self.tools = Tools()
        self.calls = []
        self.angle = 180
        self.failure = None
        self.callback = None
        self.metadata = {"XMP-dc:Rights": "Original rights",
                         "XMP-dc:Creator": ["DIAMM"], "ExifIFD:ExifImageWidth": 48,
                         "ExifIFD:ExifImageHeight": 33}
        self.restored = {}
        validate = patch.object(Tools, "validate", autospec=True, side_effect=lambda tools: tools)
        validate.start()
        self.addCleanup(validate.stop)
        run = patch.object(implementation, "_run", side_effect=self.run_tool)
        run.start()
        self.addCleanup(run.stop)

    def run_tool(self, command, *, timeout):
        args = [str(arg) for arg in command]
        self.calls.append(args)
        tool = Path(args[0]).name
        if tool in ("kdu_expand", "kdu_compress"):
            destination = Path(args[args.index("-o")+1])
            if self.failure == tool:
                destination.write_bytes(b"partial")
                raise RotationError("injected tool failure")
            if tool == "kdu_expand":
                destination.write_bytes(b"TIFF")
            else:
                w, h = (33, 48) if self.angle in (90, 270) else (48, 33)
                destination.write_bytes(container(w, h, profile=0x8000
                                                  if self.failure == "part2" else 0))
                if self.callback:
                    self.callback()
            return b""
        if tool == "gm":
            if args[1] == "version":
                return b"Feature Support:\n  Quantum Depth 16\n"
            if self.failure == "gm":
                raise RotationError("injected GraphicsMagick failure")
            self.assertEqual(args[1], "convert")
            self.assertEqual(args[args.index("-rotate") + 1], str(self.angle))
            self.assertEqual(args[args.index("-compress") + 1], "None")
            self.assertEqual(args[args.index("-type") + 1], "TrueColor")
            self.assertEqual(args[args.index("-depth") + 1], "8")
            Path(args[-1]).write_bytes(b"TIFF rotated")
            return b""
        self.assertEqual(tool, "exiftool")
        path = Path(args[-1])
        output = path.name.startswith("output.")
        if "-b" in args:
            return b"changed" if self.failure == "icc" and output else b"exact ICC bytes"
        if "-j" in args:
            if "-G1" in args:
                record = (self.restored if output else self.metadata)
                if self.failure == "metadata" and output:
                    record = {}
                return json.dumps([{"SourceFile": str(path), **record}]).encode()
            if path.suffix == ".tif":
                turned = path.name == "rotated.tif" and self.angle in (90, 270)
                w, h = (33, 48) if turned else (48, 33)
                return json.dumps([dict(
                    FileType="TIFF", ImageWidth=w, ImageHeight=h, SamplesPerPixel=3,
                    BitsPerSample="16 16 16" if self.failure == "precision" else "8 8 8",
                    SampleFormat="1 1 1", XResolution=100, YResolution=200,
                )]).encode()
            turned = output and self.angle in (90, 270)
            w, h = (33, 48) if turned else (48, 33)
            return json.dumps([dict(FileType="JPX", ImageWidth=w, ImageHeight=h)]).encode()
        if "-TagsFromFile" in args:
            self.restored = dict(self.metadata)
            for argument in args:
                if argument.startswith("-") and "=" in argument:
                    key, value = argument[1:].split("=", 1)
                    self.restored[key] = int(value) if value.isdigit() else value
        return b"1 image files updated"

    def assert_clean(self):
        self.assertEqual(list(self.root.glob(".diamm-imageops-*")), [])

    def test_all_angles_pipeline_preserves_original(self):
        for angle in (90, 180, 270):
            with self.subTest(angle=angle):
                self.angle = angle
                result = rotate_image(self.source, angle, self.root/f"new-{angle}.jpx",
                                      tools=self.tools)
                self.assertEqual(self.source.read_bytes(), self.original)
                self.assertEqual((result.width, result.height),
                                 (33, 48) if angle != 180 else (48, 33))
                self.assertTrue(result.output_path.exists())
                self.assert_clean()
        commands = [args for args in self.calls if args[0] == "kdu_compress"]
        self.assertTrue(all("Creversible=yes" in cmd and "Sprofile=PROFILE2" in cmd
                            and cmd[cmd.index("-rate")+1] == "-,1,0.5,0.25" for cmd in commands))

    def test_pipeline_stages_return_their_output_artifacts(self):
        spec = implementation._RasterSpec(48, 33, bytes([7, 1, 1]) * 3)
        profile = b"exact ICC bytes"
        decoded, info = implementation._decode_tiff(
            self.source, self.root/"decoded.tif", spec, profile, self.tools, 600)
        self.assertEqual(decoded, self.root/"decoded.tif")
        self.assertEqual(info["ImageWidth"], 48)
        rotated = implementation._rotate_tiff(
            decoded, self.root/"rotated.tif", 180, spec, profile, self.tools, 600)
        self.assertEqual(rotated, self.root/"rotated.tif")
        self.assertEqual(implementation._restore_tiff_density(
            rotated, info, 180, self.tools, 600), rotated)
        self.assertEqual(implementation._restore_tiff_density(
            rotated, {}, 180, self.tools, 600), rotated)
        encoded = implementation._encode_jpeg2000(
            rotated, self.root/"output.jpx", self.tools, 600)
        self.assertEqual(encoded, self.root/"output.jpx")
        self.assertEqual(implementation._check_jpeg2000(
            encoded, spec, profile, self.tools, 600), encoded)
        self.assertEqual(implementation._copy_metadata(
            self.source, encoded, self.metadata, self.metadata, self.tools, 600), encoded)
        output = self.root/"published.jpx"
        self.assertEqual(implementation._publish_output(
            encoded, self.source, output, implementation._fingerprint(self.source), 0o640), output)
        self.assertTrue(output.exists())

    def test_in_place_permission_bits(self):
        self.source.chmod(0o640)
        result = rotate_image(self.source, 180, tools=self.tools)
        self.assertEqual(result.output_path, self.source)
        self.assertEqual(self.source.stat().st_mode & 0o777, 0o640)
        self.assert_clean()

    def test_explicit_same_path_is_in_place(self):
        result = rotate_image(self.source, 180, self.source, tools=self.tools)
        self.assertEqual(result.output_path, self.source)
        self.assert_clean()

    def test_each_failure_preserves_original_and_cleans_up(self):
        for failure in ("kdu_expand", "gm", "kdu_compress", "part2",
                        "icc", "metadata", "precision"):
            self.failure = failure
            with self.subTest(failure=failure), self.assertRaises(RotationError):
                rotate_image(self.source, 180, tools=self.tools)
            self.assertEqual(self.source.read_bytes(), self.original)
            self.assert_clean()

    def test_existing_output_not_overwritten(self):
        output = self.root / "exists.jpx"
        output.write_bytes(b"keep")
        with self.assertRaises(RotationError):
            rotate_image(self.source, 180, output, tools=self.tools)
        self.assertEqual(output.read_bytes(), b"keep")
        self.assertEqual(self.calls, [])

    def test_racing_output_not_overwritten(self):
        output = self.root / "race.jpx"
        self.callback = lambda: output.write_bytes(b"competitor")
        with self.assertRaises(RotationError):
            rotate_image(self.source, 180, output, tools=self.tools)
        self.assertEqual(output.read_bytes(), b"competitor")
        self.assert_clean()

    def test_changed_input_not_replaced(self):
        self.callback = lambda: self.source.write_bytes(b"new external version")
        with self.assertRaisesRegex(RotationError, "input changed"):
            rotate_image(self.source, 180, tools=self.tools)
        self.assertEqual(self.source.read_bytes(), b"new external version")
        self.assert_clean()

    def test_invalid_angles(self):
        for angle in (0, 45, 360, True, "180", 90.0):
            with self.assertRaises(RotationError):
                rotate_image(self.source, angle, tools=self.tools)
        self.assertEqual(self.calls, [])

    def test_missing_input_and_output_directory(self):
        with self.assertRaises(RotationError):
            rotate_image(self.root/"missing.jpx", 180, tools=self.tools)
        with self.assertRaises(RotationError):
            rotate_image(self.source, 180, self.root/"missing"/"out.jpx", tools=self.tools)

    def test_symlinks_and_dangling_output(self):
        link = self.root/"link.jpx"
        link.symlink_to(self.source)
        with self.assertRaises(RotationError):
            rotate_image(link, 180, tools=self.tools)
        output = self.root/"dangling.jpx"
        output.symlink_to(self.root/"missing")
        with self.assertRaises(RotationError):
            rotate_image(self.source, 180, output, tools=self.tools)

    def test_unsupported_precision_components_and_pixel_limit(self):
        for data in (container(bits=12), container(components=4)):
            self.source.write_bytes(data)
            with self.assertRaises(RotationError):
                rotate_image(self.source, 180, tools=self.tools)
        self.source.write_bytes(self.original)
        with self.assertRaises(RotationError):
            rotate_image(self.source, 180, max_pixels=10, tools=self.tools)

    def test_stored_orientation_rejected(self):
        self.metadata["IFD0:Orientation"] = 3
        with self.assertRaisesRegex(RotationError, "Orientation"):
            rotate_image(self.source, 180, tools=self.tools)
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_pipeline_logs_include_original_image_path(self):
        with self.assertLogs("diamm", level="INFO") as logs:
            rotate_image(self.source, 180, tools=self.tools)
        self.assertEqual(len(logs.records), 4)
        for record in logs.records:
            self.assertEqual(record.name, "diamm")
            self.assertIn(str(self.source), record.getMessage())

    def test_filesystem_read_error_preserves_original_exception(self):
        error = PermissionError("source cannot be read")
        with patch.object(implementation, "_container_header", side_effect=error):
            with self.assertRaises(PermissionError) as caught:
                rotate_image(self.source, 180, tools=self.tools)
        self.assertIs(caught.exception, error)
        self.assertEqual(self.source.read_bytes(), self.original)


class GraphicsMagickTests(unittest.TestCase):
    def test_rotation_preserves_requested_depth_and_channel_count(self):
        decoded, rotated = Path("decoded.tif"), Path("rotated.tif")
        for bits in (8, 16):
            for components in (1, 3):
                with self.subTest(bits=bits, components=components), \
                        patch.object(implementation, "_run", return_value=b"  Quantum Depth 16\n") as run, \
                        patch.object(implementation, "_check_tiff", return_value={}) as check, \
                        patch.object(implementation, "_check_icc", return_value=rotated) as icc:
                    spec = implementation._RasterSpec(33, 48, bytes([bits - 1, 1, 1]) * components)
                    self.assertEqual(implementation._rotate_tiff(
                        decoded, rotated, 90, spec, b"profile", Tools(), 600,
                    ), rotated)
                    self.assertEqual(run.call_args.args[0], [
                        "gm", "convert", decoded, "-rotate", "90",
                        "-type", "TrueColor" if components == 3 else "Grayscale",
                        "-depth", str(bits), "-compress", "None", rotated,
                    ])
                    self.assertEqual(run.call_count, 2 if bits == 16 else 1)
                    check.assert_called_once_with(rotated, spec, Tools(), 600)
                    icc.assert_called_once_with(rotated, b"profile", Tools(), 600)

    def test_16_bit_rotation_rejects_q8_and_unknown_quantum_depth(self):
        spec = implementation._RasterSpec(33, 48, bytes([15, 1, 1]) * 3)
        for version in (b"  Quantum Depth 8\n", b"GraphicsMagick unknown build"):
            with self.subTest(version=version), \
                    patch.object(implementation, "_run", return_value=version) as run:
                with self.assertRaisesRegex(RotationError, "Q16 or higher"):
                    implementation._rotate_tiff(
                        Path("decoded.tif"), Path("rotated.tif"), 90, spec, b"", Tools(), 600,
                    )
                run.assert_called_once_with(["gm", "version"], timeout=600)


class UtilityTests(unittest.TestCase):
    def test_access_preflight_checks_effective_ids_without_creating_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.jpx"
            path.write_bytes(b"original")
            with patch.object(os, "access", return_value=True) as access:
                with patch.object(os, "supports_effective_ids", {access}):
                    self.assertEqual(implementation.check_rotation_access(path), path)
            self.assertEqual(access.call_args_list, [
                unittest.mock.call(path, os.R_OK, effective_ids=True),
                unittest.mock.call(path.parent, os.W_OK | os.X_OK, effective_ids=True),
            ])
            self.assertEqual(list(path.parent.iterdir()), [path])
            self.assertEqual(path.read_bytes(), b"original")

    def test_access_preflight_handles_platforms_without_effective_id_support(self):
        path = Path("/images/source.jpx")
        with patch.object(os, "access", return_value=True) as access:
            with patch.object(os, "supports_effective_ids", set()):
                implementation.check_rotation_access(path)
        self.assertFalse(access.call_args.kwargs["effective_ids"])

    def test_access_preflight_reports_unreadable_source(self):
        with patch.object(os, "access", return_value=False) as access:
            with self.assertRaisesRegex(RotationError, "No read access"):
                implementation.check_rotation_access(Path("/images/source.jpx"))
        access.assert_called_once()

    def test_access_preflight_reports_directory_permissions(self):
        with patch.object(os, "access", side_effect=[True, False]):
            with self.assertRaisesRegex(RotationError, "No write/search access"):
                implementation.check_rotation_access(Path("/images/source.jpx"))

    def test_path_text_narrows_strings_before_using_fspath(self):
        path = FilesystemPath("/images/source.jpx")
        with patch.object(os, "fspath", return_value="/images/source.jpx") as fspath:
            self.assertEqual(implementation._path_text("literal.jpx"), "literal.jpx")
            fspath.assert_not_called()
            self.assertEqual(implementation._path_text(path), "/images/source.jpx")
            fspath.assert_called_once_with(path)

    def test_subprocess_uses_path_protocol_not_string_representation(self):
        executable = FilesystemPath("/tools/kdu_expand")
        source = FilesystemPath("/images/source with spaces.jpx")
        with patch.object(subprocess, "run", return_value=subprocess.CompletedProcess(
                [], 0, b"output", b"")) as run:
            result = implementation._run([executable, "-i", source], timeout=5)
        self.assertEqual(result, b"output")
        self.assertEqual(run.call_args.args[0],
                         ["/tools/kdu_expand", "-i", "/images/source with spaces.jpx"])

    def test_subprocess_errors_report_filesystem_path(self):
        executable = FilesystemPath("/tools/kdu_expand")
        for outcome in (PermissionError("not executable"),
                        subprocess.TimeoutExpired("tool", 1),
                        subprocess.CompletedProcess([], 12, b"", b"failed")):
            with self.subTest(outcome=outcome):
                if isinstance(outcome, Exception):
                    run = patch.object(subprocess, "run", side_effect=outcome)
                else:
                    run = patch.object(subprocess, "run", return_value=outcome)
                with run, self.assertRaisesRegex(RotationError, "/tools/kdu_expand"):
                    implementation._run([executable], timeout=1)

    def test_empty_glob_error_reports_filesystem_path(self):
        with tempfile.TemporaryDirectory() as directory:
            pattern = str(Path(directory) / "missing-*.jpx")
            with self.assertRaises(RotationError) as caught:
                plan_rotations(FilesystemPath(pattern), 180)
        self.assertIn(pattern, str(caught.exception))

    def test_production_code_has_no_nested_functions(self):
        package = Path(implementation.__file__).parent
        for path in package.glob("*.py"):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    nested = [child.name for child in ast.walk(node)
                              if child is not node
                              and isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    self.assertEqual(nested, [], f"{path.name}: {node.name}")

    def test_tools_validation_returns_the_validated_configuration(self):
        tools = Tools()
        with patch.object(shutil, "which", return_value="/trusted/tool"):
            self.assertIs(tools.validate(), tools)

    def test_invalid_tiff_numbers_are_reported_at_parse_boundary(self):
        info = dict(FileType="TIFF", ImageWidth=48, ImageHeight=33,
                    SamplesPerPixel=3, BitsPerSample="8 8 8", SampleFormat="1 1 1")
        for field, message in (("BitsPerSample", "invalid TIFF sample precision"),
                               ("SampleFormat", "invalid TIFF sample format")):
            with self.subTest(field=field), patch.object(
                    implementation, "_inspect", return_value={**info, field: "invalid"}):
                with self.assertRaisesRegex(RotationError, message) as caught:
                    spec = implementation._RasterSpec(48, 33, bytes([7, 1, 1]) * 3)
                    _ = implementation._check_tiff(Path("image.tif"), spec, Tools(), 600)
                self.assertIsInstance(caught.exception.__cause__, ValueError)

    def test_invalid_json_and_warnings_rejected(self):
        for value in (b'[{"Warning":"bad"}]', b"not JSON", b"[]"):
            with self.assertRaises(RotationError):
                implementation._json_record(value)

    def test_subprocess_timeout_and_failures(self):
        with patch.object(subprocess, "run", side_effect=subprocess.TimeoutExpired("tool", 1)):
            with self.assertRaisesRegex(RotationError, "timeout"):
                implementation._run(["tool"], timeout=1)
        with patch.object(subprocess, "run", return_value=subprocess.CompletedProcess(
                ["tool"], 12, b"output", b"error")):
            with self.assertRaisesRegex(RotationError, "exit 12"):
                implementation._run(["tool"], timeout=1)


if __name__ == "__main__":
    unittest.main()
