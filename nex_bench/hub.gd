extends Node3D

# One native Godot entry point for existing S01, S03 and S04 implementations.
# S03's Python CLI remains the reference for offline PNG reports.
const SCENE_PATHS := [
    "res://scenes/base/corridor_static.tscn",
    "res://scenes/base/arena_combat.tscn",
    "res://scenes/base/dense_city.tscn",
]
const SCENE_LABELS := ["CORRIDOR", "ARENA", "DENSE CITY", "DENSITY LADDER"]
const DENSITY_SCRIPT := "res://stress/density_ladder.gd"
const CAPTURE_ROOT := "user://visual_truth"
const PIXEL_TOLERANCE := 2
const OBS_DIR := "user://frame_observations"
const OBS_WARMUP := 2.0
const OBS_DURATION := 8.0
const OBS_MIN_FRAMES := 60
const OBS_MAX_FRAMES := 1500
const OBS_MODES := ["geometry", "lights", "vfx", "combined"]
const GPU_PROFILE_SESSION_SCRIPT := "res://gpu_profile/session.gd"
const GPU_PROFILE_SOURCE_SHA_ENV := "NEX_GPU_PROFILE_SOURCE_SHA"

@onready var world_root: Node3D = $WorldRoot
@onready var title_label: Label = $HUD/Title
@onready var status_label: Label = $HUD/Status

var active_mode := 0
var active_world: Node3D
var capture_pending := false
var diagnostics_panel: PanelContainer
var diagnostics_label: Label
var diagnostics_elapsed := 0.0
var camera_home_position := Vector3.ZERO
var camera_home_rotation := Vector3.ZERO
var observation_active := false
var observation_elapsed := 0.0
var observation_frames: Array[float] = []
var observation_proxies := 0
var observation_mode := 0
var gpu_profile_session: RefCounted
var gpu_profile_button: Button
var gpu_profile_panel: PanelContainer
var gpu_profile_label: Label
var gpu_profile_workload: Dictionary = {}
var gpu_profile_last_status := "GPU PROFILER IDLE | F11 start in F4; measurement is disabled."

func _ready() -> void:
    DisplayServer.window_set_title("NEX Engine | Visual Lab")
    var profile_script := load(GPU_PROFILE_SESSION_SCRIPT) as Script
    if profile_script != null:
        gpu_profile_session = profile_script.new() as RefCounted
    _make_toolbar()
    _make_diagnostics_panel()
    _make_gpu_profile_panel()
    _activate_mode(0)

func _make_toolbar() -> void:
    var toolbar := HBoxContainer.new()
    toolbar.name = "Toolbar"
    toolbar.position = Vector2(20, 48)
    toolbar.add_theme_constant_override("separation", 8)
    $HUD.add_child(toolbar)
    for i in range(SCENE_LABELS.size()):
        var button := Button.new()
        button.name = "Mode_%d" % i
        button.text = "%s  [F%d]" % [SCENE_LABELS[i], i + 1]
        button.custom_minimum_size = Vector2(148, 40)
        button.pressed.connect(_activate_mode.bind(i))
        toolbar.add_child(button)
    for action in ["BASELINE [B]", "CANDIDATE [N]", "COMPARE [D]"]:
        var button := Button.new()
        button.text = action
        button.custom_minimum_size = Vector2(132, 40)
        toolbar.add_child(button)
        if action.begins_with("BASELINE"):
            button.pressed.connect(_capture.bind("baseline"))
        elif action.begins_with("CANDIDATE"):
            button.pressed.connect(_capture.bind("candidate"))
        else:
            button.pressed.connect(_compare_captures)
    var diagnostics_button := Button.new()
    diagnostics_button.text = "DIAGNOSTICO [F9]"
    diagnostics_button.custom_minimum_size = Vector2(132, 40)
    diagnostics_button.pressed.connect(_toggle_diagnostics)
    toolbar.add_child(diagnostics_button)
    gpu_profile_button = Button.new()
    gpu_profile_button.name = "GPUProfileButton"
    gpu_profile_button.text = "GPU PROFILE [F11]"
    gpu_profile_button.custom_minimum_size = Vector2(150, 40)
    gpu_profile_button.pressed.connect(_toggle_gpu_profile)
    toolbar.add_child(gpu_profile_button)

