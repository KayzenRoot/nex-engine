extends Node3D
class_name TemporalGuardAnalyzer

# NEX-M02-S04 prototype: deterministic temporal-defect analyzer and decision gate.
# Analysis only: no rendering, TAA, upscale, shader, CompositorEffect or render thread.
# Metrics are computed from synthetic region luminance sequences. The postprocess
# toggle is a guarded mock state, disabled by default and reset on every analysis.

enum Verdict { INCONCLUSIVE, BASELINE_ACCEPTABLE, DEFECT_REPRODUCED }
enum Action { NO_GO, KEEP_NATIVE, EVALUATE_COMPOSITOR }

@export var ghosting_threshold := 0.15
@export var flicker_threshold := 0.20
@export var shimmer_threshold := 0.05
@export var flicker_min_delta := 0.03
@export var step_threshold := 0.30
@export var min_frames := 4
@export var max_regions := 256

var last_error := ""
var _compositor_available := false
var _postprocess_enabled := false
var _last_report: Dictionary = {}


func configure(config: Dictionary) -> bool:
	last_error = ""
	var next_ghosting := float(config.get("ghosting_threshold", ghosting_threshold))
	var next_flicker := float(config.get("flicker_threshold", flicker_threshold))
	var next_shimmer := float(config.get("shimmer_threshold", shimmer_threshold))
	var next_min_delta := float(config.get("flicker_min_delta", flicker_min_delta))
	var next_step := float(config.get("step_threshold", step_threshold))
	var next_min_frames := int(config.get("min_frames", min_frames))
	var next_max_regions := int(config.get("max_regions", max_regions))
	for value in [next_ghosting, next_flicker, next_shimmer]:
		if not is_finite(value) or value < 0.0 or value > 1.0:
			last_error = "metric thresholds must be within [0,1]"
			return false
	if not is_finite(next_min_delta) or next_min_delta < 0.0 or next_min_delta > 0.5:
		last_error = "flicker_min_delta outside [0,0.5]"
		return false
	if not is_finite(next_step) or next_step < 0.05 or next_step > 1.0:
		last_error = "step_threshold outside [0.05,1]"
		return false
	if next_min_frames < 4 or next_min_frames > 256:
		last_error = "min_frames outside [4,256]"
		return false
	if next_max_regions < 1 or next_max_regions > 1024:
		last_error = "max_regions outside [1,1024]"
		return false
	ghosting_threshold = next_ghosting
	flicker_threshold = next_flicker
	shimmer_threshold = next_shimmer
	flicker_min_delta = next_min_delta
	step_threshold = next_step
	min_frames = next_min_frames
	max_regions = next_max_regions
	return true


func set_compositor_available(value: bool) -> void:
	_compositor_available = value
	if not value:
		_postprocess_enabled = false


func analyze(frames: Array, options := {}) -> Dictionary:
	last_error = ""
	_postprocess_enabled = false
	var render_scale := float(options.get("render_scale", 1.0))
	if not is_finite(render_scale) or render_scale < 0.5 or render_scale > 1.0:
		return _inconclusive("render_scale must be within [0.5,1]")
	if not _validate(frames):
		return _inconclusive(last_error)

	var ids: Array = frames[0].keys()
	var values: Dictionary = {}
	var edges: Dictionary = {}
	for id in ids:
		var series: Array = []
		for frame in frames:
			series.append(float(frame[id]["luminance"]))
		values[id] = series
		edges[id] = bool(frames[0][id]["edge"])
	var frame_count := frames.size()
	var ghosting := _ghosting(values, frame_count)
	var flicker := _flicker(values, frame_count)
	var shimmer := _shimmer(values, edges, frame_count)
	var penalty := (1.0 - render_scale) * 0.5
	var defect := ghosting > ghosting_threshold or flicker > flicker_threshold or shimmer > shimmer_threshold
	var verdict := "DEFECT_REPRODUCED" if defect else "BASELINE_ACCEPTABLE"
	var action := "KEEP_NATIVE"
	if defect:
		action = "NO_GO" if bool(options.get("prefer_native", false)) else "EVALUATE_COMPOSITOR"
	_last_report = {
		"verdict": verdict,
		"action": action,
		"metrics": {
			"ghosting": ghosting,
			"flicker": flicker,
			"shimmer": shimmer,
			"render_scale": render_scale,
			"sharpness_penalty": penalty,
		},
		"thresholds": {
			"ghosting": ghosting_threshold,
			"flicker": flicker_threshold,
			"shimmer": shimmer_threshold,
		},
		"frames": frame_count,
		"regions": ids.size(),
		"postprocess_enabled": false,
		"compositor_available": _compositor_available,
		"limitations": _limitations(),
	}
	return _last_report.duplicate(true)


func set_postprocess_enabled(value: bool) -> bool:
	last_error = ""
	if not value:
		_postprocess_enabled = false
		if not _last_report.is_empty():
			_last_report["postprocess_enabled"] = false
		return true
	if not _compositor_available:
		last_error = "compositor is unavailable; fallback must remain native"
		return false
	if _last_report.is_empty() or _last_report.get("verdict") != "DEFECT_REPRODUCED" or _last_report.get("action") != "EVALUATE_COMPOSITOR":
		last_error = "postprocess requires a measured temporal defect with a positive gate"
		return false
	_postprocess_enabled = true
	_last_report["postprocess_enabled"] = true
	return true


