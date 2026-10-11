# NEX M00 | Validation and resource budget
**Status:** native M00 Windows source build and targeted smokes/tests VERIFIED for PR #78 and post-merge main; historical plan preserved below and evidence recorded separately.
**Targets:** Windows native local (Codex Desktop) + Ubuntu headless free GitHub Actions. No GPU tests in cloud; benchmark FPS/VRAM belongs to admitted M01.
1. Record `git status`, branch + main SHA, lock hashes, Node/GEF baseline and local compiler/SCons/Python availability; estimate download/build duration and disk footprint before action.
2. Verify official Godot tag `4.7.2-stable` commit `ed1daf0bf001b61586d9930840f2f1394092c079`; download source `godot-4.7.2-stable.tar.xz` from verified upstream and compare SHA256 `a18ce0ccec3ecc40b0dd6c4f5132ca934e9fb7c2979717940ff32aee1eb35481`; mismatch => hard STOP.
3. Validate MIT/third-party notices and SCons/Compiler/SDK compatibility. Prefer one bounded source build job first, no concurrent heavy compilation on 24 GB RAM; do not assume RTX5050 FPS or GPU workload.
4. Windows smoke: version, editor initialization with disposable project, minimal scene import/start, clean exit; record stdout/stderr/exit codes, path to binary/manifest and runtime constraints.
5. Ubuntu CI: pinned official artifacts or build stage under free-runner constraints; `--headless` smoke and minimal scene import, no Windows FPS inference.
6. Negative tests: invalid archive digest, missing executable, nonexistent fixture, conflicting output path and permission errors fail with nonzero status and clear logs without deleting user data.
7. Evidence: package/compiler versions, asset/hash/source SHA, CI links exact HEAD, tests count, version and timestamps, elapsed time/peak memory if measured, licenses, risk/remediation, proposed checkpoint only.
**STOP:** do not label M00 DONE unless Windows native source build and all mandatory acceptance gates are independently verified; bounded resource failures become BLOCKED/INCONCLUSIVE with minimal Correction Delta.

## Verified result / limitations
- PR #78 exact HEAD `8c26ecc019b05edef5839f21c43b4af72bb34d9c`: source-build Windows and Ubuntu smoke in Actions run #38175760924, local Python 17/17, local CD-003 5/5 fresh plus 5/5 warm editor launches; CodeRabbit SUCCESS, 10/10 exact-head checks PASS, zero unresolved review threads.
- Actual main squash `0c6cdbfc13bd0c1c8e80d293f7da7f2302027861`: identical Git tree to reviewed head and 6/6 applicable postmerge checks PASS (GEF/Ubuntu+Windows, Governance x2, SonarCloud, Socket). No M00 source-build workflow run on main is claimed. Historic 0xC0000005 root cause UNKNOWN, accepted as residual risk by Owner.
- M00 tested baseline is not a runtime performance benchmark. M01 NOT_ADMITTED. See `.engineering/evidence/NEX-M00-WO-001-POSTMERGE-EVIDENCE.md`.
