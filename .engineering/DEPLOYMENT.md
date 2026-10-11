# Deployment · Bootstrap Only
Status: CANONICAL_BOOTSTRAP_POLICY; GEF v1.1.2 post-merge verified in PR #74, effective in the new checkpoint only after promotion. No M00 implementation admitted.
There is NO deployable engine or playable game in this phase. Deployment means the validated installation of GEF v1.1.2 within a local Windows checkout and reproducible CI environment.
Official upstream: https://github.com/KayzenRoot/gef-bootstrap/releases/tag/v1.1.2 .
GEF CLI can be installed in an isolated Node 22 environment using `npm install --global @gef-bootstrap/cli@1.1.2` for operator smoke-testing; project/CI integration must establish its own reproducible pin without relying on user-global binaries.
Do not call source-clone V1.0.0 instructions current: v1.1.2 package is published.
No VPS, SaaS accounts, real authentication, engine binary release, game installer or cloud deployment.
