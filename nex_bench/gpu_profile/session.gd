extends RefCounted

# This recorder is opt-in. It enables Godot's per-viewport timing only while a
# bounded capture is active and never owns/frees the Viewport RID.
const WARMUP_SECONDS := 2.0
const OBSERVATION_SECONDS := 30.0
const MIN_VALID_SAMPLES := 300
const MAX_SAMPLES_PER_SERIES := 16000
const MAX_EXPORT_BYTES := 8_000_000
const OUTPUT_DIR := "user://gpu_profiles"
const SCHEMA_VERSION := "nex_gpu_render_profile.v2"
const FORMULA_VERSION := "nex-percentile-and-one-percent-low-monotonic-v2"
const FRAME_PACING_PROVIDER := "Time.get_ticks_usec sampled on each active Visual Lab _process(delta) callback"
const FRAME_PACING_FORMULA := "1000 / mean(slowest ceil(0.01*n) positive FRAME_PACING_INTERVAL_MS samples)"
const MONOTONIC_TICK_UNAVAILABLE := -1
const SERIES_SPECS := {
	"GPU_RENDER_MS": {
		"unit": "ms",
		"provider": "RenderingServer.viewport_get_measured_render_time_gpu"
	},
	"CPU_RENDER_MS": {
		"unit": "ms",
		"provider": "RenderingServer.viewport_get_measured_render_time_cpu"
	},
	"MAIN_LOOP_INTERVAL_MS": {
		"unit": "ms",
		"provider": "SceneTree._process(delta)"
	},
	"FRAME_PACING_INTERVAL_MS": {
		"unit": "ms",
		"provider": FRAME_PACING_PROVIDER
	},
	"RENDERER_ALLOCATION_BYTES": {
		"unit": "bytes",
		"provider": "Performance.RENDER_VIDEO_MEM_USED"
	}
}

var active := false
var measurement_enabled := false
var last_error := ""
var last_state := "IDLE"
var elapsed_seconds := 0.0
var observed_seconds := 0.0
var warmup_frames_discarded := 0
var invalid_samples := {
	"GPU_RENDER_MS": 0,
	"CPU_RENDER_MS": 0,
	"MAIN_LOOP_INTERVAL_MS": 0,
	"FRAME_PACING_INTERVAL_MS": 0,
	"RENDERER_ALLOCATION_BYTES": 0
}
var gpu_samples: Array[float] = []
var cpu_samples: Array[float] = []
var main_loop_samples: Array[float] = []
var frame_pacing_samples: Array[float] = []
var allocation_samples: Array[float] = []
var last_callback_tick_usec := 0
# Freeze dimensions for the entire capture, not only when exporting metadata.
var capture_viewport_size := Vector2i.ZERO
var frame_pacing_clock_invalid := false
var device_snapshots: Array[Dictionary] = []
var viewport_rid := RID()
var profile_viewport: Viewport
var run_context: Dictionary = {}
var capture_device_telemetry := true


func begin(viewport: Viewport, context: Dictionary, include_device_snapshot := true) -> bool:
	if active:
		last_error = "A GPU profile is already active."
		return false
	if not is_instance_valid(viewport):
		last_error = "The active viewport is unavailable."
		return false
	var source_sha := str(context.get("source_sha", "")).to_lower()
	if not _is_sha1(source_sha):
		last_error = "Set NEX_GPU_PROFILE_SOURCE_SHA to the measured code commit before starting."
		return false
	var proxy_count := int(context.get("proxy_count", 0))
	var effect_mode := str(context.get("effect_mode", ""))
	if proxy_count not in [25, 50, 100, 200] or effect_mode not in ["geometry", "lights", "vfx", "combined"]:
		last_error = "The current Density Ladder workload is invalid."
		return false
	var rid := viewport.get_viewport_rid()
	if not rid.is_valid():
		last_error = "The active viewport RID is invalid."
		return false

	_reset_capture()
	capture_viewport_size = Vector2i(viewport.get_visible_rect().size)
	last_callback_tick_usec = Time.get_ticks_usec()
	if last_callback_tick_usec <= 0:
		last_error = "The monotonic clock is unavailable."
		return false
	viewport_rid = rid
	profile_viewport = viewport
	run_context = context.duplicate(true)
	capture_device_telemetry = include_device_snapshot
	if capture_device_telemetry:
		device_snapshots.append(_capture_device_snapshot())
	RenderingServer.viewport_set_measure_render_time(viewport_rid, true)
	measurement_enabled = true
	active = true
	last_error = ""
	last_state = "WARMUP"
	return true