func _make_gpu_profile_panel() -> void:
    gpu_profile_panel = PanelContainer.new()
    gpu_profile_panel.name = "GPUProfileStatus"
    gpu_profile_panel.anchor_left = 1.0
    gpu_profile_panel.anchor_top = 1.0
    gpu_profile_panel.anchor_right = 1.0
    gpu_profile_panel.anchor_bottom = 1.0
    gpu_profile_panel.offset_left = -474.0
    gpu_profile_panel.offset_top = -116.0
    gpu_profile_panel.offset_right = -16.0
    gpu_profile_panel.offset_bottom = -18.0
    gpu_profile_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    gpu_profile_label = Label.new()
    gpu_profile_label.name = "GPUProfileStats"
    gpu_profile_label.custom_minimum_size = Vector2(438.0, 78.0)
    gpu_profile_label.add_theme_font_size_override("font_size", 14)
    gpu_profile_label.text = gpu_profile_last_status
    gpu_profile_panel.add_child(gpu_profile_label)
    $HUD.add_child(gpu_profile_panel)

func _exit_tree() -> void:
    if gpu_profile_session != null and gpu_profile_session.is_active():
        gpu_profile_session.cancel("visual lab closed")

func _make_diagnostics_panel() -> void:
    diagnostics_panel = PanelContainer.new()
    diagnostics_panel.name = "RenderDiagnostics"
    diagnostics_panel.anchor_top = 1.0
    diagnostics_panel.anchor_bottom = 1.0
    diagnostics_panel.offset_left = 16.0
    diagnostics_panel.offset_top = -247.0
    diagnostics_panel.offset_right = 440.0
    diagnostics_panel.offset_bottom = -18.0
    diagnostics_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    diagnostics_label = Label.new()
    diagnostics_label.name = "RenderStats"
    diagnostics_label.custom_minimum_size = Vector2(410.0, 218.0)
    diagnostics_label.add_theme_font_size_override("font_size", 15)
    diagnostics_panel.add_child(diagnostics_label)
    $HUD.add_child(diagnostics_panel)
    diagnostics_panel.visible = false

func _toggle_diagnostics() -> void:
    if diagnostics_panel == null:
        return
    diagnostics_panel.visible = not diagnostics_panel.visible
    if diagnostics_panel.visible:
        _refresh_diagnostics()

func _process(delta: float) -> void:
    _sample_frame_observation(delta)
    _sample_gpu_profile(delta)
    if diagnostics_panel == null or not diagnostics_panel.visible:
        return
    diagnostics_elapsed += delta
    if diagnostics_elapsed >= 0.75:
        diagnostics_elapsed = 0.0
        _refresh_diagnostics()

func _refresh_diagnostics() -> void:
    if diagnostics_label == null:
        return
    var driver: String = RenderingServer.get_current_rendering_driver_name()
    var method_name: String = RenderingServer.get_current_rendering_method()
    var adapter: String = RenderingServer.get_video_adapter_name()
    var backend: String = DisplayServer.get_name()
    if adapter.is_empty():
        adapter = "N/A (headless / unavailable)"
    var is_headless: bool = backend == "headless"
    var fps: float = Performance.get_monitor(Performance.TIME_FPS)
    var process_ms: float = Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0
    var calls: int = int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
    var objects: int = int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME))
    var memory: float = Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)
    var memory_text: String = "N/A (headless / unavailable)" if is_headless or memory <= 0.0 else "%.1f MiB (renderer allocation)" % (memory / (1024.0 * 1024.0))
    diagnostics_label.text = (
        "NEX ENGINE  |  DIAGNOSTICO LOCAL [F9]\n"
        + "Cena: %s\n" % SCENE_LABELS[active_mode]
        + "Render method: %s / driver: %s\n" % [method_name, driver]
        + "Display: %s\n" % backend
        + "Adapter: %s\n" % adapter
        + "FPS observado: %.0f (nao e benchmark)\n" % fps
        + "CPU process: %.2f ms/frame (nao GPU time)\n" % process_ms
        + "Draw calls: %d | objetos 3D: %d\n" % [calls, objects]
        + "Memoria do renderizador: %s\n" % memory_text
        + "NAO representa VRAM total, p95 ou latencia GPU"
    )

