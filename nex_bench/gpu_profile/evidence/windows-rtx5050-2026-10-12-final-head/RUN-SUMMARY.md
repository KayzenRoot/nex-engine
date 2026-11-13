# Windows RTX 5050 GPU Profiler — run summary

- Implementation source SHA: `a1b1e1df89a52d219d7d5f328f011d2c6f3c657a`
- Each run: 2 s warmup + at least 30 s observation; 2,251 valid GPU and CPU samples; all records passed `validate_gpu_profile.py`.
- Fixed settings: Godot 4.7.2 stable (`ed1daf0bf`), Windows, Forward+, Vulkan, VSync mode 1, density ladder.
- Observed FPS stayed around 75 and was VSync-limited. These values are local observations, not benchmark claims or comparisons.
- GPU_RENDER_MS and CPU_RENDER_MS are Godot per-viewport measurements. Renderer allocation is not total VRAM. Device WDDM snapshots are device-wide and are not attributed to the Godot process.

## Individual runs

| Run ID | Scenario | Observed (s) | GPU n | GPU p50 (ms) | GPU p95 (ms) | GPU p99 (ms) | CPU p95 (ms) | 1% low (FPS) | VSync |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `1791860258-507813102` | 25 combined | 30.013 | 2251 | 0.210 | 0.214 | 0.224 | 0.362 | 75.00 | 1 |
| `1791860299-548824658` | 25 combined | 30.004 | 2251 | 0.211 | 0.214 | 0.330 | 0.311 | 75.00 | 1 |
| `1791860341-590174382` | 25 combined | 30.013 | 2251 | 0.209 | 0.213 | 0.363 | 0.372 | 75.00 | 1 |
| `1791859822-71220418` | 25 geometry | 30.004 | 2251 | 0.120 | 0.122 | 0.140 | 0.283 | 75.00 | 1 |
| `1791859868-117550894` | 25 geometry | 30.013 | 2251 | 0.120 | 0.122 | 0.293 | 0.299 | 75.00 | 1 |
| `1791859910-159431780` | 25 geometry | 30.013 | 2251 | 0.120 | 0.122 | 0.145 | 0.297 | 75.00 | 1 |
| `1791859955-204540384` | 100 geometry | 30.013 | 2251 | 0.192 | 0.194 | 0.203 | 0.290 | 75.00 | 1 |
| `1791859995-244498915` | 100 geometry | 30.013 | 2251 | 0.192 | 0.195 | 0.213 | 0.315 | 75.00 | 1 |
| `1791860037-286848127` | 100 geometry | 30.013 | 2251 | 0.192 | 0.195 | 0.212 | 0.324 | 75.00 | 1 |
| `1791860081-330618429` | 200 geometry | 30.004 | 2251 | 0.293 | 0.296 | 0.386 | 0.341 | 75.00 | 1 |
| `1791860122-371722372` | 200 geometry | 30.013 | 2251 | 0.293 | 0.296 | 0.327 | 0.361 | 75.00 | 1 |
| `1791860162-411747360` | 200 geometry | 30.013 | 2251 | 0.293 | 0.296 | 0.305 | 0.360 | 75.00 | 1 |

## Scenario spread (three sequential runs each)

| Scenario | Runs | GPU p95 mean (ms) | GPU p95 range (ms) | GPU p95 sample SD (ms) | CPU p95 mean (ms) | 1% low mean (FPS) |
|---|---:|---:|---:|---:|---:|---:|
| 25 geometry | 3 | 0.1220 | 0.1220–0.1220 | 0.0000 | 0.2930 | 75.00 |
| 100 geometry | 3 | 0.1947 | 0.1940–0.1950 | 0.0006 | 0.3097 | 75.00 |
| 200 geometry | 3 | 0.2960 | 0.2960–0.2960 | 0.0000 | 0.3540 | 75.00 |
| 25 combined | 3 | 0.2137 | 0.2130–0.2140 | 0.0006 | 0.3483 | 75.00 |

The spread is reported descriptively across these same-machine runs. VSync was enabled, no uncapped comparison was authorized, and power/temperature state may affect samples; do not interpret these values as a performance improvement or a cross-device comparison.