func step(delta: float, viewport: Viewport, monotonic_tick_usec: Variant = MONOTONIC_TICK_UNAVAILABLE) -> Dictionary:
	if not active:
		return {"finished": false, "state": last_state}
	if not is_instance_valid(viewport) or viewport.get_viewport_rid() != viewport_rid:
		return _finish("INVALID", "viewport_changed_or_unavailable")
	if Vector2i(viewport.get_visible_rect().size) != capture_viewport_size:
		# Mixed-resolution measurements cannot form a comparable 30 s run.
		return _finish("INVALID", "viewport_changed_or_unavailable")
	var tick_value: Variant = monotonic_tick_usec
	if typeof(monotonic_tick_usec) == TYPE_INT and int(monotonic_tick_usec) == MONOTONIC_TICK_UNAVAILABLE:
		tick_value = Time.get_ticks_usec()
	var interval_usec := _monotonic_interval_usec(tick_value)
	if interval_usec <= 0:
		return _finish("INVALID", "invalid_monotonic_tick")
	if not is_finite(delta) or delta <= 0.0 or delta >= 1.0:
		invalid_samples["MAIN_LOOP_INTERVAL_MS"] = int(invalid_samples["MAIN_LOOP_INTERVAL_MS"]) + 1
		return _finish("INVALID", "unsafe_main_loop_interval")
	var interval_seconds := float(interval_usec) / 1_000_000.0
	var previous_elapsed := elapsed_seconds
	elapsed_seconds += interval_seconds
	if elapsed_seconds <= WARMUP_SECONDS:
		warmup_frames_discarded += 1
		last_state = "WARMUP"
		return {"finished": false, "state": last_state}
	if previous_elapsed < WARMUP_SECONDS:
		warmup_frames_discarded += 1
		last_state = "COLLECTING"
		return {"finished": false, "state": last_state}

	observed_seconds += interval_seconds
	last_state = "COLLECTING"
	_record("MAIN_LOOP_INTERVAL_MS", delta * 1000.0)
	_record("FRAME_PACING_INTERVAL_MS", float(interval_usec) / 1000.0)
	_record("GPU_RENDER_MS", RenderingServer.viewport_get_measured_render_time_gpu(viewport_rid))
	_record("CPU_RENDER_MS", RenderingServer.viewport_get_measured_render_time_cpu(viewport_rid))
	_record("RENDERER_ALLOCATION_BYTES", Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED))

	if observed_seconds >= OBSERVATION_SECONDS:
		if frame_pacing_samples.size() < MIN_VALID_SAMPLES:
			return _finish("INVALID", "insufficient_frame_pacing_samples")
		return _finish("COMPLETE", "requested_observation_window_elapsed")
	if _sample_cap_reached():
		return _finish("INVALID", "sample_cap_reached_before_requested_duration")
	return {"finished": false, "state": last_state}


func cancel(reason: String) -> bool:
	if not active:
		return false
	active = false
	_disable_measurement()
	_reset_capture()
	last_state = "CANCELLED: " + reason
	last_error = reason
	return true


func progress() -> Dictionary:
	return {
		"state": last_state,
		"elapsed_seconds": elapsed_seconds,
		"observed_seconds": observed_seconds,
		"gpu_samples": gpu_samples.size(),
		"cpu_samples": cpu_samples.size(),
		"main_loop_samples": main_loop_samples.size(),
		"frame_pacing_samples": frame_pacing_samples.size(),
		"allocation_samples": allocation_samples.size(),
		"invalid_samples": invalid_samples.duplicate(true)
	}


func is_active() -> bool:
	return active


func is_measurement_enabled() -> bool:
	return measurement_enabled


func save_document(document: Dictionary) -> String:
	var output_directory := ProjectSettings.globalize_path(OUTPUT_DIR)
	if DirAccess.make_dir_recursive_absolute(output_directory) != OK:
		return ""
	var run_id := str(document.get("run_id", ""))
	if run_id.is_empty():
		return ""
	var output_path := output_directory.path_join("gpu_profile_%s.json" % run_id)
	if FileAccess.file_exists(output_path):
		return ""
	var encoded := JSON.stringify(document, "\t") + "\n"
	if encoded.to_utf8_buffer().size() > MAX_EXPORT_BYTES:
		return ""
	var file := FileAccess.open(output_path, FileAccess.WRITE)
	if file == null:
		return ""
	file.store_string(encoded)
	file.flush()
	file.close()
	return output_path


