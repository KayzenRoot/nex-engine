# Legacy SonarCloud findings triage — PR #105

Read-only check on 2026-10-13: the public SonarCloud issue-search endpoint and GitHub check-run annotations for PR #105 were accessible. The three findings remain OPEN and are outside the Stage B write allowlist. All are `CODE_SMELL` findings; none is typed as a vulnerability or security hotspot. No unrelated files were changed to address them.

| Rule | Sonar severity / type | File:line | Finding | Stage B disposition |
|---|---|---|---|---|
| `python:S5778` | MAJOR / CODE_SMELL | `tests/ci/test_frame_observation_validator.py:120` | Exception test contains more than one invocation that may throw. | Existing test maintainability issue; outside allowlist. |
| `python:S9073` | MAJOR / CODE_SMELL | `tests/ci/test_frame_observation_validator.py:14` | Composite assertion should be split. | Existing test maintainability issue; outside allowlist. |
| `python:S3776` | CRITICAL / CODE_SMELL | `nex_bench/validate_frame_observation.py:72` | Cognitive Complexity 26 exceeds the configured limit 15. | Existing code maintainability issue; outside allowlist. `CRITICAL` is the Sonar issue severity; its type is still `CODE_SMELL`. |

The GitHub annotation source was check run `115074956851`; the exact annotation messages and paths were consistent with SonarCloud. This triage makes no claim about findings outside these three records or about the repository's overall security posture.
