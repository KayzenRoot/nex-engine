# NEX-M00-WO-001 — Evidence Bundle

**Evidence snapshot:** exact candidate `a58b86754fd1fd729296d085d6e10f610c238297` was built, all technical CI/security checks passed, and its digest-verified Windows artifact passed local smokes. CodeRabbit remained skipped because the PR was draft. This file is being refreshed after that snapshot; its commit advances the PR HEAD, so the resulting exact HEAD must receive fresh checks and artifact/local-smoke validation. No merge, checkpoint promotion, or M01 admission is authorized here.

- **Work Order:** NEX-M00-WO-001, Issue #5
- **Correction:** Delta 002, Windows source build through standard GitHub Actions; attached PDF SHA-256 `0137eb1ac39d20b6616a19b04a4e7427025fcc3b0fd19723ccc3384cbcec6360`
- **Repository/PR:** [KayzenRoot/nex-engine PR #78](https://github.com/KayzenRoot/nex-engine/pull/78), branch `feat/nex-m00-wo-001-local-windows`
- **Required base and verified GitHub `main`:** `c4174573086df365aadc72967e4722b2cbe6f3ac`
**Correction commit:** `6d42e9114de25f8b8eaa221a2cf73fe79500c90f`; the evidence commit follows it. The PR page is the live source for the resulting candidate HEAD and its exact-head checks.

## P0 — State, lease, and workstation

- GitHub `main`, fetched `origin/main`, and PR #78 base all resolved to the required base SHA. PR #78 is the only open PR on the repository at recheck.
- Context Lock verification: 16/16 unchanged canonical blobs match the authority base; 7/7 admission-delta paths match the promoted Issue #5 attestation. The five admitted files that differ from their pre-admission blobs are within the approved admission delta.
- Exclusive writer lease: Issue #5 comment [#6110755622](https://github.com/KayzenRoot/nex-engine/issues/5#issuecomment-6110755622). The two implementation reviewers completed read-only reviews; no reviewer modified the branch. The unrelated `opencode-cli` process did not reference this repository, the Work Order, or Godot/SCons.
- Workstation at recheck: C: had 16.35 GiB free; D: had 544.57 GiB free. The M00 minimum disk budget is 12 GiB. Artifacts and smoke logs are under `D:\NEX-M00-WO-001-LOCAL-20261011\`; no C: cleanup or deletion was performed. Local free RAM was 0.99 GiB before exact-head smokes and 1.20 GiB afterward, so no local source compilation was attempted.

## P0/P1/P2 — Windows standard-runner source build

The prior successful source-build run is [Actions run 38155659453](https://github.com/KayzenRoot/nex-engine/actions/runs/38155659453), exact build candidate `f4c7eed400b3d0b5efbc31e9aa280766e32870e5`. This run predates the bounded editor-exit correction; its artifacts are provenance inputs for the local diagnostic below, not final-head CI evidence.

| Measurement | Observed value |
|---|---:|
| Runner | GitHub-hosted `windows-2022` standard, public repository |
| Pre-build available RAM / commit headroom | 13.71 / 16.57 GiB |
| Pre-build free disk on runner D: | 147.01 GiB |
| CPUs / total physical memory | 4 / 15.99 GiB |
| Python / SCons | 3.12.10 / 4.11.1 |
| MSVC toolset / SCons family / Windows SDK | 14.44.35207 / 14.3 / 10.0.26100.0 |
| Build duration / result | 5160.516 s / exit 0 / no timeout |
| Samples during build | 173 |
| Minimum free physical RAM / commit headroom / disk | 5.02 / 7.52 / 143.36 GiB |

The configured 8 GiB RAM, 12 GiB commit, and 12 GiB disk gates passed at the required pre-build feasibility check. The resource monitor recorded lower RAM and commit headroom during compilation; the job completed without timeout or resource-stop classification. Those minima are preserved for the independent audit and are not represented as the pre-build values.

The command used `platform=windows target=editor arch=x86_64 -j1 lto=none debug_symbols=no accesskit=yes d3d12=yes msvc_version=14.3 mssdk_version=10.0.26100.0`, plus the verified dependency paths. The binary was built from official Godot tag `4.7.2-stable`, commit `ed1daf0bf001b61586d9930840f2f1394092c079`; source archive SHA-256 `a18ce0ccec3ecc40b0dd6c4f5132ca934e9fb7c2979717940ff32aee1eb35481`.

Pinned build inputs in the manifest: SCons wheel SHA-256 `454cef364348053422696e3d2ecb4fa593c96a624f955842eaaea64f95c8d11d`; AccessKit 0.22.3 SHA-256 `41b30b1382d03b225b6f7e8721269a32557a68065804f3797bdffc34a3273498`; Godot NIR 25.3.1-3 SHA-256 `f7796c97657fab348774906dc938bb46fbfd1e45434244141fc8886e5e4b5530`. MIT, Apache-2.0, and Chromium/Godot notices were included in the package. No Godot source/core/renderer files were changed.

### Artifacts and provenance

- Windows workflow artifact [11710477778](https://github.com/KayzenRoot/nex-engine/actions/runs/38155659453/artifacts/11710477778): 82,491,348 bytes, API digest `sha256:37527905cd27096ec8d4e0fc337aada2227396e521afb47a35b7189718a06377`; local copy matched.
- Nested source-build package SHA-256 `a5d8470eb067d72821b30f3ab91de4173417b9cd3f68fe47f07f6340b33ef489`.
- Windows build-log artifact [11710013500](https://github.com/KayzenRoot/nex-engine/actions/runs/38155659453/artifacts/11710013500): API digest `sha256:0652fa79069a4a30609b17a57879308619dc3d60448c9fafea4a501862229e51`.
- Ubuntu smoke artifact [11710586747](https://github.com/KayzenRoot/nex-engine/actions/runs/38155659453/artifacts/11710586747): API digest `sha256:992d325c1a4c7a00a0bfa1447f59b68e6509d9e4da817e143d0d71875f420ec0`.
- Compiled Windows GUI editor: 175,405,568 bytes, SHA-256 `c9f81b746fe00f4255d75a4ad0d7394fe43a08e6e228d585acd272b341175891`.
- Compiled Windows console editor: 301,056 bytes, SHA-256 `855440c5a47f90531fa872ba49cdd4ffe54cb77b5a98a97b2af763d70a07c4f5`.
- The package manifest, nested archive, notices, executable sizes/hashes, and API artifact digests were verified before local execution. All downloaded/extracted files remain on D:.

### Exact PR candidate `a58b86754fd1fd729296d085d6e10f610c238297`

- M00 Actions run [38163959546](https://github.com/KayzenRoot/nex-engine/actions/runs/38163959546): Windows feasibility job `114542520247`, Windows source-build/smoke job `114542559397` (exit 0, 5160.141 s), and Ubuntu official smoke/negative-tests job `114560719225` all succeeded. Exact-run preflight observed 13.58 GiB available physical RAM, 16.49 GiB commit headroom, 147.01 GiB free runner disk, 4 CPUs, Python 3.12.10, MSVC toolset 14.44.35207, and SDK 10.0.26100.0. During-build sampling (173 samples) reached minima of 6.74 GiB physical RAM, 9.25 GiB commit headroom, and 143.36 GiB free disk; the build completed without timeout.
- GEF smoke run [38163959535](https://github.com/KayzenRoot/nex-engine/actions/runs/38163959535): Windows job `114542520134` and Ubuntu job `114542520291` succeeded. Governance run [38163959599](https://github.com/KayzenRoot/nex-engine/actions/runs/38163959599): Source Pack job `114542520533` and PowerShell job `114542520616` succeeded. SonarCloud, Socket Project Report, and Socket Pull Request Alerts also succeeded on this candidate; see the live [PR checks](https://github.com/KayzenRoot/nex-engine/pull/78/checks).
- Windows build artifact [11714196180](https://github.com/KayzenRoot/nex-engine/actions/runs/38163959546/artifacts/11714196180): 82,490,645 bytes; API digest and downloaded ZIP SHA-256 both `9782b76f8bbb54cb10efa7bfd0c8b6d50d5ef66adcd9e0d2c576e5aac532807a`. The nested package SHA-256 matched its sidecar: `d65561f3847ac3b8bba8eec6b611c5faf29fb792397420e23a3f57b46033ea2b`. Manifest candidate SHA and source/tag/hash matched the exact candidate and pinned official inputs. Console and GUI executable hashes matched the manifest: `43a8adc387ecd53604aedefe32356d3731c6c93a0b9bad5f97443166099fbce6` and `363988968b764f411938edd80a56aa891a2850e912ac6bb9ede609d78c22bcc7`.
- Build logs artifact [11714161429](https://github.com/KayzenRoot/nex-engine/actions/runs/38163959546/artifacts/11714161429): 35,763 bytes; API digest/local ZIP SHA-256 `2227af2e98bfc98eb7bc9deeabe275abb6a3507c7bc540c301a552791471664a`. Ubuntu smoke artifact [11713293107](https://github.com/KayzenRoot/nex-engine/actions/runs/38163959546/artifacts/11713293107): 1,740 bytes; API digest/local ZIP SHA-256 `eba095c68c64502c737d9ff0b5cbec99cfea76d5fb14c1c4cd6364c452f16359`. All three ZIPs were checked for unsafe paths, symlinks, and encryption before extraction.

## P2-LOCAL — Compiled artifact on this Windows workstation

The console binary above was run from the verified package against the disposable project on D:. The corrected headless-editor invocation is the command explicitly allowed by Correction Delta 002: `--headless --editor --path <fixture> --quit-after 2`.

| Local run | Exit | Duration | Log SHA-256 |
|---|---:|---:|---|
| `--version` (`4.7.2.stable.custom_build.ed1daf0bf`) | 0 | 0.460 s | `96c9513577ee9a3cba007fb2996f9e447271f54f865f2cb70c5bc9f7dc6dd22d` |
| `--headless --editor ... --quit-after 2` | 0 | 4.445 s | `92ecae00832f3f3cf3f9fbfed5255f06e281f294e336a708a1c1145ea25e183b` |
| `--headless --path ... --quit-after 3` | 0 | 0.505 s | `a68a97aef91ab4fd5d42721b2235290b4b94d00d4c303cef1f27c5637a86cee5` |

The earlier `--quit` form initialized the editor but exited locally with `-1073741819` and `ERROR: Parameter "singleton" is null` (`windows-local-headless-editor.log`, SHA-256 `1347b4da06a7d9e6113f3b03be98b78da7656741a1a9713cc06dac754c8e1e9c`). The same form had exited 0 on the hosted runner. The script now uses `--quit-after 2`, and a regression test fixes that invocation. The corrected command passed against the verified compiled binary locally.

The GUI editor was also launched from that verified package; a window handle was observed, `CloseMainWindow` succeeded, and the process exited 0. Its log SHA-256 is `6d94a9591bbcbfaaa5c05e2fbaa50a8a45297bee99616e2dd20e49c75fd0d24`; it contains a shutdown warning `Scan thread aborted...`, retained here as a caveat rather than silently omitted.

The exact `a58b867...` artifact was separately downloaded by API and its outer digest, nested sidecar digest, manifest, and binary SHA-256 values were verified before execution. Against a disposable copy of the minimal project on D:, the exact-head console binary returned exit 0 for all three local invocations:

| Exact-head local run | Exit | Duration | Log SHA-256 |
|---|---:|---:|---|
| `--version` | 0 | 9.666 s | `ee9ff175ea8229e52467c9f5ede77164ea42892b0cef5aea3ed558e8e47fc0c9` |
| `--headless --editor --path <fixture> --quit-after 2` | 0 | 6.757 s | `e5d129a3fcfce7fcf77c12a3cf8f6855d7d3f59d6aff3bda1a69eed3b78de60b` |
| `--headless --path <fixture> --quit-after 3` | 0 | 0.423 s | `9bd3dec0f0c279ced0361f967d0b1c5e9192f75d0d524912a311b254223df0ef` |

The local exact-head unit suite also passed 14/14 on Python 3.13; log SHA-256 `dbde490747c2ecb8f4d3af222c789457d1854b4dcd36ac1ad0f72c92e12b42b0`. These exact-head results are for candidate `a58b867...`, not for the evidence-refresh commit that follows this snapshot.

All three corrected local smoke logs and the unit-test output are under `D:\NEX-M00-WO-001-LOCAL-20261011\windows-artifact-f4c7eed\local-smoke-after-correction-2\`. The unit log SHA-256 is `83f1dd0df098459854ea9c995e8083fc8db97590bae2dcbb7fa0aabf120b9827`.

## P3 — Unit, negative, and Ubuntu smoke evidence

`python -m unittest discover -s tests/m00 -v` passed **14/14** on the local Windows host (Python 3.13) at candidates `6d42e91...` and `a58b867...`. It covers pinned build flags, bad/oversized digests, missing executable/fixture, nonzero commands, permission failure, output-path preservation, and unsafe tar/ZIP members/symlinks, plus the bounded editor-exit command. The exact `a58b867...` Windows runner also ran the suite under locked Python 3.12.10.

The prior Ubuntu job [114535939954](https://github.com/KayzenRoot/nex-engine/actions/runs/38155659453/job/114535939954) passed official headless and negative tests on `f4c7eed...`; exact candidate `a58b867...` passed the same gate in job `114560719225`.

## External checks and exact-head gate

On exact candidate `a58b867...`, Windows feasibility, Windows source build/smoke, Ubuntu smoke/negative tests, GEF Windows/Ubuntu, NEX Governance Source Pack and PowerShell, Socket Project Report, Socket Pull Request Alerts, and SonarCloud were SUCCESS. The live [PR #78 checks](https://github.com/KayzenRoot/nex-engine/pull/78/checks) are authoritative for the evidence-refresh candidate created after this snapshot.

CodeRabbit's predecessor commit status says `Review skipped: draft pull request`; the bot comment confirms the draft was not reviewed, and there is no submitted review. The status label `SUCCESS` is therefore **not** evidence of a CodeRabbit review. GEF Windows/Ubuntu checks also did not run on the predecessor path set; this evidence/delta commit touches `.engineering/**`, which should trigger the GEF matrix on the new exact head. Do not mark the PR approved or merge while any required exact-head check/review is absent, pending, or failed.

The PR head is intentionally resolved from the live PR/checks link because this file is included in the candidate and cannot contain the hash of its own future commit. Candidate `a58b867...` has exact-head artifact and check evidence above; the evidence-refresh commit advances the candidate, so its exact SHA, new run/job links, artifact digest, and local smoke must be verified before declaring the stop condition. The PR description and Issue #5 closeout must then record that resulting exact HEAD.

## Boundary and remaining gates

- The source compilation ran on a standard Windows GitHub-hosted runner; the verified compiled artifact was executed locally. The canonical DoD requires a native Windows source build and Windows-local validation, and the Correction Delta authorizes this runner-plus-local-execution route. This does not claim that compilation occurred on the user's workstation.
- No checkpoint canonical file, `main`, Godot core/renderer, `.gef/**`, package manifest, secret, paid service, larger runner, or M01 component was changed or used.
- Billing was not queried. The workflow used only the standard Windows runner configured for the public repository; no larger/self-hosted runner or paid service was configured.
- For candidate `a58b867...`, exact-head Windows build/smoke, Ubuntu smoke, GEF Windows/Ubuntu, Governance, Socket x2, SonarCloud, artifact digest verification, local execution, and unit tests passed. CodeRabbit was skipped because PR #78 remained a draft; no external review or approval exists. The evidence-refresh candidate still requires fresh exact-head CI/security checks, artifact digest verification/local execution, CodeRabbit review after the PR is ready, thread resolution, and independent/Owner audit before declaring `NEX_M00_WO_001_READY_FOR_EXACT_HEAD_REVIEW`.
- No merge, checkpoint promotion, or M01 admission occurred.

## CodeRabbit correction review — 2026-10-11

CodeRabbit completed an actual review of candidate `a629d9911d348550b12870030c2437c0e1e45942` (review run `66c62bc3-d386-4f5f-9e5b-033bf929e4d8`; review comment `6113776892`). Its two inline findings and one summary nitpick were verified against the code:

- `run_logged` stopped checking its deadline after the direct process exited, so a descendant keeping stdout open could extend the step indefinitely. A real Windows regression reproduced a 6.18-second wait for a 2-second timeout. The working-tree correction now checks the deadline independently and stops waiting for the reader after the budget; the targeted regression returned in 2.15 seconds with exit code 0 and `timedOut=false` because the direct process itself had exited before its deadline.
- `windows_build` depended on dependency list order, hard-coded archive/source names, and did not consume the lock's `requiredFiles`. The correction resolves pins by name, derives names/roots from the pinned tag and URLs, and validates every required path from the lock without allowing traversal.
- Package and log artifacts retained for one day could expire before an audit. The workflow and lock were changed together to seven days, still a short-lived artifact window for the public-repository audit.

The no-op `except Exception: raise` in `download_verified` was also removed; failures still leave the isolated `.part` file because the code does not delete or replace it.

The targeted correction tests and full local M00 unit suite passed 17/17 on the working tree based on `a629d99`. At the time this entry was prepared, these follow-up changes had not yet received a new commit, exact-head CI, fresh artifacts, or a new CodeRabbit review. All checks and artifacts recorded above for `a629d99` are therefore historical for the follow-up candidate. Re-run the complete exact-head workflow, verify/download the artifact, repeat local Windows smoke, and inspect CodeRabbit/Socket/Sonar results before any readiness or checkpoint decision. This addendum does not authorize merge, checkpoint promotion, or M01.