func _record(name: String, raw_value: float) -> void:
	var value := float(raw_value)
	if not is_finite(value) or value <= 0.0:
		invalid_samples[name] = int(invalid_samples[name]) + 1
		return
	if name == "MAIN_LOOP_INTERVAL_MS" and value >= 1000.0:
		invalid_samples[name] = int(invalid_samples[name]) + 1
		return
	if name == "FRAME_PACING_INTERVAL_MS" and value >= 1000.0:
		invalid_samples[name] = int(invalid_samples[name]) + 1
		frame_pacing_clock_invalid = true
		return
	if name == "RENDERER_ALLOCATION_BYTES":
		value = float(int(value))
		if value <= 0.0:
			invalid_samples[name] = int(invalid_samples[name]) + 1
			return
	match name:
		"GPU_RENDER_MS":
			gpu_samples.append(value)
		"CPU_RENDER_MS":
			cpu_samples.append(value)
		"MAIN_LOOP_INTERVAL_MS":
			main_loop_samples.append(value)
		"FRAME_PACING_INTERVAL_MS":
			frame_pacing_samples.append(value)
		"RENDERER_ALLOCATION_BYTES":
			allocation_samples.append(value)


func _sample_cap_reached() -> bool:
	return (
		gpu_samples.size() >= MAX_SAMPLES_PER_SERIES
		or cpu_samples.size() >= MAX_SAMPLES_PER_SERIES
		or main_loop_samples.size() >= MAX_SAMPLES_PER_SERIES
		or frame_pacing_samples.size() >= MAX_SAMPLES_PER_SERIES
		or allocation_samples.size() >= MAX_SAMPLES_PER_SERIES
	)


func _finish(run_status: String, reason: String) -> Dictionary:
	if run_status == "COMPLETE" and frame_pacing_clock_invalid:
		run_status = "INVALID"
		reason = "invalid_monotonic_tick"
	elif run_status == "COMPLETE" and frame_pacing_samples.size() < MIN_VALID_SAMPLES:
		run_status = "INVALID"
		reason = "insufficient_frame_pacing_samples"
	active = false
	_disable_measurement()
	if capture_device_telemetry:
		device_snapshots.append(_capture_device_snapshot())
	last_state = run_status
	last_error = reason if run_status != "COMPLETE" else ""
	var document := _build_document(run_status, reason)
	return {"finished": true, "state": run_status, "reason": reason, "document": document}