func _unhandled_key_input(event: InputEvent) -> void:
    if not (event is InputEventKey):
        return
    var key_event := event as InputEventKey
    if not key_event.pressed or key_event.echo:
        return
    match key_event.keycode:
        KEY_F1:
            _activate_mode(0)
        KEY_F2:
            _activate_mode(1)
        KEY_F3:
            _activate_mode(2)
        KEY_F4:
            _activate_mode(3)
        KEY_F9:
            _toggle_diagnostics()
        KEY_F10:
            if observation_active:
                _cancel_frame_observation("Observation cancelled")
            else:
                _begin_frame_observation()
        KEY_F11:
            _toggle_gpu_profile()
        KEY_F12:
            _capture_gpu_profile_screenshot()
        KEY_LEFT:
            _move_reference_camera(-15.0, 0.0, 1.0)
        KEY_RIGHT:
            _move_reference_camera(15.0, 0.0, 1.0)
        KEY_UP:
            _move_reference_camera(0.0, 10.0, 1.0)
        KEY_DOWN:
            _move_reference_camera(0.0, -10.0, 1.0)
        KEY_PAGEUP:
            _move_reference_camera(0.0, 0.0, 0.85)
        KEY_PAGEDOWN:
            _move_reference_camera(0.0, 0.0, 1.15)
        KEY_HOME:
            _reset_reference_camera()
        KEY_B:
            _capture("baseline")
        KEY_N:
            _capture("candidate")
        KEY_D:
            _compare_captures()
        _:
            return
    get_viewport().set_input_as_handled()

func _activate_mode(index: int) -> void:
    if index < 0 or index >= SCENE_LABELS.size():
        return
    var next_world: Node3D
    if index < SCENE_PATHS.size():
        var packed := load(SCENE_PATHS[index]) as PackedScene
        if packed == null:
            _status("BLOCKED: missing reference scene")
            return
        next_world = packed.instantiate() as Node3D
    else:
        next_world = _make_density_root()
    if next_world == null:
        _status("BLOCKED: unable to create native module")
        return
    if gpu_profile_session != null and gpu_profile_session.is_active():
        _cancel_gpu_profile("scene switched")
    if observation_active:
        _cancel_frame_observation("Observation cancelled: scene switched")
    _hide_diff_preview()
    for child in world_root.get_children():
        world_root.remove_child(child)
        child.queue_free()
    world_root.add_child(next_world)
    active_world = next_world
    active_mode = index
    var reference_cam: Camera3D = _reference_camera()
    if reference_cam != null:
        camera_home_position = reference_cam.position
        camera_home_rotation = reference_cam.rotation_degrees
    if diagnostics_panel != null and diagnostics_panel.visible:
        _refresh_diagnostics()
    title_label.text = "NEX ENGINE  /  " + SCENE_LABELS[index]
    if index == 3:
        _status("Density: 1/2/3/4 load, G/L/V/C effects, F10=record 2s warmup + 8s intervals (not GPU)")
    else:
        _status("3D camera: arrows orbit/tilt, PgUp/PgDn zoom, Home reset | B baseline, N candidate, D compare")

# Bounded samples of scene-tree _process(delta), not GPU frame timing.
func _begin_frame_observation() -> bool:
    if observation_active or (gpu_profile_session != null and gpu_profile_session.is_active()) or active_mode != 3 or active_world == null:
        _status("F10 observation available in F4 Density Ladder only")
        return false
    var raw_counts: Variant = active_world.get("counts")
    if not (raw_counts is Array):
        return false
    var levels: Array = raw_counts
    var idx: int = int(active_world.get("count_index"))
    var mode: int = int(active_world.get("current_mode"))
    if idx < 0 or idx >= levels.size() or mode < 0 or mode >= OBS_MODES.size():
        return false
    observation_proxies = int(levels[idx])
    observation_mode = mode
    if observation_proxies < 25 or observation_proxies > 200:
        return false
    observation_elapsed = 0.0
    observation_frames.clear()
    observation_active = true
    _status("Recording %d proxies/%s: 2s warmup + 8s observed frames; do not change load" % [
        observation_proxies, OBS_MODES[mode]
    ])
    return true

func _cancel_frame_observation(reason: String) -> void:
    observation_active = false
    observation_frames.clear()
    observation_elapsed = 0.0
    _status(reason)

func _toggle_gpu_profile() -> void:
    if gpu_profile_session == null:
        _status("GPU profiler unavailable: session module failed to load")
        gpu_profile_last_status = "GPU PROFILER BLOCKED | session module failed to load."
        _refresh_gpu_profile_panel()
        return
    if gpu_profile_session.is_active():
        _cancel_gpu_profile("manual cancellation")
    else:
        _begin_gpu_profile()