func get_report() -> Dictionary:
	return _last_report.duplicate(true)


func reset() -> void:
	last_error = ""
	_postprocess_enabled = false
	_last_report = {}


func _validate(frames: Array) -> bool:
	if frames.size() < min_frames:
		last_error = "at least %d frames are required" % min_frames
		return false
	var ids: Array = []
	for frame_index in range(frames.size()):
		var frame = frames[frame_index]
		if not (frame is Dictionary) or frame.is_empty():
			last_error = "frame %d must be a non-empty dictionary" % frame_index
			return false
		if ids.is_empty():
			ids = frame.keys()
			if ids.size() > max_regions:
				last_error = "region count exceeds max_regions"
				return false
		elif frame.size() != ids.size():
			last_error = "frame %d has a different region set" % frame_index
			return false
		for id in ids:
			if not frame.has(id):
				last_error = "frame %d is missing region %s" % [frame_index, id]
				return false
			var region = frame[id]
			if not (region is Dictionary):
				last_error = "region %s must be a dictionary" % id
				return false
			for key in ["luminance", "motion", "alpha", "edge"]:
				if not region.has(key):
					last_error = "region %s is missing %s" % [id, key]
					return false
			if not _is_number(region["luminance"]) or float(region["luminance"]) < 0.0 or float(region["luminance"]) > 1.0:
				last_error = "region %s luminance outside [0,1]" % id
				return false
			if not _is_number(region["alpha"]) or float(region["alpha"]) < 0.0 or float(region["alpha"]) > 1.0:
				last_error = "region %s alpha outside [0,1]" % id
				return false
			var motion = region["motion"]
			if not (motion is Array) or motion.size() != 2 or not _is_number(motion[0]) or not _is_number(motion[1]):
				last_error = "region %s motion must be two finite numbers" % id
				return false
			if not (region["edge"] is bool):
				last_error = "region %s edge must be boolean" % id
				return false
	return true


func _ghosting(values: Dictionary, frame_count: int) -> float:
	var max_lag := 0.0
	var steps := 0
	for id in values.keys():
		var series: Array = values[id]
		for index in range(1, frame_count):
			var old_value := float(series[index - 1])
			var target := float(series[index])
			var span := absf(target - old_value)
			if span < step_threshold:
				continue
			var ghosted := false
			var lag := 0
			for later in range(index + 1, frame_count):
				var value := float(series[later])
				if absf(value - old_value) < absf(value - target):
					ghosted = true
				if ghosted and absf(value - target) <= 0.1 * span:
					lag = later - index
					break
			if ghosted and lag == 0:
				lag = frame_count - index
			if ghosted:
				steps += 1
				max_lag = maxf(max_lag, float(lag))
	if steps == 0:
		return 0.0
	return max_lag / float(maxi(1, frame_count - 1))


func _flicker(values: Dictionary, frame_count: int) -> float:
	var worst := 0.0
	for id in values.keys():
		var series: Array = values[id]
		var deltas: Array = []
		for index in range(1, frame_count):
			deltas.append(float(series[index]) - float(series[index - 1]))
		var changes := 0
		var previous_sign := 0
		for delta in deltas:
			if absf(float(delta)) < flicker_min_delta:
				continue
			var sign_value := 1 if float(delta) > 0.0 else -1
			if previous_sign != 0 and sign_value != previous_sign:
				changes += 1
			previous_sign = sign_value
		worst = maxf(worst, float(changes) / float(maxi(1, frame_count - 2)))
	return worst


func _shimmer(values: Dictionary, edges: Dictionary, frame_count: int) -> float:
	var worst := 0.0
	for id in values.keys():
		if not bool(edges[id]):
			continue
		var series: Array = values[id]
		var deltas: Array = []
		for index in range(1, frame_count):
			deltas.append(absf(float(series[index]) - float(series[index - 1])))
		if deltas.size() <= 1:
			continue
		var largest := 0.0
		for delta in deltas:
			largest = maxf(largest, float(delta))
		var total := 0.0
		var removed := false
		for delta in deltas:
			if not removed and is_equal_approx(float(delta), largest):
				removed = true
				continue
			total += float(delta)
		worst = maxf(worst, total / float(deltas.size() - 1))
	return worst


func _inconclusive(reason: String) -> Dictionary:
	last_error = reason
	_last_report = {
		"verdict": "INCONCLUSIVE",
		"action": "NO_GO",
		"error": reason,
		"metrics": {},
		"thresholds": {
			"ghosting": ghosting_threshold,
			"flicker": flicker_threshold,
			"shimmer": shimmer_threshold,
		},
		"frames": 0,
		"regions": 0,
		"postprocess_enabled": false,
		"compositor_available": _compositor_available,
		"limitations": _limitations(),
	}
	return _last_report.duplicate(true)


func _limitations() -> Array:
	return [
		"analysis only; no rendering, TAA, upscale or antialiasing is executed",
		"real-scene ghosting/flicker/shimmer is INCONCLUSIVE_NOT_RUN",
		"metrics use synthetic region luminance, not pixel buffers",
		"CompositorEffect/render-thread is out of scope and requires a separate WO with ABI review",
		"postprocess is disabled by default; the enable toggle is a guarded mock state",
	]


func _is_number(value) -> bool:
	return (value is int or value is float) and not (value is bool) and is_finite(float(value))
