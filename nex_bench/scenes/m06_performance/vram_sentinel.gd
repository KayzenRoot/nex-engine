extends RefCounted
class_name VRAMSentinel

# NEX M06-S09 VRAM Sentinel: process-visible engine memory monitors plus a
# hysteresis policy. It does not claim total device VRAM or OOM control.

var budget_bytes := 6000000000
var warn_ratio := 0.80
var critical_ratio := 0.92
var hysteresis_ratio := 0.03
var last_error := ""
var _state := "OK"


func configure(config := {}) -> bool:
	last_error = ""
	var next_budget := int(config.get("budget_bytes", budget_bytes))
	var next_warn := float(config.get("warn_ratio", warn_ratio))
	var next_critical := float(config.get("critical_ratio", critical_ratio))
	var next_hysteresis := float(config.get("hysteresis_ratio", hysteresis_ratio))
	if next_budget < 1:
		last_error = "budget_bytes must be positive"
		return false
	if next_warn <= 0.0 or next_critical > 1.0 or next_warn >= next_critical:
		last_error = "require 0 < warn < critical <= 1"
		return false
	if next_hysteresis < 0.0 or next_hysteresis >= next_warn:
		last_error = "invalid hysteresis_ratio"
		return false
	budget_bytes = next_budget
	warn_ratio = next_warn
	critical_ratio = next_critical
	hysteresis_ratio = next_hysteresis
	return true


func sample() -> Dictionary:
	var video := float(Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED))
	var texture := float(Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED))
	var buffer := float(Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED))
	var measured := video > 0.0
	return {
		"status": "MEASURED" if measured else "UNAVAILABLE",
		"provider": "Performance.RENDER_VIDEO_MEM_USED / TEXTURE / BUFFER",
		"video_bytes": int(video) if measured else null,
		"texture_bytes": int(texture) if texture > 0.0 else null,
		"buffer_bytes": int(buffer) if buffer > 0.0 else null,
		"unavailable_reason": "" if measured else "engine monitor returned 0 in this process",
	}


func evaluate(sample_document: Dictionary) -> Dictionary:
	if String(sample_document.get("status", "")) != "MEASURED":
		_state = "UNKNOWN"
		return {"state": "UNKNOWN", "ratio": null, "reason": "memory monitor unavailable"}
	var used := float(sample_document["video_bytes"])
	var ratio := used / float(budget_bytes)
	if ratio >= critical_ratio:
		_state = "CRITICAL"
	elif ratio >= warn_ratio and _state != "CRITICAL":
		_state = "WARN"
	elif _state == "CRITICAL" and ratio <= critical_ratio - hysteresis_ratio:
		_state = "WARN"
	elif _state == "WARN" and ratio <= warn_ratio - hysteresis_ratio:
		_state = "OK"
	return {"state": _state, "ratio": snappedf(ratio, 0.0001), "used_bytes": int(used),
		"budget_bytes": budget_bytes}


func reset() -> void:
	_state = "OK"
	last_error = ""


func get_state() -> Dictionary:
	return {"state": _state, "budget_bytes": budget_bytes, "warn_ratio": warn_ratio,
		"critical_ratio": critical_ratio, "hysteresis_ratio": hysteresis_ratio}