func _begin_gpu_profile() -> bool:
    if gpu_profile_session == null or observation_active:
        _status("GPU profile unavailable while F10 is recording")
        return false
    if active_mode != 3 or active_world == null:
        _status("GPU profile is available in F4 Density Ladder only")
        gpu_profile_last_status = "GPU PROFILER IDLE | select F4 Density Ladder, then press F11."
        _refresh_gpu_profile_panel()
        return false
    var raw_counts: Variant = active_world.get("counts")
    if not (raw_counts is Array):
        _status("GPU profile blocked: Density Ladder workload unavailable")
        return false
    var levels: Array = raw_counts
    var index := int(active_world.get("count_index"))
    var mode := int(active_world.get("current_mode"))
    if index < 0 or index >= levels.size() or mode < 0 or mode >= OBS_MODES.size():
        _status("GPU profile blocked: invalid Density Ladder selection")
        return false
    var source_sha := OS.get_environment(GPU_PROFILE_SOURCE_SHA_ENV).strip_edges().to_lower()
    gpu_profile_workload = {
        "source_sha": source_sha,
        "proxy_count": int(levels[index]),
        "effect_mode": OBS_MODES[mode]
    }
    var context := {
        "source_sha": source_sha,
        "scene": "Density Ladder",
        "proxy_count": int(levels[index]),
        "effect_mode": OBS_MODES[mode],
        "renderer": RenderingServer.get_current_rendering_method(),
        "driver": RenderingServer.get_current_rendering_driver_name(),
        "adapter": RenderingServer.get_video_adapter_name()
    }
    if not gpu_profile_session.begin(get_viewport(), context, true):
        _status("GPU profile blocked: " + str(gpu_profile_session.last_error))
        gpu_profile_last_status = "GPU PROFILER BLOCKED | " + str(gpu_profile_session.last_error)
        _refresh_gpu_profile_panel()
        return false
    if gpu_profile_button != null:
        gpu_profile_button.text = "CANCEL PROFILE [F11]"
    gpu_profile_last_status = "GPU PROFILER WARMUP | 2 s, then 30 s capture; workload locked."
    _refresh_gpu_profile_panel()
    _status("GPU profile started: 2s warmup + 30s observation; F11 cancels")
    return true

func _sample_gpu_profile(delta: float) -> void:
    if gpu_profile_session == null or not gpu_profile_session.is_active():
        return
    if not _gpu_profile_workload_matches():
        _cancel_gpu_profile("workload changed; run not exported")
        return
    var update: Dictionary = gpu_profile_session.step(delta, get_viewport())
    _refresh_gpu_profile_panel()
    if bool(update.get("finished", false)):
        _finish_gpu_profile(update)

func _gpu_profile_workload_matches() -> bool:
    if active_mode != 3 or active_world == null:
        return false
    var raw_counts: Variant = active_world.get("counts")
    if not (raw_counts is Array):
        return false
    var levels: Array = raw_counts
    var index := int(active_world.get("count_index"))
    var mode := int(active_world.get("current_mode"))
    return (
        index >= 0 and index < levels.size()
        and mode >= 0 and mode < OBS_MODES.size()
        and int(levels[index]) == int(gpu_profile_workload.get("proxy_count", -1))
        and OBS_MODES[mode] == str(gpu_profile_workload.get("effect_mode", ""))
    )

func _cancel_gpu_profile(reason: String) -> void:
    if gpu_profile_session == null or not gpu_profile_session.is_active():
        return
    gpu_profile_session.cancel(reason)
    if gpu_profile_button != null:
        gpu_profile_button.text = "GPU PROFILE [F11]"
    gpu_profile_last_status = "GPU PROFILER CANCELLED | %s; no partial report exported." % reason
    _refresh_gpu_profile_panel()
    _status("GPU profile cancelled: " + reason)

func _finish_gpu_profile(update: Dictionary) -> void:
    if gpu_profile_button != null:
        gpu_profile_button.text = "GPU PROFILE [F11]"
    var document: Dictionary = update.get("document", {})
    var output_path := str(gpu_profile_session.save_document(document))
    if output_path.is_empty():
        gpu_profile_last_status = "GPU PROFILER %s | capture was not saved; see local output limits." % str(update.get("state", "INVALID"))
        _status("GPU profile collected but JSON export failed")
    else:
        var series: Dictionary = document.get("series", {})
        var gpu: Dictionary = series.get("GPU_RENDER_MS", {})
        var cpu: Dictionary = series.get("CPU_RENDER_MS", {})
        gpu_profile_last_status = "GPU PROFILER %s | GPU=%s n=%d, CPU=%s n=%d\n%s" % [
            str(document.get("run_status", "INVALID")),
            str(gpu.get("status", "UNAVAILABLE")), int(gpu.get("valid_sample_count", 0)),
            str(cpu.get("status", "UNAVAILABLE")), int(cpu.get("valid_sample_count", 0)), output_path
        ]
        _status("GPU profile %s: %s" % [str(document.get("run_status", "INVALID")), output_path])
    _refresh_gpu_profile_panel()

