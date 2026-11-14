# NEX M06 · Performance advisories (full dataset) — RTX 5050

**Status:** `ADVISORIES_DERIVED_FROM_MEASURED_OBSERVATIONS / SINGLE_SESSION / NO_FPS_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `docs/benchmarks/m06/observations/m09-observations-full.v1.json` · **Observações:** 144

## Resumo

- Bottlenecks: {'pacing': 144}.
- Headroom de render: 3.327–4.009 ms.
- Maior participação GPU no frame: 21.05%.
- Frame alvo a 240 fps: 4.167 ms.

## Advisórios

| Observação | Cena | Proxies | Resolução | GPU ms | CPU ms | Pacing ms | Headroom ms | GPU % | CPU % | Bottleneck |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| m09-preset-ab-001 | preset-ab | 200 | 1280×720 | 0.147 | 0.357 | 4.199 | 3.842 | 3.50 | 8.50 | pacing |
| m09-preset-ab-002 | preset-ab | 200 | 1280×720 | 0.746 | 0.467 | 4.222 | 3.476 | 17.67 | 11.06 | pacing |
| m09-preset-ab-003 | preset-ab | 200 | 1280×720 | 0.147 | 0.366 | 4.204 | 3.838 | 3.50 | 8.71 | pacing |
| m09-preset-ab-004 | preset-ab | 200 | 1280×720 | 0.881 | 0.472 | 4.229 | 3.348 | 20.83 | 11.16 | pacing |
| m09-preset-ab-005 | preset-ab | 200 | 1280×720 | 0.152 | 0.346 | 4.216 | 3.870 | 3.61 | 8.21 | pacing |
| m09-preset-ab-006 | preset-ab | 200 | 1280×720 | 0.887 | 0.529 | 4.214 | 3.327 | 21.05 | 12.55 | pacing |
| m09-proxy-scaling-001 | preset-ab | 25 | 1280×720 | 0.128 | 0.298 | 4.249 | 3.951 | 3.01 | 7.01 | pacing |
| m09-proxy-scaling-002 | preset-ab | 25 | 1280×720 | 0.782 | 0.389 | 4.287 | 3.505 | 18.24 | 9.07 | pacing |
| m09-proxy-scaling-003 | preset-ab | 25 | 1280×720 | 0.127 | 0.292 | 4.268 | 3.976 | 2.98 | 6.84 | pacing |
| m09-proxy-scaling-004 | preset-ab | 25 | 1280×720 | 0.771 | 0.376 | 4.259 | 3.488 | 18.10 | 8.83 | pacing |
| m09-proxy-scaling-005 | preset-ab | 25 | 1280×720 | 0.128 | 0.305 | 4.242 | 3.937 | 3.02 | 7.19 | pacing |
| m09-proxy-scaling-006 | preset-ab | 25 | 1280×720 | 0.774 | 0.382 | 4.269 | 3.495 | 18.13 | 8.95 | pacing |
| m09-proxy-scaling-007 | preset-ab | 100 | 1280×720 | 0.138 | 0.310 | 4.278 | 3.968 | 3.23 | 7.25 | pacing |
| m09-proxy-scaling-008 | preset-ab | 100 | 1280×720 | 0.836 | 0.418 | 4.275 | 3.439 | 19.56 | 9.78 | pacing |
| m09-proxy-scaling-009 | preset-ab | 100 | 1280×720 | 0.140 | 0.323 | 4.264 | 3.941 | 3.28 | 7.58 | pacing |
| m09-proxy-scaling-010 | preset-ab | 100 | 1280×720 | 0.824 | 0.444 | 4.249 | 3.425 | 19.39 | 10.45 | pacing |
| m09-proxy-scaling-011 | preset-ab | 100 | 1280×720 | 0.139 | 0.302 | 4.254 | 3.952 | 3.27 | 7.10 | pacing |
| m09-proxy-scaling-012 | preset-ab | 100 | 1280×720 | 0.833 | 0.449 | 4.274 | 3.441 | 19.49 | 10.51 | pacing |
| m09-proxy-scaling-013 | preset-ab | 200 | 1280×720 | 0.152 | 0.374 | 4.289 | 3.915 | 3.54 | 8.72 | pacing |
| m09-proxy-scaling-014 | preset-ab | 200 | 1280×720 | 0.876 | 0.457 | 4.263 | 3.387 | 20.55 | 10.72 | pacing |
| m09-proxy-scaling-015 | preset-ab | 200 | 1280×720 | 0.153 | 0.380 | 4.243 | 3.863 | 3.61 | 8.96 | pacing |
| m09-proxy-scaling-016 | preset-ab | 200 | 1280×720 | 0.879 | 0.449 | 4.256 | 3.377 | 20.65 | 10.55 | pacing |
| m09-proxy-scaling-017 | preset-ab | 200 | 1280×720 | 0.150 | 0.359 | 4.274 | 3.915 | 3.51 | 8.40 | pacing |
| m09-proxy-scaling-018 | preset-ab | 200 | 1280×720 | 0.879 | 0.480 | 4.251 | 3.372 | 20.68 | 11.29 | pacing |
| m09-m01-ab-001 | m01-corridor | 100 | 1280×720 | 0.086 | 0.328 | 4.208 | 3.880 | 2.04 | 7.79 | pacing |
| m09-m01-ab-002 | m01-corridor | 100 | 1280×720 | 0.542 | 0.475 | 4.210 | 3.668 | 12.87 | 11.28 | pacing |
| m09-m01-ab-003 | m01-corridor | 100 | 1280×720 | 0.088 | 0.370 | 4.208 | 3.838 | 2.09 | 8.79 | pacing |
| m09-m01-ab-004 | m01-corridor | 100 | 1280×720 | 0.421 | 0.452 | 4.227 | 3.775 | 9.96 | 10.69 | pacing |
| m09-m01-ab-005 | m01-corridor | 100 | 1280×720 | 0.089 | 0.347 | 4.209 | 3.862 | 2.11 | 8.24 | pacing |
| m09-m01-ab-006 | m01-corridor | 100 | 1280×720 | 0.423 | 0.429 | 4.218 | 3.789 | 10.03 | 10.17 | pacing |
| m09-m01-ab-007 | m01-arena | 100 | 1280×720 | 0.109 | 0.320 | 4.217 | 3.897 | 2.58 | 7.59 | pacing |
| m09-m01-ab-008 | m01-arena | 100 | 1280×720 | 0.462 | 0.416 | 4.200 | 3.738 | 11.00 | 9.90 | pacing |
| m09-m01-ab-009 | m01-arena | 100 | 1280×720 | 0.109 | 0.345 | 4.218 | 3.873 | 2.58 | 8.18 | pacing |
| m09-m01-ab-010 | m01-arena | 100 | 1280×720 | 0.462 | 0.446 | 4.231 | 3.769 | 10.92 | 10.54 | pacing |
| m09-m01-ab-011 | m01-arena | 100 | 1280×720 | 0.117 | 0.369 | 4.231 | 3.862 | 2.77 | 8.72 | pacing |
| m09-m01-ab-012 | m01-arena | 100 | 1280×720 | 0.462 | 0.435 | 4.242 | 3.780 | 10.89 | 10.25 | pacing |
| m09-m01-ab-013 | m01-city | 100 | 1280×720 | 0.084 | 0.321 | 4.239 | 3.918 | 1.98 | 7.57 | pacing |
| m09-m01-ab-014 | m01-city | 100 | 1280×720 | 0.362 | 0.431 | 4.277 | 3.846 | 8.46 | 10.08 | pacing |
| m09-m01-ab-015 | m01-city | 100 | 1280×720 | 0.084 | 0.325 | 4.285 | 3.960 | 1.96 | 7.58 | pacing |
| m09-m01-ab-016 | m01-city | 100 | 1280×720 | 0.363 | 0.438 | 4.240 | 3.802 | 8.56 | 10.33 | pacing |
| m09-m01-ab-017 | m01-city | 100 | 1280×720 | 0.083 | 0.325 | 4.284 | 3.959 | 1.94 | 7.59 | pacing |
| m09-m01-ab-018 | m01-city | 100 | 1280×720 | 0.362 | 0.432 | 4.270 | 3.838 | 8.48 | 10.12 | pacing |
| m09-res-scaling-001 | m01-arena | 100 | 960×540 | 0.096 | 0.318 | 4.225 | 3.907 | 2.27 | 7.53 | pacing |
| m09-res-scaling-002 | m01-arena | 100 | 960×540 | 0.317 | 0.444 | 4.203 | 3.759 | 7.54 | 10.56 | pacing |
| m09-res-scaling-003 | m01-arena | 100 | 960×540 | 0.096 | 0.322 | 4.202 | 3.880 | 2.28 | 7.66 | pacing |
| m09-res-scaling-004 | m01-arena | 100 | 960×540 | 0.317 | 0.443 | 4.201 | 3.758 | 7.55 | 10.55 | pacing |
| m09-res-scaling-005 | m01-arena | 100 | 960×540 | 0.096 | 0.325 | 4.202 | 3.877 | 2.28 | 7.73 | pacing |
| m09-res-scaling-006 | m01-arena | 100 | 960×540 | 0.316 | 0.430 | 4.204 | 3.774 | 7.52 | 10.23 | pacing |
| m09-res-scaling-007 | m01-arena | 100 | 1280×720 | 0.106 | 0.328 | 4.250 | 3.922 | 2.49 | 7.72 | pacing |
| m09-res-scaling-008 | m01-arena | 100 | 1280×720 | 0.460 | 0.438 | 4.255 | 3.795 | 10.81 | 10.29 | pacing |
| m09-res-scaling-009 | m01-arena | 100 | 1280×720 | 0.107 | 0.337 | 4.257 | 3.920 | 2.51 | 7.92 | pacing |
| m09-res-scaling-010 | m01-arena | 100 | 1280×720 | 0.461 | 0.434 | 4.241 | 3.780 | 10.87 | 10.23 | pacing |
| m09-res-scaling-011 | m01-arena | 100 | 1280×720 | 0.106 | 0.319 | 4.241 | 3.922 | 2.50 | 7.52 | pacing |
| m09-res-scaling-012 | m01-arena | 100 | 1280×720 | 0.459 | 0.440 | 4.257 | 3.798 | 10.78 | 10.34 | pacing |
| m09-res-scaling-013 | m01-arena | 100 | 1920×1080 | 0.156 | 0.344 | 4.241 | 3.897 | 3.68 | 8.11 | pacing |
| m09-res-scaling-014 | m01-arena | 100 | 1920×1080 | 0.826 | 0.446 | 4.273 | 3.447 | 19.33 | 10.44 | pacing |
| m09-res-scaling-015 | m01-arena | 100 | 1920×1080 | 0.157 | 0.329 | 4.242 | 3.913 | 3.70 | 7.76 | pacing |
| m09-res-scaling-016 | m01-arena | 100 | 1920×1080 | 0.827 | 0.455 | 4.263 | 3.436 | 19.40 | 10.67 | pacing |
| m09-res-scaling-017 | m01-arena | 100 | 1920×1080 | 0.156 | 0.329 | 4.292 | 3.963 | 3.63 | 7.67 | pacing |
| m09-res-scaling-018 | m01-arena | 100 | 1920×1080 | 0.826 | 0.454 | 4.290 | 3.464 | 19.25 | 10.58 | pacing |
| m09-interaction-001 | m01-arena | 50 | 960×540 | 0.096 | 0.231 | 4.240 | 4.009 | 2.26 | 5.45 | pacing |
| m09-interaction-002 | m01-arena | 50 | 960×540 | 0.304 | 0.299 | 4.242 | 3.938 | 7.17 | 7.05 | pacing |
| m09-interaction-003 | m01-arena | 50 | 960×540 | 0.096 | 0.233 | 4.240 | 4.007 | 2.26 | 5.50 | pacing |
| m09-interaction-004 | m01-arena | 50 | 960×540 | 0.308 | 0.304 | 4.240 | 3.932 | 7.26 | 7.17 | pacing |
| m09-interaction-005 | m01-arena | 50 | 960×540 | 0.096 | 0.248 | 4.242 | 3.994 | 2.26 | 5.85 | pacing |
| m09-interaction-006 | m01-arena | 50 | 960×540 | 0.307 | 0.305 | 4.242 | 3.935 | 7.24 | 7.19 | pacing |
| m09-interaction-007 | m01-arena | 50 | 1920×1080 | 0.140 | 0.236 | 4.242 | 4.006 | 3.30 | 5.56 | pacing |
| m09-interaction-008 | m01-arena | 50 | 1920×1080 | 0.820 | 0.306 | 4.240 | 3.420 | 19.34 | 7.22 | pacing |
| m09-interaction-009 | m01-arena | 50 | 1920×1080 | 0.144 | 0.236 | 4.241 | 4.005 | 3.40 | 5.56 | pacing |
| m09-interaction-010 | m01-arena | 50 | 1920×1080 | 0.820 | 0.305 | 4.243 | 3.423 | 19.33 | 7.19 | pacing |
| m09-interaction-011 | m01-arena | 50 | 1920×1080 | 0.144 | 0.238 | 4.241 | 4.003 | 3.40 | 5.61 | pacing |
| m09-interaction-012 | m01-arena | 50 | 1920×1080 | 0.819 | 0.314 | 4.240 | 3.421 | 19.32 | 7.41 | pacing |
| m09-interaction-013 | m01-arena | 100 | 960×540 | 0.097 | 0.253 | 4.242 | 3.989 | 2.29 | 5.96 | pacing |
| m09-interaction-014 | m01-arena | 100 | 960×540 | 0.314 | 0.320 | 4.240 | 3.920 | 7.41 | 7.55 | pacing |
| m09-interaction-015 | m01-arena | 100 | 960×540 | 0.096 | 0.239 | 4.240 | 4.001 | 2.26 | 5.64 | pacing |
| m09-interaction-016 | m01-arena | 100 | 960×540 | 0.314 | 0.323 | 4.240 | 3.917 | 7.41 | 7.62 | pacing |
| m09-interaction-017 | m01-arena | 100 | 960×540 | 0.096 | 0.247 | 4.240 | 3.993 | 2.26 | 5.83 | pacing |
| m09-interaction-018 | m01-arena | 100 | 960×540 | 0.316 | 0.318 | 4.242 | 3.924 | 7.45 | 7.50 | pacing |
| m09-interaction-019 | m01-arena | 100 | 1920×1080 | 0.145 | 0.246 | 4.243 | 3.997 | 3.42 | 5.80 | pacing |
| m09-interaction-020 | m01-arena | 100 | 1920×1080 | 0.826 | 0.333 | 4.243 | 3.417 | 19.47 | 7.85 | pacing |
| m09-interaction-021 | m01-arena | 100 | 1920×1080 | 0.144 | 0.242 | 4.243 | 4.001 | 3.39 | 5.70 | pacing |
| m09-interaction-022 | m01-arena | 100 | 1920×1080 | 0.826 | 0.330 | 4.246 | 3.420 | 19.45 | 7.77 | pacing |
| m09-interaction-023 | m01-arena | 100 | 1920×1080 | 0.143 | 0.246 | 4.242 | 3.996 | 3.37 | 5.80 | pacing |
| m09-interaction-024 | m01-arena | 100 | 1920×1080 | 0.825 | 0.324 | 4.241 | 3.416 | 19.45 | 7.64 | pacing |
| m09-cross-scene-001 | m01-corridor | 50 | 960×540 | 0.072 | 0.310 | 4.282 | 3.972 | 1.68 | 7.24 | pacing |
| m09-cross-scene-002 | m01-corridor | 50 | 960×540 | 0.280 | 0.427 | 4.252 | 3.825 | 6.59 | 10.04 | pacing |
| m09-cross-scene-003 | m01-corridor | 50 | 960×540 | 0.071 | 0.334 | 4.275 | 3.941 | 1.66 | 7.81 | pacing |
| m09-cross-scene-004 | m01-corridor | 50 | 960×540 | 0.280 | 0.438 | 4.252 | 3.814 | 6.59 | 10.30 | pacing |
| m09-cross-scene-005 | m01-corridor | 50 | 960×540 | 0.071 | 0.311 | 4.245 | 3.934 | 1.67 | 7.33 | pacing |
| m09-cross-scene-006 | m01-corridor | 50 | 960×540 | 0.276 | 0.414 | 4.265 | 3.851 | 6.47 | 9.71 | pacing |
| m09-cross-scene-007 | m01-corridor | 50 | 1920×1080 | 0.137 | 0.330 | 4.284 | 3.954 | 3.20 | 7.70 | pacing |
| m09-cross-scene-008 | m01-corridor | 50 | 1920×1080 | 0.784 | 0.426 | 4.242 | 3.458 | 18.48 | 10.04 | pacing |
| m09-cross-scene-009 | m01-corridor | 50 | 1920×1080 | 0.136 | 0.327 | 4.242 | 3.915 | 3.21 | 7.71 | pacing |
| m09-cross-scene-010 | m01-corridor | 50 | 1920×1080 | 0.783 | 0.425 | 4.297 | 3.514 | 18.22 | 9.89 | pacing |
| m09-cross-scene-011 | m01-corridor | 50 | 1920×1080 | 0.136 | 0.328 | 4.295 | 3.967 | 3.17 | 7.64 | pacing |
| m09-cross-scene-012 | m01-corridor | 50 | 1920×1080 | 0.784 | 0.420 | 4.242 | 3.458 | 18.48 | 9.90 | pacing |
| m09-cross-scene-013 | m01-corridor | 100 | 960×540 | 0.071 | 0.332 | 4.265 | 3.933 | 1.66 | 7.78 | pacing |
| m09-cross-scene-014 | m01-corridor | 100 | 960×540 | 0.280 | 0.442 | 4.252 | 3.810 | 6.59 | 10.40 | pacing |
| m09-cross-scene-015 | m01-corridor | 100 | 960×540 | 0.071 | 0.337 | 4.276 | 3.939 | 1.66 | 7.88 | pacing |
| m09-cross-scene-016 | m01-corridor | 100 | 960×540 | 0.279 | 0.441 | 4.293 | 3.852 | 6.50 | 10.27 | pacing |
| m09-cross-scene-017 | m01-corridor | 100 | 960×540 | 0.072 | 0.339 | 4.289 | 3.950 | 1.68 | 7.90 | pacing |
| m09-cross-scene-018 | m01-corridor | 100 | 960×540 | 0.282 | 0.448 | 4.294 | 3.846 | 6.57 | 10.43 | pacing |
| m09-cross-scene-019 | m01-corridor | 100 | 1920×1080 | 0.138 | 0.396 | 4.295 | 3.899 | 3.21 | 9.22 | pacing |
| m09-cross-scene-020 | m01-corridor | 100 | 1920×1080 | 0.790 | 0.451 | 4.259 | 3.469 | 18.55 | 10.59 | pacing |
| m09-cross-scene-021 | m01-corridor | 100 | 1920×1080 | 0.140 | 0.338 | 4.252 | 3.914 | 3.29 | 7.95 | pacing |
| m09-cross-scene-022 | m01-corridor | 100 | 1920×1080 | 0.794 | 0.449 | 4.292 | 3.498 | 18.50 | 10.46 | pacing |
| m09-cross-scene-023 | m01-corridor | 100 | 1920×1080 | 0.140 | 0.329 | 4.288 | 3.959 | 3.26 | 7.67 | pacing |
| m09-cross-scene-024 | m01-corridor | 100 | 1920×1080 | 0.790 | 0.451 | 4.249 | 3.459 | 18.59 | 10.61 | pacing |
| m09-cross-scene-025 | m01-city | 50 | 960×540 | 0.068 | 0.317 | 4.243 | 3.926 | 1.60 | 7.47 | pacing |
| m09-cross-scene-026 | m01-city | 50 | 960×540 | 0.237 | 0.405 | 4.263 | 3.858 | 5.56 | 9.50 | pacing |
| m09-cross-scene-027 | m01-city | 50 | 960×540 | 0.068 | 0.306 | 4.269 | 3.963 | 1.59 | 7.17 | pacing |
| m09-cross-scene-028 | m01-city | 50 | 960×540 | 0.235 | 0.407 | 4.241 | 3.834 | 5.54 | 9.60 | pacing |
| m09-cross-scene-029 | m01-city | 50 | 960×540 | 0.068 | 0.306 | 4.261 | 3.955 | 1.60 | 7.18 | pacing |
| m09-cross-scene-030 | m01-city | 50 | 960×540 | 0.235 | 0.411 | 4.250 | 3.839 | 5.53 | 9.67 | pacing |
| m09-cross-scene-031 | m01-city | 50 | 1920×1080 | 0.122 | 0.321 | 4.241 | 3.920 | 2.88 | 7.57 | pacing |
| m09-cross-scene-032 | m01-city | 50 | 1920×1080 | 0.684 | 0.413 | 4.294 | 3.610 | 15.93 | 9.62 | pacing |
| m09-cross-scene-033 | m01-city | 50 | 1920×1080 | 0.122 | 0.314 | 4.276 | 3.962 | 2.85 | 7.34 | pacing |
| m09-cross-scene-034 | m01-city | 50 | 1920×1080 | 0.685 | 0.422 | 4.294 | 3.609 | 15.95 | 9.83 | pacing |
| m09-cross-scene-035 | m01-city | 50 | 1920×1080 | 0.122 | 0.320 | 4.243 | 3.923 | 2.88 | 7.54 | pacing |
| m09-cross-scene-036 | m01-city | 50 | 1920×1080 | 0.686 | 0.418 | 4.298 | 3.612 | 15.96 | 9.73 | pacing |
| m09-cross-scene-037 | m01-city | 100 | 960×540 | 0.069 | 0.323 | 4.247 | 3.924 | 1.62 | 7.61 | pacing |
| m09-cross-scene-038 | m01-city | 100 | 960×540 | 0.241 | 0.429 | 4.291 | 3.862 | 5.62 | 10.00 | pacing |
| m09-cross-scene-039 | m01-city | 100 | 960×540 | 0.069 | 0.334 | 4.245 | 3.911 | 1.63 | 7.87 | pacing |
| m09-cross-scene-040 | m01-city | 100 | 960×540 | 0.242 | 0.423 | 4.251 | 3.828 | 5.69 | 9.95 | pacing |
| m09-cross-scene-041 | m01-city | 100 | 960×540 | 0.069 | 0.326 | 4.251 | 3.925 | 1.62 | 7.67 | pacing |
| m09-cross-scene-042 | m01-city | 100 | 960×540 | 0.241 | 0.438 | 4.248 | 3.810 | 5.67 | 10.31 | pacing |
| m09-cross-scene-043 | m01-city | 100 | 1920×1080 | 0.117 | 0.324 | 4.281 | 3.957 | 2.73 | 7.57 | pacing |
| m09-cross-scene-044 | m01-city | 100 | 1920×1080 | 0.693 | 0.441 | 4.247 | 3.554 | 16.32 | 10.38 | pacing |
| m09-cross-scene-045 | m01-city | 100 | 1920×1080 | 0.124 | 0.330 | 4.301 | 3.971 | 2.88 | 7.67 | pacing |
| m09-cross-scene-046 | m01-city | 100 | 1920×1080 | 0.691 | 0.444 | 4.242 | 3.551 | 16.29 | 10.47 | pacing |
| m09-cross-scene-047 | m01-city | 100 | 1920×1080 | 0.124 | 0.330 | 4.274 | 3.944 | 2.90 | 7.72 | pacing |
| m09-cross-scene-048 | m01-city | 100 | 1920×1080 | 0.691 | 0.445 | 4.263 | 3.572 | 16.21 | 10.44 | pacing |
| m09-interaction-200-001 | m01-arena | 200 | 960×540 | 0.099 | 0.357 | 4.261 | 3.904 | 2.32 | 8.38 | pacing |
| m09-interaction-200-002 | m01-arena | 200 | 960×540 | 0.322 | 0.506 | 4.264 | 3.758 | 7.55 | 11.87 | pacing |
| m09-interaction-200-003 | m01-arena | 200 | 960×540 | 0.098 | 0.356 | 4.247 | 3.891 | 2.31 | 8.38 | pacing |
| m09-interaction-200-004 | m01-arena | 200 | 960×540 | 0.323 | 0.503 | 4.265 | 3.762 | 7.57 | 11.79 | pacing |
| m09-interaction-200-005 | m01-arena | 200 | 960×540 | 0.098 | 0.359 | 4.247 | 3.888 | 2.31 | 8.45 | pacing |
| m09-interaction-200-006 | m01-arena | 200 | 960×540 | 0.322 | 0.496 | 4.263 | 3.767 | 7.55 | 11.63 | pacing |
| m09-interaction-200-007 | m01-arena | 200 | 1920×1080 | 0.157 | 0.361 | 4.275 | 3.914 | 3.67 | 8.44 | pacing |
| m09-interaction-200-008 | m01-arena | 200 | 1920×1080 | 0.846 | 0.518 | 4.248 | 3.402 | 19.92 | 12.19 | pacing |
| m09-interaction-200-009 | m01-arena | 200 | 1920×1080 | 0.157 | 0.369 | 4.289 | 3.920 | 3.66 | 8.60 | pacing |
| m09-interaction-200-010 | m01-arena | 200 | 1920×1080 | 0.845 | 0.520 | 4.296 | 3.451 | 19.67 | 12.10 | pacing |
| m09-interaction-200-011 | m01-arena | 200 | 1920×1080 | 0.157 | 0.353 | 4.289 | 3.936 | 3.66 | 8.23 | pacing |
| m09-interaction-200-012 | m01-arena | 200 | 1920×1080 | 0.844 | 0.506 | 4.294 | 3.450 | 19.66 | 11.78 | pacing |

## Recomendações

- `m09-preset-ab-001`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-preset-ab-002`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-preset-ab-003`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-preset-ab-004`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-preset-ab-005`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-preset-ab-006`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-001`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-002`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-003`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-004`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-005`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-006`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-007`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-008`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-009`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-010`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-011`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-012`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-013`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-014`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-015`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-016`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-017`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-proxy-scaling-018`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-001`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-002`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-003`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-004`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-005`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-006`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-007`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-008`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-009`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-010`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-011`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-012`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-013`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-014`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-015`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-016`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-017`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-m01-ab-018`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-001`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-002`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-003`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-004`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-005`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-006`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-007`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-008`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-009`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-010`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-011`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-012`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-013`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-014`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-015`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-016`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-017`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-res-scaling-018`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-001`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-002`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-003`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-004`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-005`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-006`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-007`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-008`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-009`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-010`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-011`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-012`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-013`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-014`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-015`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-016`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-017`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-018`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-019`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-020`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-021`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-022`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-023`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-024`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-001`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-002`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-003`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-004`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-005`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-006`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-007`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-008`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-009`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-010`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-011`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-012`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-013`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-014`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-015`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-016`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-017`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-018`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-019`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-020`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-021`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-022`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-023`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-024`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-025`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-026`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-027`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-028`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-029`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-030`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-031`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-032`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-033`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-034`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-035`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-036`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-037`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-038`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-039`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-040`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-041`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-042`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-043`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-044`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-045`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-046`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-047`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-cross-scene-048`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-200-001`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-200-002`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-200-003`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-200-004`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-200-005`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-200-006`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-200-007`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-200-008`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-200-009`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-200-010`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-200-011`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).
- `m09-interaction-200-012`: re-measure with a higher cap or a heavier workload before optimizing (the pacing cap dominates; render headroom does not prove GPU capacity at a lower cap; risco LOW; requer nova medição).

## Limitações

- advisories are derived from one session on one RTX 5050; no cross-device or cross-session generalization
- renderer allocation bytes are session history, not device VRAM
- GPU render timing can describe earlier work and is not frame-aligned
- headroom is relative to this capped run and does not prove capacity at another cap or workload
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m06/tools/build_advisories.py`; não é benchmark nem claim de ganho.
