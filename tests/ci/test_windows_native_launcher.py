"""Windows launcher static safety/wiring tests; no Windows or Godot execution claimed."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "nex_bench"


class WindowsNativeLauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.launcher = (LAB / "Start-NEX.ps1").read_text(encoding="utf-8")
        cls.batch = (LAB / "Start-NEX.cmd").read_text(encoding="utf-8")
        cls.lock = json.loads(
            (ROOT / ".nex/toolchain/NEX-M00-WO-001-toolchain-lock.json").read_text(encoding="utf-8")
        )
        cls.readme = (LAB / "README.md").read_text(encoding="utf-8")

    def test_lock_drives_actual_version_check(self):
        self.assertEqual(self.lock["godot"]["tag"], "4.7.2-stable")
        self.assertIn('NEX-M00-WO-001-toolchain-lock.json', self.launcher)
        self.assertIn('$lock.godot.tag', self.launcher)
        self.assertIn('StartsWith($expectedVersion', self.launcher)

    def test_does_not_install_download_or_disable_security(self):
        for forbidden in ("Invoke-WebRequest", "Start-BitsTransfer", "irm ", "iwr ",
                          "Install-Module", "Set-ExecutionPolicy", "ExecutionPolicy Bypass",
                          "Invoke-Expression", "DownloadString", "curl ", "wget "):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.launcher)
                self.assertNotIn(forbidden, self.batch)

    def test_fails_closed_on_wrong_binary_and_native_smoke_failure(self):
        for token in ('Stop-Nex "Godot', '$versionExit -ne 0',
                      '$smokeExit -ne 0', 'NEX_NATIVE_IMPORT_SMOKE_PASS',
                      'NEX_LAUNCH_BLOCKED'):
            with self.subTest(token=token):
                self.assertIn(token, self.launcher)

    def test_launches_same_existing_unified_project(self):
        for token in ('Split-Path -Parent $PSCommandPath', '--path $projectDir',
                      'Start-Process -FilePath $godot', 'NEX_GUI_STARTED'):
            with self.subTest(token=token):
                self.assertIn(token, self.launcher)
        self.assertTrue((LAB / "project.godot").is_file())
        self.assertTrue((LAB / "smoke.gd").is_file())

    def test_double_click_passes_arguments_and_returns_exit_code(self):
        self.assertIn('"%~dp0Start-NEX.ps1" %*', self.batch)
        self.assertIn('exit /b %NEX_EXIT%', self.batch)
        self.assertIn('powershell.exe -NoLogo -NoProfile', self.batch)
        self.assertIn('-ExecutionPolicy RemoteSigned', self.batch)

    def test_native_ci_checks_real_controls_and_powershell_smoke(self):
        smoke = (LAB / "smoke.gd").read_text(encoding="utf-8")
        workflow = (ROOT / ".github/workflows/nex-visual-lab-native-smoke.yml").read_text(encoding="utf-8")
        self.assertIn("toolbar.get_child_count() != 7", smoke)
        self.assertIn("workload.get_child_count() != 25", smoke)
        self.assertIn("scene_root.get_node_or_null(\"IsometricCamera\")", smoke)
        self.assertIn("pwsh -NoLogo -NoProfile -File nex_bench/Start-NEX.ps1", workflow)
        self.assertIn("NEX_POWERSHELL_LAUNCHER_SMOKE_VERIFIED", workflow)

    def test_windows_native_runner_verifies_pinned_cmd_smoke(self):
        workflow = (ROOT / ".github/workflows/nex-visual-lab-native-smoke.yml").read_text(encoding="utf-8")
        self.assertIn("runs-on: windows-2022", workflow)
        self.assertIn("windowsReferenceBinary.sha256", workflow)
        self.assertIn("Get-FileHash -LiteralPath", workflow)
        self.assertIn("Start-NEX.cmd' -GodotPath", workflow)
        self.assertIn("NEX_WINDOWS_CMD_NATIVE_SMOKE_VERIFIED", workflow)
        self.assertIn("if not defined CI pause", self.batch)

    def test_headless_mode_and_instructions(self):
        self.assertIn('[switch]$SmokeOnly', self.launcher)
        self.assertIn('if ($SmokeOnly)', self.launcher)
        self.assertIn('Start-NEX.cmd', self.readme)
        self.assertIn('-SmokeOnly', self.readme)


if __name__ == "__main__":
    unittest.main()