func _refresh_gpu_profile_panel() -> void:
    if gpu_profile_panel == null or gpu_profile_label == null:
        return
    gpu_profile_label.text = gpu_profile_last_status
    if gpu_profile_session != null and gpu_profile_session.is_active():
        var progress: Dictionary = gpu_profile_session.progress()
        var elapsed := float(progress.get("elapsed_seconds", 0.0))
        var observed := float(progress.get("observed_seconds", 0.0))
        var phase := str(progress.get("state", "WARMUP"))
        var invalid: Dictionary = progress.get("invalid_samples", {})
        gpu_profile_label.text = "GPU PROFILER %s | %s\nWarmup %.1f/2s | captura %.1f/30s\nGPU %d (+%d inválidas) | CPU %d | loop %d" % [
            phase, str(gpu_profile_workload.get("effect_mode", "")),
            minf(elapsed, 2.0), observed,
            int(progress.get("gpu_samples", 0)), int(invalid.get("GPU_RENDER_MS", 0)),
            int(progress.get("cpu_samples", 0)), int(progress.get("main_loop_samples", 0))
        ]

func _capture_gpu_profile_screenshot() -> void:
    if active_mode != 3 or capture_pending:
        _status("Profiler screenshot is available in F4 only")
        return
    if gpu_profile_session != null and gpu_profile_session.is_active():
        _status("Wait for the GPU capture to finish before saving a HUD screenshot")
        return
    capture_pending = true
    await RenderingServer.frame_post_draw
    var image := get_viewport().get_texture().get_image()
    capture_pending = false
    if image == null or image.is_empty():
        _status("BLOCKED: GPU profiler screenshot unavailable")
        return
    var directory := ProjectSettings.globalize_path("user://gpu_profiles")
    if DirAccess.make_dir_recursive_absolute(directory) != OK:
        _status("BLOCKED: profiler screenshot folder unavailable")
        return
    var filename := "gpu_profile_ui_%d_%d.png" % [int(Time.get_unix_time_from_system()), Time.get_ticks_usec()]
    var output_path := directory.path_join(filename)
    var error := image.save_png(output_path)
    if error != OK:
        _status("BLOCKED: profiler screenshot could not be written")
        return
    _status("GPU profiler HUD screenshot saved: %s" % output_path)

func _sample_frame_observation(delta: float) -> void:
    if not observation_active:
        return
    if active_mode != 3 or active_world == null:
        _cancel_frame_observation("Observation cancelled: scene switched")
        return
    var raw_counts: Variant = active_world.get("counts")
    if not (raw_counts is Array):
        _cancel_frame_observation("Observation cancelled: missing workload")
        return
    var levels: Array = raw_counts
    var idx: int = int(active_world.get("count_index"))
    if idx < 0 or idx >= levels.size() or int(levels[idx]) != observation_proxies or int(active_world.get("current_mode")) != observation_mode:
        _cancel_frame_observation("Observation cancelled: workload changed")
        return
    # Never omit slow or invalid frames while still counting elapsed time:
    # that would bias p95/p99 and mean FPS upward, hiding a real hitch.
    if not is_finite(delta) or delta <= 0.0 or delta >= 1.0:
        _cancel_frame_observation("F10 INVALID: unsafe frame interval, no JSON saved")
        return
    observation_elapsed += delta
    if observation_elapsed <= OBS_WARMUP:
        return
    if observation_frames.size() < OBS_MAX_FRAMES:
        observation_frames.append(delta * 1000.0)
    if observation_elapsed >= OBS_WARMUP + OBS_DURATION or observation_frames.size() >= OBS_MAX_FRAMES:
        _finish_frame_observation()

# Nearest-rank percentile, no invented or interpolated frames.
func _observed_percentile_ms(samples: Array[float], quantile: float) -> float:
    if samples.is_empty():
        return 0.0
    var sorted: Array[float] = samples.duplicate()
    sorted.sort()
    var rank: int = clampi(int(ceil(quantile * float(sorted.size()))) - 1, 0, sorted.size() - 1)
    return sorted[rank]

