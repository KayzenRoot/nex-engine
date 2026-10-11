from __future__ import annotations

import io
import json
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tooling" / "godot"))

import ci_build


class IntegrityHelperTests(unittest.TestCase):
    def test_wrong_sha256_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "payload.bin"
            path.write_bytes(b"pinned data")
            with self.assertRaisesRegex(ci_build.IntegrityError, "SHA-256 mismatch"):
                ci_build.verify_file(path, "0" * 64)

    def test_download_digest_mismatch_stops_before_output_is_promoted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "payload.zip"
            with mock.patch("ci_build.urllib.request.urlopen", return_value=io.BytesIO(b"untrusted bytes")):
                with self.assertRaisesRegex(ci_build.IntegrityError, "SHA-256 mismatch"):
                    ci_build.download_verified("https://example.invalid/payload.zip", destination, "0" * 64)
            self.assertFalse(destination.exists())
            self.assertTrue(destination.with_name(destination.name + ".part").exists())

    def test_valid_zip_extracts_without_replacing_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "dependency.zip"
            with zipfile.ZipFile(archive, "w") as zipped:
                zipped.writestr("package/include/header.h", "verified")
            destination = root / "extract"
            ci_build.safe_extract_zip(archive, destination)
            self.assertEqual((destination / "package" / "include" / "header.h").read_text(), "verified")

    def test_tar_traversal_is_rejected_before_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "source.tar.xz"
            with tarfile.open(archive, "w:xz") as tar:
                safe = tarfile.TarInfo("godot-source/README.md")
                safe_data = b"safe"
                safe.size = len(safe_data)
                tar.addfile(safe, io.BytesIO(safe_data))
                unsafe = tarfile.TarInfo("godot-source/../../outside.txt")
                unsafe_data = b"outside"
                unsafe.size = len(unsafe_data)
                tar.addfile(unsafe, io.BytesIO(unsafe_data))
            destination = root / "extract"
            with self.assertRaisesRegex(ci_build.IntegrityError, "Unsafe archive member"):
                ci_build.safe_extract_tar(archive, destination, "godot-source")
            self.assertFalse(destination.exists())
            self.assertFalse((root / "outside.txt").exists())

    def test_zip_traversal_is_rejected_before_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "dependency.zip"
            with zipfile.ZipFile(archive, "w") as zipped:
                zipped.writestr("package/safe.txt", "safe")
                zipped.writestr("../outside.txt", "outside")
            destination = root / "extract"
            with self.assertRaisesRegex(ci_build.IntegrityError, "Unsafe archive member"):
                ci_build.safe_extract_zip(archive, destination)
            self.assertFalse(destination.exists())
            self.assertFalse((root / "outside.txt").exists())

    def test_zip_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "symlink.zip"
            entry = zipfile.ZipInfo("package/link")
            entry.create_system = 3
            entry.external_attr = (0o120777 << 16)
            with zipfile.ZipFile(archive, "w") as zipped:
                zipped.writestr(entry, "target")
            with self.assertRaisesRegex(ci_build.IntegrityError, "Symlink entry"):
                ci_build.safe_extract_zip(archive, root / "extract")

    def test_missing_executable_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ci_build.IntegrityError, "Required file does not exist"):
                ci_build.require_file(Path(temp) / "missing.exe")

    def test_missing_fixture_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ci_build.IntegrityError, "fixture directory does not exist"):
                ci_build.validate_fixture(Path(temp) / "missing-project")

    def test_conflicting_output_path_preserves_existing_user_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "existing"
            output.mkdir()
            marker = output / "keep.txt"
            marker.write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(ci_build.IntegrityError, "refusing to remove or reuse"):
                ci_build.create_new_directory(output)
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")

    def test_permission_error_is_reported_without_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "blocked"
            with mock.patch.object(Path, "mkdir", side_effect=PermissionError("denied")):
                with self.assertRaisesRegex(ci_build.IntegrityError, "Permission denied"):
                    ci_build.create_new_directory(target)

    def test_nonzero_command_exit_is_reported_with_log(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "command.log"
            with self.assertRaises(ci_build.CommandFailure) as raised:
                ci_build.run_logged(
                    [sys.executable, "-c", "print('visible failure'); raise SystemExit(23)"],
                    cwd=root,
                    log_path=log,
                    timeout_seconds=30,
                )
            self.assertEqual(raised.exception.exit_code, 23)
            self.assertIn("visible failure", log.read_text(encoding="utf-8"))

    def test_lock_keeps_required_windows_features_enabled(self) -> None:
        lock = json.loads(ci_build.LOCK_PATH.read_text(encoding="utf-8"))
        flags = lock["build"]["command"]
        for required in (
            "platform=windows",
            "target=editor",
            "arch=x86_64",
            "-j1",
            "lto=none",
            "debug_symbols=no",
            "accesskit=yes",
            "d3d12=yes",
            "msvc_version=14.4",
            "mssdk_version=10.0.26100.0",
        ):
            self.assertIn(required, flags)
        self.assertTrue(lock["policy"]["verifyBeforeExtractionOrExecution"])
        self.assertTrue(lock["policy"]["doNotDeleteExistingOutput"])
        self.assertLessEqual(lock["build"]["maximumBuildMinutes"], 180)


if __name__ == "__main__":
    unittest.main()
