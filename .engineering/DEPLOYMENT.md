# Deployment · Bootstrap Only
Status: CANONICAL_BOOTSTRAP_POLICY_AND_M00_NATIVE_BASELINE_VERIFIED_AFTER_CHECKPOINT_PROMOTION; GEF v1.1.2 and M00 source-build CI verified, but no distributable NEX Engine release is approved.
There is NO deployable engine or playable game in this phase. Deployment means the validated installation of GEF v1.1.2 within a local Windows checkout and reproducible CI environment.
Official upstream: https://github.com/KayzenRoot/gef-bootstrap/releases/tag/v1.1.2 .
GEF CLI can be installed in an isolated Node 22 environment using `npm install --global @gef-bootstrap/cli@1.1.2` for operator smoke-testing; project/CI integration must establish its own reproducible pin without relying on user-global binaries.
Do not call source-clone V1.0.0 instructions current: v1.1.2 package is published.
No VPS, SaaS accounts, real authentication, engine binary release, game installer or cloud deployment.

## M00 native baseline availability
- PR #78 compiled unmodified Godot `4.7.2-stable` on the GitHub-hosted standard Windows runner, produced SHA-verified editor/console candidate binaries and passed local/CI smoke. M00 implementation squash SHA: `0c6cdbfc13bd0c1c8e80d293f7da7f2302027861`; source evidence `.engineering/evidence/NEX-M00-WO-001-POSTMERGE-EVIDENCE.md`.
- Candidate binary inside short-retention CI artifact is NOT an official packaged NEX Engine release. No installer, signing, production deployment, distribution/marketing, benchmark or custom renderer is authorized. M01 NOT_ADMITTED.