func _finish_frame_observation() -> void:
    observation_active = false
    var frames: int = observation_frames.size()
    if frames < OBS_MIN_FRAMES:
        _status("Observation invalid: only %d samples, no JSON saved" % frames)
        observation_frames.clear()
        return
    var total_ms := 0.0
    for frame_ms in observation_frames:
        total_ms += frame_ms
    var mean_ms: float = total_ms / float(frames)
    var view: Vector2 = get_viewport().get_visible_rect().size
    var data := {
        "schema_version": "nex_frame_observation.v1",
        "measurement": "OBSERVED_MAIN_LOOP_DELTA_NOT_GPU_TIME",
        "captured_at_utc": Time.get_datetime_string_from_system(true, true),
        "godot": str(Engine.get_version_info().get("string", "unknown")),
        "os": OS.get_name(),
        "display": DisplayServer.get_name(),
        "renderer": RenderingServer.get_current_rendering_method(),
        "driver": RenderingServer.get_current_rendering_driver_name(),
        "adapter": RenderingServer.get_video_adapter_name(),
        "viewport_px": [int(view.x), int(view.y)],
        "max_fps_setting": Engine.max_fps,
        "vsync_mode": DisplayServer.window_get_vsync_mode(),
        "proxy_count": observation_proxies,
        "effect_mode": OBS_MODES[observation_mode],
        "warmup_seconds": OBS_WARMUP,
        "requested_seconds": OBS_DURATION,
        "sample_count": frames,
        "frame_intervals_units": "ms",
        "frame_intervals_ms": observation_frames.duplicate(),
        "observed_seconds": total_ms / 1000.0,
        "mean_interval_ms": mean_ms,
        "p50_interval_ms": _observed_percentile_ms(observation_frames, 0.50),
        "p95_interval_ms": _observed_percentile_ms(observation_frames, 0.95),
        "p99_interval_ms": _observed_percentile_ms(observation_frames, 0.99),
        "observed_mean_fps": 1000.0 / mean_ms,
        "limitations": "May be VSync capped; main-loop deltas are NOT GPU time, total VRAM or maximum FPS."
    }
    var dir: String = ProjectSettings.globalize_path(OBS_DIR)
    if DirAccess.make_dir_recursive_absolute(dir) != OK:
        _status("Observation complete but output folder unavailable")
        observation_frames.clear()
        return
    var file_name: String = "density_%d_%s_%d.json" % [
        observation_proxies, OBS_MODES[observation_mode], int(Time.get_unix_time_from_system())
    ]
    var output: String = dir.path_join(file_name)
    var stream: FileAccess = FileAccess.open(output, FileAccess.WRITE)
    if stream == null:
        _status("Observation complete but JSON could not be written")
        observation_frames.clear()
        return
    stream.store_string(JSON.stringify(data, "  ") + "\n")
    stream.close()
    observation_frames.clear()
    _status("F10 saved %d intervals, p95 %.2f ms (NOT GPU): %s" % [
        frames, float(data["p95_interval_ms"]), output
    ])

func _reference_camera() -> Camera3D:
    if active_world == null or active_mode >= SCENE_PATHS.size():
        return null
    return active_world.get_node_or_null("IsometricCamera") as Camera3D

# Camera moves change only the active reference viewport; never change source scenes,
# saved baselines, or the dynamic density mode. Distances and elevations are bounded.
func _move_reference_camera(yaw_degrees: float, elevation_degrees: float, zoom: float) -> bool:
    var camera: Camera3D = _reference_camera()
    if camera == null:
        return false
    var position: Vector3 = camera.position
    var radius: float = position.length()
    var original_radius: float = camera_home_position.length()
    if radius < 0.1 or original_radius < 0.1 or zoom <= 0.0:
        return false
    var azimuth: float = atan2(position.x, position.z) + deg_to_rad(yaw_degrees)
    var elevation: float = clampf(
        asin(clampf(position.y / radius, -1.0, 1.0)) + deg_to_rad(elevation_degrees),
        deg_to_rad(12.0), deg_to_rad(76.0)
    )
    var distance: float = clampf(radius * zoom, original_radius * 0.40, original_radius * 2.00)
    camera.position = Vector3(
        sin(azimuth) * cos(elevation),
        sin(elevation),
        cos(azimuth) * cos(elevation)
    ) * distance
    camera.look_at(Vector3.ZERO, Vector3.UP)
    _status("Camera adjusted | B baseline, N candidate, D diff | HOME reset")
    return true

