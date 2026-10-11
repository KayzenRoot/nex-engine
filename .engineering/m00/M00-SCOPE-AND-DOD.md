# NEX M00 | Scope and Definition of Done
**Status:** owner-approved policy PROPOSED for promotion, execution NOT_ADMITTED until subsequent lock PR.
**Included:** official Godot native editor/runtime baseline 4.7.2-stable @ `ed1daf0bf001b61586d9930840f2f1394092c079`, release SHA256, license/third-party notices, Windows source build and minimal runtime/editor smoke, Ubuntu headless CI, manifest and evidence.
**Excluded:** shaders/renderer customizations, game feature, MMOs, 2D/2.5D improvements, M01 performance experiments, 1080p/60 or 120 claims, core fork patches, GDExtension ABI changes, cloud GPU or paid services.
**DoD:**
1. Owner decision and governance PR + execution lock in authoritative main, fingerprints checked and Steward exclusive lease.
2. Exact upstream tag commit and archive digest validated on bytes, source attribution, compiler/SCons/build flags pinned and manifest committed, no unapproved binary vendoring.
3. Native Windows Godot source build and version/editor/minimal-scene smoke proven with exit codes and logs, plus Ubuntu headless CI smoke at exact HEAD (official binary smoke alone ≠ source build proof).
4. Safe failure of missing/bad checksum, invalid toolchain, untrusted executable, stale locks. No secrets, no forbidden path edits or uncontrolled install scripts.
5. CodeRabbit/Socket/Sonar/CI applicable gate SUCCESS, no unresolved HIGH/CRITICAL, Evidence Bundle and owner/steward exact HEAD audit, squash merge and post-merge verification before promotion.
6. M00 says nothing about FPS parity, native engine improvements or release completeness; M01 builds visual/frametime test fixtures only under its own approved WO.
**Stop:** implementation PR ready for independent review, not automatic merge or M01.
