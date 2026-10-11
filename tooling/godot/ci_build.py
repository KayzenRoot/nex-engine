#!/usr/bin/env python3
"""Verified, bounded Godot M00 build and smoke helpers for GitHub Actions."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import queue
import shutil
import stat
import subprocess
import sys
import tarfile
import threading
import time
import urllib.request
import zipfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlsplit


REPO_ROOT = Path(__file__).resolve().parents[2]
LOCK_PATH = REPO_ROOT / ".nex" / "toolchain" / "NEX-M00-WO-001-toolchain-lock.json"


class IntegrityError(RuntimeError):
    """Raised when an input, path, or required tool violates the pinned contract."""


class CommandFailure(RuntimeError):
    def __init__(self, command: Iterable[str], exit_code: int, log_path: Path, timed_out: bool = False):
        self.command = list(command)
        self.exit_code = exit_code
        self.log_path = log_path
        self.timed_out = timed_out
        state = "timed out" if timed_out else f"exited {exit_code}"
        super().__init__(f"Command {state}; full output: {log_path}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_lock() -> dict[str, Any]:
    try:
        return json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrityError(f"Could not read toolchain lock {LOCK_PATH}: {exc}") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_file(path: Path, expected_sha256: str, expected_size: int | None = None) -> dict[str, Any]:
    if not path.is_file():
        raise IntegrityError(f"Required file is missing: {path}")
    actual_size = path.stat().st_size
    actual_sha256 = sha256_file(path)
    if expected_size is not None and actual_size != expected_size:
        raise IntegrityError(
            f"Size mismatch for {path}: expected {expected_size} bytes, got {actual_size}."
        )
    if actual_sha256.lower() != expected_sha256.lower():
        raise IntegrityError(
            f"SHA-256 mismatch for {path}: expected {expected_sha256}, got {actual_sha256}."
        )
    return {"path": str(path), "size": actual_size, "sha256": actual_sha256}


def dependency_pin(lock: dict[str, Any], name: str) -> dict[str, Any]:
    matches = [pin for pin in lock.get("dependencies", []) if pin.get("name") == name]
    if len(matches) != 1:
        raise IntegrityError(f"Expected one dependency pin named {name!r}, found {len(matches)}.")
    return matches[0]


def download_filename(url: str) -> str:
    filename = PurePosixPath(urlsplit(url).path).name
    if filename in ("", ".", ".."):
        raise IntegrityError(f"Pinned download URL has no file name: {url!r}")
    return filename


def dependency_destination_name(pin: dict[str, Any]) -> str:
    required_files = pin.get("requiredFiles")
    if not isinstance(required_files, list) or not required_files:
        raise IntegrityError(f"Dependency {pin.get('name', '<unnamed>')!r} has no requiredFiles list.")
    paths = []
    for name in required_files:
        if not isinstance(name, str):
            raise IntegrityError(f"Dependency requiredFiles entries must be strings: {name!r}")
        paths.append(_safe_archive_parts(name))
    roots = {parts[0] for parts in paths if parts}
    if len(roots) != 1 or any(not parts for parts in paths):
        raise IntegrityError(f"Dependency {pin.get('name', '<unnamed>')!r} requiredFiles must share one root.")
    return roots.pop()


def verify_dependency_files(root: Path, pin: dict[str, Any]) -> str:
    destination_name = dependency_destination_name(pin)
    for name in pin["requiredFiles"]:
        require_file(root.joinpath(*_safe_archive_parts(name)))
    return destination_name


def download_verified(
    url: str,
    destination: Path,
    expected_sha256: str,
    expected_size: int | None = None,
) -> dict[str, Any]:
    if destination.exists():
        raise IntegrityError(f"Refusing to overwrite existing download output: {destination}")
    partial = destination.with_name(destination.name + ".part")
    if partial.exists():
        raise IntegrityError(f"Refusing to overwrite existing partial download: {partial}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "NEX-M00-WO-001-CI"})
    digest = hashlib.sha256()
    byte_count = 0
    with urllib.request.urlopen(request, timeout=60) as response, partial.open("xb") as target:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            new_byte_count = byte_count + len(chunk)
            if expected_size is not None and new_byte_count > expected_size:
                raise IntegrityError(
                    f"Size mismatch for {url}: expected at most {expected_size} bytes, "
                    f"received at least {new_byte_count}."
                )
            target.write(chunk)
            digest.update(chunk)
            byte_count = new_byte_count
        target.flush()
        os.fsync(target.fileno())
    actual_sha256 = digest.hexdigest()
    if expected_size is not None and byte_count != expected_size:
        raise IntegrityError(
            f"Size mismatch for {url}: expected {expected_size} bytes, got {byte_count}."
        )
    if actual_sha256.lower() != expected_sha256.lower():
        raise IntegrityError(
            f"SHA-256 mismatch for {url}: expected {expected_sha256}, got {actual_sha256}."
        )
    if destination.exists():
        raise IntegrityError(f"Refusing to overwrite a download created concurrently: {destination}")
    partial.rename(destination)
    return {"url": url, "path": str(destination), "size": byte_count, "sha256": actual_sha256}


def create_new_directory(path: Path) -> Path:
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise IntegrityError(f"Output path already exists; refusing to remove or reuse it: {path}") from exc
    except PermissionError as exc:
        raise IntegrityError(f"Permission denied while creating output path {path}: {exc}") from exc
    return path


def _safe_archive_parts(name: str) -> tuple[str, ...]:
    if not name or "\x00" in name or "\\" in name:
        raise IntegrityError(f"Unsafe archive member path: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise IntegrityError(f"Unsafe archive member path: {name!r}")
    if any(":" in part for part in path.parts):
        raise IntegrityError(f"Drive-qualified archive member path is forbidden: {name!r}")
    return path.parts


def _contained_path(root: Path, parts: tuple[str, ...]) -> Path:
    root_resolved = root.resolve()
    target = root.joinpath(*parts).resolve()
    try:
        target.relative_to(root_resolved)
    except ValueError as exc:
        raise IntegrityError(f"Archive member escapes extraction directory: {parts!r}") from exc
    return target


def safe_extract_tar(archive: Path, destination: Path, expected_root: str) -> list[str]:
    if destination.exists():
        raise IntegrityError(f"Refusing to extract over existing output: {destination}")
    with tarfile.open(archive, mode="r:xz") as tar:
        members = tar.getmembers()
        seen: set[tuple[str, ...]] = set()
        validated: list[tuple[tarfile.TarInfo, tuple[str, ...]]] = []
        for member in members:
            parts = _safe_archive_parts(member.name.rstrip("/"))
            if not parts or parts[0] != expected_root:
                raise IntegrityError(f"Unexpected source archive root in member {member.name!r}")
            if parts in seen:
                raise IntegrityError(f"Duplicate source archive member: {member.name!r}")
            seen.add(parts)
            if not (member.isdir() or member.isfile()):
                raise IntegrityError(f"Unsupported tar member type: {member.name!r}")
            _contained_path(destination, parts)
            validated.append((member, parts))

        destination.mkdir(parents=True, exist_ok=False)
        for member, parts in validated:
            target = destination.joinpath(*parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            if source is None:
                raise IntegrityError(f"Could not read regular tar member: {member.name!r}")
            with source, target.open("xb") as output:
                shutil.copyfileobj(source, output)
            if os.name != "nt":
                target.chmod(member.mode & 0o777)
    return [member.name for member in members]


def safe_extract_zip(archive: Path, destination: Path) -> list[str]:
    if destination.exists():
        raise IntegrityError(f"Refusing to extract over existing output: {destination}")
    with zipfile.ZipFile(archive) as zipped:
        entries = zipped.infolist()
        seen: set[tuple[str, ...]] = set()
        validated: list[tuple[zipfile.ZipInfo, tuple[str, ...], bool, int]] = []
        for entry in entries:
            parts = _safe_archive_parts(entry.filename.rstrip("/"))
            if not parts:
                raise IntegrityError(f"Empty zip member path: {entry.filename!r}")
            if parts in seen:
                raise IntegrityError(f"Duplicate zip member: {entry.filename!r}")
            seen.add(parts)
            mode = (entry.external_attr >> 16) & 0xFFFF
            file_type = stat.S_IFMT(mode)
            is_directory = entry.is_dir() or file_type == stat.S_IFDIR
            if file_type == stat.S_IFLNK:
                raise IntegrityError(f"Symlink entry is forbidden in dependency archive: {entry.filename!r}")
            if entry.flag_bits & 0x1:
                raise IntegrityError(f"Encrypted zip entry is forbidden: {entry.filename!r}")
            _contained_path(destination, parts)
            validated.append((entry, parts, is_directory, mode & 0o777))

        destination.mkdir(parents=True, exist_ok=False)
        for entry, parts, is_directory, mode in validated:
            target = destination.joinpath(*parts)
            if is_directory:
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zipped.open(entry, "r") as source, target.open("xb") as output:
                shutil.copyfileobj(source, output)
            if os.name != "nt" and mode:
                target.chmod(mode)
    return [entry.filename for entry in entries]


def require_file(path: Path) -> Path:
    if not path.is_file():
        raise IntegrityError(f"Required file does not exist: {path}")
    return path


def validate_fixture(path: Path) -> None:
    if not path.is_dir():
        raise IntegrityError(f"Godot smoke fixture directory does not exist: {path}")
    for name in ("project.godot", "main.tscn"):
        require_file(path / name)


def _terminate_process_tree(process: subprocess.Popen[str]) -> None:
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired):
            process.kill()
    else:
        process.terminate()


def run_logged(
    command: Iterable[str],
    *,
    cwd: Path,
    log_path: Path,
    timeout_seconds: int,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    command = [str(part) for part in command]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    started_utc = utc_now()
    print("RUN: " + subprocess.list2cmdline(command), flush=True)
    events: queue.Queue[str | None] = queue.Queue()
    timed_out = False
    with log_path.open("w", encoding="utf-8", errors="replace", newline="") as log:
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        def read_output() -> None:
            assert process.stdout is not None
            try:
                for line in process.stdout:
                    events.put(line)
            finally:
                events.put(None)

        reader = threading.Thread(target=read_output, daemon=True)
        reader.start()
        reader_finished = False
        deadline = started + timeout_seconds
        while not reader_finished or process.poll() is None:
            if time.monotonic() >= deadline:
                if process.poll() is None:
                    timed_out = True
                    _terminate_process_tree(process)
                break
            try:
                item = events.get(timeout=0.25)
            except queue.Empty:
                continue
            if item is None:
                reader_finished = True
            else:
                log.write(item)
                log.flush()
                sys.stdout.write(item)
                sys.stdout.flush()
        if timed_out:
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        else:
            process.wait()
        join_timeout = 10 if timed_out else max(0, min(10, deadline - time.monotonic()))
        reader.join(timeout=join_timeout)
        if process.stdout is not None and not reader.is_alive():
            process.stdout.close()

    elapsed = round(time.monotonic() - started, 3)
    result = {
        "command": command,
        "startedAtUtc": started_utc,
        "endedAtUtc": utc_now(),
        "elapsedSeconds": elapsed,
        "exitCode": process.returncode,
        "logPath": str(log_path),
        "timedOut": timed_out,
    }
    if process.returncode != 0 or timed_out:
        raise CommandFailure(command, process.returncode, log_path, timed_out)
    return result


def _windows_memory() -> dict[str, int]:
    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return {
        "totalPhysicalBytes": int(status.ullTotalPhys),
        "availablePhysicalBytes": int(status.ullAvailPhys),
        "totalCommitLimitBytes": int(status.ullTotalPageFile),
        "availableCommitBytes": int(status.ullAvailPageFile),
    }


def host_resource_snapshot(path: Path) -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "observedAtUtc": utc_now(),
        "logicalProcessors": os.cpu_count(),
        "freeDiskBytes": shutil.disk_usage(path).free,
    }
    if os.name == "nt":
        snapshot.update(_windows_memory())
    elif Path("/proc/meminfo").is_file():
        memory = {}
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            key, value = line.split(":", 1)
            memory[key] = int(value.strip().split()[0]) * 1024
        snapshot["totalPhysicalBytes"] = memory.get("MemTotal", 0)
        snapshot["availablePhysicalBytes"] = memory.get("MemAvailable", 0)
    return snapshot


@contextmanager
def resource_monitor(output_path: Path, sample_seconds: int = 30):
    samples: list[dict[str, Any]] = []
    stop = threading.Event()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    def sample() -> None:
        record = host_resource_snapshot(output_path.parent)
        samples.append(record)
        with output_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")
            stream.flush()

    def monitor() -> None:
        while not stop.wait(sample_seconds):
            try:
                sample()
            except OSError as exc:
                print(f"Resource sample unavailable: {exc}", file=sys.stderr, flush=True)

    sample()
    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    try:
        yield samples
    finally:
        stop.set()
        thread.join(timeout=10)
        sample()


def _run_smoke(binary: Path, fixture: Path, log_dir: Path, prefix: str) -> list[dict[str, Any]]:
    require_file(binary)
    validate_fixture(fixture)
    results = []
    version_log = log_dir / f"{prefix}-version.log"
    results.append(run_logged([binary, "--version"], cwd=fixture, log_path=version_log, timeout_seconds=120))
    version_text = version_log.read_text(encoding="utf-8", errors="replace")
    if "4.7.2" not in version_text:
        raise IntegrityError(f"Godot version smoke did not report 4.7.2; see {version_log}")
    results.append(
        run_logged(
            [binary, "--headless", "--editor", "--path", fixture, "--quit-after", "2"],
            cwd=fixture,
            log_path=log_dir / f"{prefix}-headless-editor.log",
            timeout_seconds=600,
        )
    )
    results.append(
        run_logged(
            [binary, "--headless", "--path", fixture, "--quit-after", "3"],
            cwd=fixture,
            log_path=log_dir / f"{prefix}-scene-smoke.log",
            timeout_seconds=600,
        )
    )
    return results


def _install_scons(wheel: Path, environment_dir: Path, logs: Path) -> Path:
    require_file(wheel)
    run_logged(
        [sys.executable, "-m", "venv", str(environment_dir)],
        cwd=REPO_ROOT,
        log_path=logs / "python-venv.log",
        timeout_seconds=120,
    )
    scons = environment_dir / "Scripts" / "scons.exe"
    pip = environment_dir / "Scripts" / "pip.exe"
    run_logged(
        [pip, "install", "--no-index", "--no-deps", "--disable-pip-version-check", str(wheel)],
        cwd=REPO_ROOT,
        log_path=logs / "scons-offline-install.log",
        timeout_seconds=300,
    )
    require_file(scons)
    return scons


def _copy_notice(source: Path, target: Path) -> None:
    require_file(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _write_github_output(values: dict[str, str]) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if not output:
        return
    with Path(output).open("a", encoding="utf-8", newline="") as stream:
        for key, value in values.items():
            stream.write(f"{key}={value}\n")


def windows_build(args: argparse.Namespace) -> int:
    lock = load_lock()
    fixture = Path(args.fixture).resolve()
    validate_fixture(fixture)
    candidate_sha = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    if candidate_sha.lower() != args.candidate_sha.lower():
        raise IntegrityError(
            f"Checkout SHA mismatch: workflow expected {args.candidate_sha}, checked out {candidate_sha}."
        )
    if os.name != "nt":
        raise IntegrityError("The Godot source build command is permitted only on native Windows.")
    if not os.environ.get("VCToolsVersion") or not os.environ.get("WindowsSDKVersion"):
        raise IntegrityError("MSVC/Windows SDK environment is absent; invoke through the runner vcvars script.")
    expected_python = tuple(int(part) for part in lock["buildTools"]["python"]["version"].split("."))
    if sys.version_info[:3] != expected_python:
        raise IntegrityError(
            f"Python version mismatch: expected {lock['buildTools']['python']['version']}, "
            f"got {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}."
        )
    compiler_pin = lock["buildTools"]["windowsCompiler"]
    actual_toolset = os.environ["VCToolsVersion"].strip().rstrip("\\/")
    if actual_toolset != compiler_pin["toolsetVersion"]:
        raise IntegrityError(
            f"MSVC toolset mismatch: expected {compiler_pin['toolsetVersion']}, got {actual_toolset}."
        )
    actual_sdk = os.environ["WindowsSDKVersion"].strip().rstrip("\\/")
    if actual_sdk != compiler_pin["sdkVersion"]:
        raise IntegrityError(f"Windows SDK mismatch: expected {compiler_pin['sdkVersion']}, got {actual_sdk}.")
    if not shutil.which("cl.exe"):
        raise IntegrityError("MSVC cl.exe is not on PATH after vcvars initialization.")

    output = create_new_directory(Path(args.output_dir).resolve())
    downloads = output / "downloads"
    downloads.mkdir()
    logs = output / "logs"
    logs.mkdir()
    source_extract = output / "source"
    deps_root = output / "build_deps"
    deps_root.mkdir()
    data: dict[str, Any] = {
        "schemaVersion": 1,
        "workOrder": "NEX-M00-WO-001",
        "candidateSha": candidate_sha,
        "startedAtUtc": utc_now(),
        "host": {
            "platform": sys.platform,
            "python": sys.version,
            "logicalProcessors": os.cpu_count(),
            "msvcToolsVersion": actual_toolset,
            "windowsSdkVersion": actual_sdk,
            "freeDiskBytesAtStart": shutil.disk_usage(output).free,
        },
        "source": {
            "repository": lock["godot"]["repository"],
            "tag": lock["godot"]["tag"],
            "commit": lock["godot"]["commit"],
            "license": lock["godot"]["source"]["license"],
        },
        "dependencies": [],
        "tests": [],
    }

    source_pin = lock["godot"]["source"]
    source_archive = downloads / source_pin["file"]
    data["source"]["archive"] = download_verified(
        source_pin["url"], source_archive, source_pin["sha256"], source_pin["size"]
    )
    source_root = f"godot-{lock['godot']['tag']}"
    safe_extract_tar(source_archive, source_extract, source_root)
    source_dir = source_extract / source_root

    accesskit_pin = dependency_pin(lock, "AccessKit C static SDK")
    nir_pin = dependency_pin(lock, "Godot Mesa NIR static library")
    accesskit_name = dependency_destination_name(accesskit_pin)
    accesskit_archive = downloads / download_filename(accesskit_pin["url"])
    data["dependencies"].append(
        download_verified(accesskit_pin["url"], accesskit_archive, accesskit_pin["sha256"], accesskit_pin["size"])
    )
    accesskit_stage = deps_root / f"{accesskit_name}-unpacked"
    safe_extract_zip(accesskit_archive, accesskit_stage)
    accesskit_source = accesskit_stage / Path(accesskit_archive.name).stem
    if not accesskit_source.is_dir():
        raise IntegrityError(f"Dependency archive did not contain its expected top-level directory: {accesskit_source}.")
    accesskit = deps_root / accesskit_name
    accesskit_source.rename(accesskit)
    verify_dependency_files(deps_root, accesskit_pin)

    mesa_name = dependency_destination_name(nir_pin)
    nir_archive = downloads / download_filename(nir_pin["url"])
    data["dependencies"].append(
        download_verified(nir_pin["url"], nir_archive, nir_pin["sha256"], nir_pin["size"])
    )
    mesa = deps_root / mesa_name
    safe_extract_zip(nir_archive, mesa)
    verify_dependency_files(deps_root, nir_pin)
    nir_license = downloads / download_filename(nir_pin["licenseUrl"])
    data["dependencies"].append(
        download_verified(nir_pin["licenseUrl"], nir_license, nir_pin["licenseSha256"], nir_pin["licenseSize"])
    )

    scons_pin = lock["buildTools"]["scons"]
    scons_wheel = downloads / scons_pin["file"]
    data["buildTools"] = {
        "python": sys.version,
        "sconsWheel": download_verified(scons_pin["url"], scons_wheel, scons_pin["sha256"], scons_pin["size"]),
        "sconsLicense": scons_pin["license"],
    }
    scons = _install_scons(scons_wheel, output / "scons-venv", logs)
    scons_version = subprocess.run(
        [str(scons), "--version"], cwd=source_dir, text=True, capture_output=True, timeout=60, check=True
    )
    data["buildTools"]["sconsVersionOutput"] = (scons_version.stdout + scons_version.stderr).strip()

    flags = lock["build"]["command"][1:]
    flags += [f"accesskit_sdk_path={accesskit}", f"mesa_libs={mesa}"]
    help_result = subprocess.run(
        [str(scons), "--help", *flags],
        cwd=source_dir,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    help_text = help_result.stdout + help_result.stderr
    (logs / "scons-help.log").write_text(help_text, encoding="utf-8", errors="replace")
    if help_result.returncode != 0:
        raise IntegrityError(f"Pinned SCons rejected the required build options; see {logs / 'scons-help.log'}")
    for required_option in ("accesskit", "d3d12", "debug_symbols", "lto"):
        if required_option not in help_text:
            raise IntegrityError(f"SCons help did not expose required option {required_option}.")

    build_command = [str(scons), *flags]
    data["build"] = {
        "command": build_command,
        "cwd": str(source_dir),
        "startedAtUtc": utc_now(),
        "timeoutMinutes": lock["build"]["maximumBuildMinutes"],
        "estimatedDuration": lock["build"]["estimatedDuration"],
        "featureFlags": {"accesskit": True, "d3d12": True, "pix": False, "agilitySdk": "not supplied"},
    }
    with resource_monitor(logs / "resource-samples.jsonl") as resource_samples:
        build_result = run_logged(
            build_command,
            cwd=source_dir,
            log_path=logs / "windows-source-build.log",
            timeout_seconds=lock["build"]["maximumBuildMinutes"] * 60,
        )
    data["build"]["result"] = build_result
    data["build"]["endedAtUtc"] = utc_now()
    data["build"]["resourceSampleCount"] = len(resource_samples)
    data["build"]["minimumAvailablePhysicalBytes"] = min(
        (item.get("availablePhysicalBytes", 0) for item in resource_samples), default=None
    )
    data["build"]["minimumAvailableCommitBytes"] = min(
        (item.get("availableCommitBytes", 0) for item in resource_samples if "availableCommitBytes" in item),
        default=None,
    )
    data["build"]["minimumFreeDiskBytes"] = min(
        (item.get("freeDiskBytes", 0) for item in resource_samples), default=None
    )

    binary_dir = source_dir / "bin"
    editor = require_file(binary_dir / "godot.windows.editor.x86_64.exe")
    console_editor = require_file(binary_dir / "godot.windows.editor.x86_64.console.exe")
    data["tests"] = _run_smoke(console_editor, fixture, logs, "windows-source")
    data["binary"] = {
        "editor": {"file": editor.name, "size": editor.stat().st_size, "sha256": sha256_file(editor)},
        "consoleEditor": {
            "file": console_editor.name,
            "size": console_editor.stat().st_size,
            "sha256": sha256_file(console_editor),
        },
        "reportedVersion": (logs / "windows-source-version.log").read_text(encoding="utf-8", errors="replace").strip(),
    }

    package_dir = output / "package"
    package_dir.mkdir()
    shutil.copy2(editor, package_dir / editor.name)
    shutil.copy2(console_editor, package_dir / console_editor.name)
    notices = package_dir / "notices"
    _copy_notice(source_dir / "LICENSE.txt", notices / "Godot-LICENSE.txt")
    _copy_notice(source_dir / "COPYRIGHT.txt", notices / "Godot-COPYRIGHT.txt")
    _copy_notice(source_dir / "thirdparty" / "README.md", notices / "Godot-thirdparty-README.md")
    accesskit_notices = notices / "AccessKit"
    for name in ("LICENSE-MIT", "LICENSE-APACHE", "LICENSE.chromium"):
        source = accesskit / name
        if source.is_file():
            _copy_notice(source, accesskit_notices / name)
    _copy_notice(nir_license, notices / "Mesa-NIR-LICENSE.md")
    data["runtimeLicenseNotices"] = [
        "Godot MIT and copyright files",
        "Godot thirdparty/README.md",
        "AccessKit MIT, Apache-2.0, and Chromium notice files from verified archive",
        "Godot NIR static MIT license from verified tagged source",
    ]
    data["endedAtUtc"] = utc_now()
    data["host"]["freeDiskBytesAtEnd"] = shutil.disk_usage(output).free
    (package_dir / "build-manifest.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    package_zip = output / "godot-windows-source-build.zip"
    with zipfile.ZipFile(package_zip, mode="x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zipped:
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file():
                zipped.write(file_path, file_path.relative_to(package_dir).as_posix())
    package_size = package_zip.stat().st_size
    if package_size > lock["build"]["artifactMaximumBytes"]:
        raise IntegrityError(
            f"Windows binary package is {package_size} bytes; maximum is {lock['build']['artifactMaximumBytes']}."
        )
    package_digest = sha256_file(package_zip)
    checksum_file = output / "godot-windows-source-build.zip.sha256"
    checksum_file.write_text(f"{package_digest}  {package_zip.name}\n", encoding="ascii")
    print(f"Package SHA-256: {package_digest}; bytes: {package_size}", flush=True)
    _write_github_output({"package_path": str(package_zip), "package_ready": "true"})
    return 0


def linux_smoke(args: argparse.Namespace) -> int:
    lock = load_lock()
    fixture = Path(args.fixture).resolve()
    validate_fixture(fixture)
    candidate_sha = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    if candidate_sha.lower() != args.candidate_sha.lower():
        raise IntegrityError(
            f"Checkout SHA mismatch: workflow expected {args.candidate_sha}, checked out {candidate_sha}."
        )
    output = create_new_directory(Path(args.output_dir).resolve())
    logs = output / "logs"
    logs.mkdir()
    downloads = output / "downloads"
    downloads.mkdir()
    binary_pin = lock["godot"]["linuxSmokeBinary"]
    archive = downloads / binary_pin["file"]
    download_verified(binary_pin["url"], archive, binary_pin["sha256"], binary_pin["size"])
    extraction = output / "godot"
    safe_extract_zip(archive, extraction)
    binaries = [path for path in extraction.rglob("Godot_v4.7.2-stable_linux.x86_64") if path.is_file()]
    if len(binaries) != 1:
        raise IntegrityError(f"Expected one official Linux editor binary, found {len(binaries)}.")
    binary = binaries[0]
    binary.chmod(binary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    results = _run_smoke(binary, fixture, logs, "ubuntu-official")
    (output / "smoke-results.json").write_text(
        json.dumps(
            {
                "workOrder": "NEX-M00-WO-001",
                "startedAtUtc": results[0]["startedAtUtc"],
                "endedAtUtc": utc_now(),
                "sourceSha": candidate_sha,
                "binary": {
                    "path": str(binary),
                    "size": binary.stat().st_size,
                    "sha256": sha256_file(binary),
                    "reportedVersion": (logs / "ubuntu-official-version.log").read_text(
                        encoding="utf-8", errors="replace"
                    ).strip(),
                },
                "archive": {"name": binary_pin["file"], "size": binary_pin["size"], "sha256": binary_pin["sha256"]},
                "smokeResults": results,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    windows = commands.add_parser("windows-build")
    windows.add_argument("--candidate-sha", required=True)
    windows.add_argument("--fixture", default=str(REPO_ROOT / "tests" / "m00" / "minimal-project"))
    windows.add_argument("--output-dir", required=True)
    linux = commands.add_parser("linux-smoke")
    linux.add_argument("--candidate-sha", required=True)
    linux.add_argument("--fixture", default=str(REPO_ROOT / "tests" / "m00" / "minimal-project"))
    linux.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    try:
        if args.command == "windows-build":
            return windows_build(args)
        return linux_smoke(args)
    except (IntegrityError, CommandFailure, OSError, subprocess.SubprocessError) as exc:
        print(f"M00 CI FAILED: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