func _reset_reference_camera() -> bool:
    var camera: Camera3D = _reference_camera()
    if camera == null:
        return false
    camera.position = camera_home_position
    camera.rotation_degrees = camera_home_rotation
    _status("Camera reset | B baseline, N candidate, D diff")
    return true

func _make_density_root() -> Node3D:
    var script := load(DENSITY_SCRIPT) as Script
    if script == null:
        return null
    var root := Node3D.new()
    root.name = "DensityLadder"
    root.set_script(script)
    var workload := Node3D.new()
    workload.name = "WorkloadRoot"
    root.add_child(workload)
    var hud := CanvasLayer.new()
    hud.name = "HUD"
    root.add_child(hud)
    var label := Label.new()
    label.name = "Status"
    label.position = Vector2(20, 166)
    label.add_theme_font_size_override("font_size", 16)
    hud.add_child(label)
    return root

func _capture(kind: String) -> void:
    if active_mode == 3:
        _status("Choose a static scene for repeatable screenshots, not live Density Ladder effects")
        return
    if capture_pending:
        return
    capture_pending = true
    $HUD.visible = false
    await RenderingServer.frame_post_draw
    var image := get_viewport().get_texture().get_image()
    $HUD.visible = true
    capture_pending = false
    if image == null or image.is_empty():
        _status("BLOCKED: screenshot unavailable")
        return
    var directory := ProjectSettings.globalize_path(CAPTURE_ROOT)
    var err := DirAccess.make_dir_recursive_absolute(directory)
    if err != OK:
        _status("BLOCKED: cannot create screenshot directory")
        return
    var filename := "%s_%s.png" % [SCENE_PATHS[active_mode].get_file().get_basename(), kind]
    err = image.save_png(directory.path_join(filename))
    if err != OK:
        _status("BLOCKED: screenshot save failed")
        return
    _status("%s SAVED: %s | run D for pixel comparison" % [kind.to_upper(), directory.path_join(filename)])

func _compare_captures() -> void:
    if active_mode == 3:
        _status("Pixel reference comparison is limited to static scenes")
        return
    var directory := ProjectSettings.globalize_path(CAPTURE_ROOT)
    var stem: String = SCENE_PATHS[active_mode].get_file().get_basename()
    var baseline := directory.path_join(stem + "_baseline.png")
    var candidate := directory.path_join(stem + "_candidate.png")
    if not FileAccess.file_exists(baseline) or not FileAccess.file_exists(candidate):
        _status("Capture both B baseline and N candidate first")
        return
    var first := Image.load_from_file(baseline)
    var second := Image.load_from_file(candidate)
    if first == null or second == null or first.is_empty() or second.is_empty():
        _status("BLOCKED: PNG could not be decoded")
        return
    var report: Dictionary = _pixel_diff(first, second)
    match str(report.get("status", "INVALID_IMAGE")):
        "SIZE_MISMATCH":
            _status("FAIL: screenshot resolution mismatch")
        "INVALID_IMAGE", "BUFFER_MISMATCH":
            _status("BLOCKED: pixel buffers incompatible")
        _:
            var heatmap: Image = _create_heatmap(first, second)
            if heatmap == null:
                _status("BLOCKED: heatmap could not be created")
                return
            _show_diff_preview(heatmap, report)
            var output_path: String = directory.path_join(stem + "_heatmap.png")
            var write_error: Error = heatmap.save_png(output_path)
            var image_note: String = "heatmap saved" if write_error == OK else "heatmap preview only (save failed)"
            _status("VISUAL TRUTH | %.3f%% changed (> %d/255) | MAE %.6f | %s | %s" % [
                float(report["changed_ratio"]) * 100.0,
                int(report["pixel_tolerance"]),
                float(report["mean_absolute_error_normalized"]),
                str(report["status"]),
                image_note
            ])

