extends RefCounted
class_name FramePacer

# NEX M06-S06 FramePacer: render-scale policy with hysteresis and cooldown.
# The policy is research-bounded; it does not claim dynamic adaptation.

var min_scale := 0.6
var max_scale := 1.0
var target_ms := 16.67
var step := 0.05
var cooldown_frames := 30
var hysteresis_ms := 1.5
var scale := 1.0
var last_error := ""
var _last_change_frame := -1000000
var _last_action := "hold"


func configure(config := {}) -> bool:
	last_error = ""
	var next_min := float(config.get("min_scale", min_scale))
	var next_max := float(config.get("max_scale", max_scale))
	var next_target := float(config.get("target_ms", target_ms))
	var next_step := float(config.get("step", step))
	var next_cooldown := int(config.get("cooldown_frames", cooldown_frames))
	var next_hysteresis := float(config.get("hysteresis_ms", hysteresis_ms))
	if not is_finite(next_min) or not is_finite(next_max) or not is_finite(next_target):
		last_error = "scale and target must be finite"
		return false
	if next_min < 0.1 or next_max > 1.0 or next_min > next_max:
		last_error = "require 0.1 <= min <= max <= 1.0"
		return false
	if next_target <= 0.0 or next_step <= 0.0 or next_step > 0.5:
		last_error = "invalid target or step"
		return false
	if next_cooldown < 1 or next_hysteresis < 0.0:
		last_error = "invalid cooldown or hysteresis"
		return false
	min_scale = next_min
	max_scale = next_max
	target_ms = next_target
	step = next_step
	cooldown_frames = next_cooldown
	hysteresis_ms = next_hysteresis
	scale = clampf(scale, min_scale, max_scale)
	return true


func update(frame_ms: float, frame_index: int) -> Dictionary:
	if not is_finite(frame_ms) or frame_ms < 0.0:
		last_error = "frame_ms must be finite and non-negative"
		return {"ok": false, "reason": last_error}
	var elapsed := frame_index - _last_change_frame
	if elapsed < cooldown_frames:
		_last_action = "hold"
		return {"ok": true, "scale": scale, "action": "hold", "reason": "cooldown"}
	if frame_ms > target_ms + hysteresis_ms and scale > min_scale:
		scale = maxf(min_scale, scale - step)
		_last_change_frame = frame_index
		_last_action = "down"
		return {"ok": true, "scale": scale, "action": "down", "reason": "above_target"}
	if frame_ms < target_ms - hysteresis_ms and scale < max_scale:
		scale = minf(max_scale, scale + step)
		_last_change_frame = frame_index
		_last_action = "up"
		return {"ok": true, "scale": scale, "action": "up", "reason": "below_target"}
	_last_action = "hold"
	return {"ok": true, "scale": scale, "action": "hold", "reason": "in_band"}


func apply(viewport: Viewport) -> bool:
	if viewport == null:
		last_error = "viewport is required"
		return false
	viewport.scaling_3d_scale = scale
	return true


func reset() -> void:
	scale = max_scale
	_last_change_frame = -1000000
	_last_action = "hold"
	last_error = ""


func get_state() -> Dictionary:
	return {"scale": scale, "min_scale": min_scale, "max_scale": max_scale,
		"target_ms": target_ms, "step": step, "cooldown_frames": cooldown_frames,
		"last_action": _last_action}