func _build_document(run_status: String, reason: String) -> Dictionary:
	var view_size := Vector2i.ZERO
	if is_instance_valid(profile_viewport):
		view_size = profile_viewport.get_visible_rect().size
	var method_name := str(run_context.get("renderer", RenderingServer.get_current_rendering_method()))
	var driver_name := str(run_context.get("driver", RenderingServer.get_current_rendering_driver_name()))
	var adapter_name := str(run_context.get("adapter", RenderingServer.get_video_adapter_name()))
	var device_status := "UNAVAILABLE"
	var device_reason := "nvidia-smi snapshots were not requested or were unavailable."
	for snapshot in device_snapshots:
		if str(snapshot.get("status", "")) == "MEASURED":
			device_status = "MEASURED"
			device_reason = ""
			break
	var frame_pacing_record := _series_record("FRAME_PACING_INTERVAL_MS", frame_pacing_samples)
	var one_percent_low: Variant = null
	if frame_pacing_record["status"] == "MEASURED":
		one_percent_low = _one_percent_low_fps(frame_pacing_samples)
	var delta_derived_one_percent_low: Variant = null
	if main_loop_samples.size() >= MIN_VALID_SAMPLES:
		delta_derived_one_percent_low = _one_percent_low_fps(main_loop_samples)
	return {
		"schema_version": SCHEMA_VERSION,
		"run_id": "%d-%d" % [int(Time.get_unix_time_from_system()), Time.get_ticks_usec()],
		"run_status": run_status,
		"run_reason": reason,
		"captured_at_utc": _utc_timestamp(),
		"source_sha": str(run_context.get("source_sha", "")).to_lower(),
		"godot_version": str(Engine.get_version_info().get("string", "unknown")),
		"os": OS.get_name(),
		"display": DisplayServer.get_name(),
		"renderer": method_name,
		"driver": driver_name,
		"adapter": adapter_name,
		"viewport": {
			"rid": str(viewport_rid),
			"resolution_px": [view_size.x, view_size.y]
		},
		"workload": {
			"scene": str(run_context.get("scene", "Density Ladder")),
			"proxy_count": int(run_context.get("proxy_count", 0)),
			"effect_mode": str(run_context.get("effect_mode", "")),
			"layout": "built-in deterministic grid"
		},
		"settings": {
			"vsync_mode": DisplayServer.window_get_vsync_mode(),
			"max_fps": Engine.max_fps
		},
		"measurement": {
			"provider": "Godot RenderingServer per-viewport render timing",
			"warmup_seconds": WARMUP_SECONDS,
			"requested_seconds": OBSERVATION_SECONDS,
			"observed_seconds": observed_seconds,
			"warmup_frames_discarded": warmup_frames_discarded,
			"invalid_main_loop_samples": int(invalid_samples["MAIN_LOOP_INTERVAL_MS"]),
			"percentile_method": "nearest_rank",
			"formula_version": FORMULA_VERSION,
			"one_percent_low_fps_formula": FRAME_PACING_FORMULA,
			"one_percent_low_fps": one_percent_low,
			"one_percent_low_fps_source": "FRAME_PACING_INTERVAL_MS",
			"frame_pacing_provider": FRAME_PACING_PROVIDER,
			"frame_pacing_status": frame_pacing_record["status"],
			"frame_pacing_unavailable_reason": frame_pacing_record["unavailable_reason"],
			"invalid_frame_pacing_samples": int(invalid_samples["FRAME_PACING_INTERVAL_MS"]),
			"delta_derived_one_percent_low_fps_label": "DELTA_DERIVED_VSYNC_LIMITED",
			"delta_derived_one_percent_low_fps": delta_derived_one_percent_low,
			"frame_pacing_limitation": "Monotonic Time.get_ticks_usec callback intervals are CPU callback pacing, not display presentation or input-to-photon latency.",
			"temporal_alignment_note": "Viewport render timing can describe earlier rendered work and is not guaranteed to align one-to-one with the current _process(delta)."
		},
		"series": {
			"GPU_RENDER_MS": _series_record("GPU_RENDER_MS", gpu_samples),
			"CPU_RENDER_MS": _series_record("CPU_RENDER_MS", cpu_samples),
			"MAIN_LOOP_INTERVAL_MS": _series_record("MAIN_LOOP_INTERVAL_MS", main_loop_samples),
			"FRAME_PACING_INTERVAL_MS": frame_pacing_record,
			"RENDERER_ALLOCATION_BYTES": _series_record("RENDERER_ALLOCATION_BYTES", allocation_samples)
		},
		"device_snapshot": {
			"status": device_status,
			"provider": "nvidia-smi --query-gpu (device-wide; never process-attributed under WDDM)",
			"scope": "DEVICE_WIDE_NOT_PROCESS_ATTRIBUTED",
			"samples": device_snapshots.duplicate(true),
			"unavailable_reason": device_reason if device_status == "UNAVAILABLE" else ""
		}
	}


func _series_record(name: String, samples: Array[float]) -> Dictionary:
	var spec: Dictionary = SERIES_SPECS[name]
	var retained := samples.duplicate()
	var valid_count := retained.size()
	var unavailable_reason := ""
	var status := "MEASURED"
	var aggregates: Variant = null
	if name == "FRAME_PACING_INTERVAL_MS" and frame_pacing_clock_invalid:
		status = "UNAVAILABLE"
		unavailable_reason = "invalid_monotonic_tick_sequence"
	elif valid_count < MIN_VALID_SAMPLES:
		status = "UNAVAILABLE"
		unavailable_reason = "fewer_than_%d_valid_samples" % MIN_VALID_SAMPLES
	else:
		aggregates = _aggregates(retained)
	return {
		"status": status,
		"unit": spec["unit"],
		"provider": spec["provider"],
		"samples": retained,
		"valid_sample_count": valid_count,
		"invalid_sample_count": int(invalid_samples[name]),
		"aggregates": aggregates,
		"unavailable_reason": unavailable_reason
	}


func _aggregates(samples: Array[float]) -> Dictionary:
	var sorted: Array[float] = samples.duplicate()
	sorted.sort()
	var total := 0.0
	for sample in sorted:
		total += sample
	return {
		"mean": total / float(sorted.size()),
		"p50": _percentile(sorted, 0.50),
		"p95": _percentile(sorted, 0.95),
		"p99": _percentile(sorted, 0.99)
	}


func _percentile(sorted_samples: Array[float], quantile: float) -> float:
	var rank := clampi(int(ceil(quantile * float(sorted_samples.size()))) - 1, 0, sorted_samples.size() - 1)
	return sorted_samples[rank]