# Pure native Image comparator shared by the live UI and native runner tests.
# Keeps screenshots unchanged and does not touch user:// or invoke external programs.
func _pixel_diff(first: Image, second: Image) -> Dictionary:
    if first == null or second == null or first.is_empty() or second.is_empty():
        return {"status": "INVALID_IMAGE"}
    if first.get_size() != second.get_size():
        return {"status": "SIZE_MISMATCH"}
    var first_rgb := first.duplicate() as Image
    var second_rgb := second.duplicate() as Image
    first_rgb.convert(Image.FORMAT_RGB8)
    second_rgb.convert(Image.FORMAT_RGB8)
    var lhs: PackedByteArray = first_rgb.get_data()
    var rhs: PackedByteArray = second_rgb.get_data()
    if lhs.size() != rhs.size() or lhs.size() == 0 or lhs.size() % 3 != 0:
        return {"status": "BUFFER_MISMATCH"}
    var changed := 0
    var absolute_error := 0
    for i in range(0, lhs.size(), 3):
        var dr := absi(int(lhs[i]) - int(rhs[i]))
        var dg := absi(int(lhs[i + 1]) - int(rhs[i + 1]))
        var db := absi(int(lhs[i + 2]) - int(rhs[i + 2]))
        absolute_error += dr + dg + db
        if maxi(dr, maxi(dg, db)) > PIXEL_TOLERANCE:
            changed += 1
    var pixels := first_rgb.get_width() * first_rgb.get_height()
    return {
        "status": "PASS" if changed == 0 else "DIFF",
        "changed_pixels": changed,
        "changed_ratio": float(changed) / float(pixels),
        "mean_absolute_error_normalized": float(absolute_error) / float(pixels * 3 * 255),
        "pixel_tolerance": PIXEL_TOLERANCE
    }

# Deterministic red-difference heatmap. Never modifies the source images.
# This is an RGB pixel visualization, not GPU/perceptual validation.
func _create_heatmap(first: Image, second: Image) -> Image:
    if first == null or second == null or first.is_empty() or second.is_empty():
        return null
    if first.get_size() != second.get_size():
        return null
    var reference: Image = first.duplicate() as Image
    var candidate: Image = second.duplicate() as Image
    reference.convert(Image.FORMAT_RGB8)
    candidate.convert(Image.FORMAT_RGB8)
    var lhs: PackedByteArray = reference.get_data()
    var rhs: PackedByteArray = candidate.get_data()
    if lhs.size() != rhs.size() or lhs.size() == 0 or lhs.size() % 3 != 0:
        return null
    var pixels: int = reference.get_width() * reference.get_height()
    if lhs.size() != pixels * 3:
        return null
    var output := PackedByteArray()
    output.resize(pixels * 4)
    for pixel in range(pixels):
        var src: int = pixel * 3
        var dst: int = pixel * 4
        var dr: int = absi(int(lhs[src]) - int(rhs[src]))
        var dg: int = absi(int(lhs[src + 1]) - int(rhs[src + 1]))
        var db: int = absi(int(lhs[src + 2]) - int(rhs[src + 2]))
        if maxi(dr, maxi(dg, db)) > PIXEL_TOLERANCE:
            output[dst] = 255
            output[dst + 1] = 32
            output[dst + 2] = 48
        else:
            var grayscale: int = (int(lhs[src]) + int(lhs[src + 1]) + int(lhs[src + 2])) / 6
            output[dst] = grayscale
            output[dst + 1] = grayscale
            output[dst + 2] = grayscale
        output[dst + 3] = 255
    return Image.create_from_data(reference.get_width(), reference.get_height(), false, Image.FORMAT_RGBA8, output)

func _hide_diff_preview() -> void:
    var previous: Control = $HUD.get_node_or_null("DiffPreview") as Control
    if previous != null:
        $HUD.remove_child(previous)
        previous.queue_free()

func _show_diff_preview(heatmap: Image, report: Dictionary) -> void:
    _hide_diff_preview()
    var panel := PanelContainer.new()
    panel.name = "DiffPreview"
    panel.anchor_left = 1.0
    panel.anchor_top = 1.0
    panel.anchor_right = 1.0
    panel.anchor_bottom = 1.0
    panel.offset_left = -464.0
    panel.offset_top = -342.0
    panel.offset_right = -16.0
    panel.offset_bottom = -18.0
    panel.mouse_filter = Control.MOUSE_FILTER_STOP
    var content := VBoxContainer.new()
    panel.add_child(content)
    var title := Label.new()
    title.text = "VISUAL TRUTH  |  %d altered pixels" % int(report.get("changed_pixels", 0))
    content.add_child(title)
    var preview := TextureRect.new()
    preview.name = "HeatmapTexture"
    preview.custom_minimum_size = Vector2(420.0, 252.0)
    preview.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    preview.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
    preview.texture = ImageTexture.create_from_image(heatmap)
    content.add_child(preview)
    var close_button := Button.new()
    close_button.text = "FECHAR MAPA DE DIFERENCAS"
    close_button.pressed.connect(_hide_diff_preview)
    content.add_child(close_button)
    $HUD.add_child(panel)

func _status(message: String) -> void:
    status_label.text = message