func _one_percent_low_fps(samples: Array[float]) -> float:
	var ordered: Array[float] = samples.duplicate()
	ordered.sort()
	var slowest_count := maxi(1, int(ceil(0.01 * float(ordered.size()))))
	var slowest_total := 0.0
	for index in range(ordered.size() - slowest_count, ordered.size()):
		slowest_total += ordered[index]
	return 1000.0 / (slowest_total / float(slowest_count))


func _monotonic_interval_usec(tick_usec: Variant) -> int:
	if typeof(tick_usec) != TYPE_INT or int(tick_usec) <= 0 or last_callback_tick_usec <= 0:
		invalid_samples["FRAME_PACING_INTERVAL_MS"] = int(invalid_samples["FRAME_PACING_INTERVAL_MS"]) + 1
		frame_pacing_clock_invalid = true
		return -1
	var current_tick := int(tick_usec)
	if current_tick <= last_callback_tick_usec:
		invalid_samples["FRAME_PACING_INTERVAL_MS"] = int(invalid_samples["FRAME_PACING_INTERVAL_MS"]) + 1
		frame_pacing_clock_invalid = true
		return -1
	var interval_usec := current_tick - last_callback_tick_usec
	if interval_usec >= 1_000_000:
		invalid_samples["FRAME_PACING_INTERVAL_MS"] = int(invalid_samples["FRAME_PACING_INTERVAL_MS"]) + 1
		frame_pacing_clock_invalid = true
		return -1
	last_callback_tick_usec = current_tick
	return interval_usec


func _capture_device_snapshot() -> Dictionary:
	if OS.get_name() != "Windows":
		return _unavailable_device_snapshot("nvidia-smi device snapshots are Windows-local only.")
	var output: Array = []
	var exit_code := OS.execute("nvidia-smi", [
		"--query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu,clocks.current.graphics,temperature.gpu,power.draw",
		"--format=csv,noheader"
	], output, true)
	var lines := PackedStringArray()
	for line in output:
		lines.append(str(line))
	var raw_csv := "\n".join(lines).strip_edges()
	if exit_code != 0 or raw_csv.is_empty():
		return {
			"status": "UNAVAILABLE",
			"provider": "nvidia-smi",
			"scope": "DEVICE_WIDE_NOT_PROCESS_ATTRIBUTED",
			"captured_at_utc": _utc_timestamp(),
			"exit_code": exit_code,
			"raw_csv": "",
			"unavailable_reason": "nvidia-smi was not available or returned no device row."
		}
	return {
		"status": "MEASURED",
		"provider": "nvidia-smi",
		"scope": "DEVICE_WIDE_NOT_PROCESS_ATTRIBUTED",
		"captured_at_utc": _utc_timestamp(),
		"exit_code": exit_code,
		"raw_csv": raw_csv,
		"unavailable_reason": ""
	}


func _unavailable_device_snapshot(reason: String) -> Dictionary:
	return {
		"status": "UNAVAILABLE",
		"provider": "nvidia-smi",
		"scope": "DEVICE_WIDE_NOT_PROCESS_ATTRIBUTED",
		"captured_at_utc": _utc_timestamp(),
		"exit_code": -1,
		"raw_csv": "",
		"unavailable_reason": reason
	}


func _disable_measurement() -> void:
	if measurement_enabled and viewport_rid.is_valid():
		RenderingServer.viewport_set_measure_render_time(viewport_rid, false)
	measurement_enabled = false


func _reset_capture() -> void:
	elapsed_seconds = 0.0
	observed_seconds = 0.0
	warmup_frames_discarded = 0
	invalid_samples = {
		"GPU_RENDER_MS": 0,
		"CPU_RENDER_MS": 0,
		"MAIN_LOOP_INTERVAL_MS": 0,
		"FRAME_PACING_INTERVAL_MS": 0,
		"RENDERER_ALLOCATION_BYTES": 0
	}
	gpu_samples.clear()
	cpu_samples.clear()
	main_loop_samples.clear()
	frame_pacing_samples.clear()
	allocation_samples.clear()
	device_snapshots.clear()
	last_callback_tick_usec = 0
	capture_viewport_size = Vector2i.ZERO
	frame_pacing_clock_invalid = false


func _is_sha1(value: String) -> bool:
	if value.length() != 40:
		return false
	for character in value:
		if not "0123456789abcdef".contains(character):
			return false
	return true


func _utc_timestamp() -> String:
	return Time.get_datetime_string_from_system(true, false) + "Z"
