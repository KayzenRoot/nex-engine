extends Node
class_name FeedbackPlanner

# NEX-M10-FEEDBACK prototype: deterministic combat-feedback planner.
# Planning only: no animation, camera, shader, scene or renderer is created.
# Vocabulary follows the integrated feedback.v1 contract.

enum Phase { ANTICIPATION, ACTIVE, RECOVERY }
enum Element { FIRE, ICE, LIGHTNING, ARCANE, NATURE, PHYSICAL }
enum Channel { HIT_STOP, CAMERA_SHAKE, FLASH, RECOIL, DAMAGE_NUMBER }

const PHASE_NAMES: Array[String] = ["anticipation", "active", "recovery"]
const ELEMENT_NAMES: Array[String] = ["fire", "ice", "lightning", "arcane", "nature", "physical"]
const CHANNEL_NAMES: Array[String] = ["hit_stop", "camera_shake", "flash", "recoil", "damage_number"]
const FEEDBACK_TAIL_MS := 1000
const MAX_DURATION_MS := 10000
const MAX_EVENTS := 32
const MAX_CHANNELS := 32

var max_hit_stop_ms := 80
var max_shake_amplitude := 0.8
var max_concurrent_channels := 5
var max_total_channels := 8
var last_error := ""
var _attack_id := ""
var _phases: Array = []
var _events: Dictionary = {}
var _event_order: Array[String] = []
var _channels: Dictionary = {}
var _channel_order: Array[String] = []
var _last_plan: Dictionary = {}


func configure(config := {}) -> bool:
	last_error = ""
	var next_hit_stop := int(config.get("max_hit_stop_ms", max_hit_stop_ms))
	var next_shake := float(config.get("max_shake_amplitude", max_shake_amplitude))
	var next_concurrent := int(config.get("max_concurrent_channels", max_concurrent_channels))
	var next_total := int(config.get("max_total_channels", max_total_channels))
	if next_hit_stop < 0 or next_hit_stop > 500:
		last_error = "max_hit_stop_ms outside [0,500]"
		return false
	if not is_finite(next_shake) or next_shake < 0.0 or next_shake > 2.0:
		last_error = "max_shake_amplitude outside [0,2]"
		return false
	if next_concurrent < 1 or next_concurrent > 16:
		last_error = "max_concurrent_channels outside [1,16]"
		return false
	if next_total < 1 or next_total > MAX_CHANNELS:
		last_error = "max_total_channels outside [1,32]"
		return false
	max_hit_stop_ms = next_hit_stop
	max_shake_amplitude = next_shake
	max_concurrent_channels = next_concurrent
	max_total_channels = next_total
	return true


func set_attack(attack_id: String, phases: Array) -> bool:
	last_error = ""
	if not _is_contract_id(attack_id):
		last_error = "attack id does not match the contract"
		return false
	if phases.is_empty() or phases.size() > 3:
		last_error = "attack requires 1..3 phases"
		return false
	var next: Array = []
	var names: Array[String] = []
	var total := 0
	for phase in phases:
		if not phase is Dictionary:
			last_error = "phase must be an object"
			return false
		var kind := int(phase.get("phase", -1))
		if kind < Phase.ANTICIPATION or kind > Phase.RECOVERY:
			last_error = "invalid phase"
			return false
		if not phase.has("duration_ms") or not _is_integer(phase["duration_ms"]):
			last_error = "phase requires integer duration_ms"
			return false
		var duration := int(phase["duration_ms"])
		if duration < 0 or duration > MAX_DURATION_MS:
			last_error = "phase duration outside [0,10000]"
			return false
		if names.has(PHASE_NAMES[kind]):
			last_error = "duplicate phase"
			return false
		names.append(PHASE_NAMES[kind])
		total += duration
		next.append({"phase": kind, "duration_ms": duration})
	if not names.has("active"):
		last_error = "active phase is required"
		return false
	if total > MAX_DURATION_MS:
		last_error = "total attack duration exceeds 10000 ms"
		return false
	_attack_id = attack_id
	_phases = next
	return true


func register_hit_event(event_id: String, at_ms: int, target_id: String, damage: int, critical: bool, element: int) -> bool:
	last_error = ""
	if not _is_contract_id(event_id):
		last_error = "event id does not match the contract"
		return false
	if _events.has(event_id):
		last_error = "duplicate event id: " + event_id
		return false
	if _events.size() >= MAX_EVENTS:
		last_error = "max hit events reached"
		return false
	if at_ms < 0 or at_ms > MAX_DURATION_MS:
		last_error = "event time outside [0,10000]"
		return false
	if not _is_contract_id(target_id):
		last_error = "target id does not match the contract"
		return false
	if damage < 0 or damage > 1000000:
		last_error = "damage outside [0,1000000]"
		return false
	if element < Element.FIRE or element > Element.PHYSICAL:
		last_error = "invalid element"
		return false
	_events[event_id] = {
		"at_ms": at_ms, "target_id": target_id, "damage": damage,
		"critical": critical, "element": element,
	}
	_event_order.append(event_id)
	return true


func register_channel(channel_id: String, channel: int, start_ms: int, duration_ms: int,
		intensity: float, priority: int, event_id := "", target_id := "") -> bool:
	last_error = ""
	if not _is_contract_id(channel_id):
		last_error = "channel id does not match the contract"
		return false
	if _channels.has(channel_id):
		last_error = "duplicate channel id: " + channel_id
		return false
	if _channels.size() >= MAX_CHANNELS:
		last_error = "max channels reached"
		return false
	if channel < Channel.HIT_STOP or channel > Channel.DAMAGE_NUMBER:
		last_error = "invalid channel type"
		return false
	if start_ms < 0 or start_ms > MAX_DURATION_MS:
		last_error = "channel start outside [0,10000]"
		return false
	if duration_ms < 0 or duration_ms > 5000:
		last_error = "channel duration outside [0,5000]"
		return false
	if not is_finite(intensity) or intensity < 0.0 or intensity > 1.0:
		last_error = "intensity outside [0,1]"
		return false
	if priority < 0 or priority > 10:
		last_error = "priority outside [0,10]"
		return false
	if not event_id.is_empty() and not _is_contract_id(event_id):
		last_error = "event id does not match the contract"
		return false
	if not target_id.is_empty() and not _is_contract_id(target_id):
		last_error = "target id does not match the contract"
		return false
	_channels[channel_id] = {
		"channel": channel, "start_ms": start_ms, "duration_ms": duration_ms,
		"intensity": intensity, "priority": priority, "event_id": event_id, "target_id": target_id,
	}
	_channel_order.append(channel_id)
	return true


func plan() -> Dictionary:
	last_error = ""
	if _attack_id.is_empty() or _phases.is_empty():
		return _invalid("attack is not configured")
	if _channels.is_empty():
		return _invalid("at least one feedback channel is required")
	var total := _total_duration()
	var conflicts: Array = []
	for event_id in _event_order:
		var event: Dictionary = _events[event_id]
		if int(event["at_ms"]) > total:
			conflicts.append(_finding("event_outside_attack", "high", "hit event is outside the attack duration", event_id, "event_id"))
		if bool(event["critical"]) and int(event["damage"]) <= 0:
			conflicts.append(_finding("critical_without_damage", "high", "critical event has no damage", event_id, "event_id"))
	var peak_concurrency := 0
	var total_hit_stop := 0
	var max_shake := 0.0
	var damage_numbers := 0
	for channel_id in _channel_order:
		var channel: Dictionary = _channels[channel_id]
		var start := int(channel["start_ms"])
		var end := start + int(channel["duration_ms"])
		if start > total or end > total + FEEDBACK_TAIL_MS:
			conflicts.append(_finding("channel_outside_window", "high", "channel is outside the attack window plus tail", channel_id))
		var event_id := String(channel["event_id"])
		if not event_id.is_empty() and not _events.has(event_id):
			conflicts.append(_finding("dangling_event", "high", "channel references an unknown hit event", channel_id))
		if int(channel["channel"]) == Channel.DAMAGE_NUMBER:
			damage_numbers += 1
			var event: Dictionary = _events.get(event_id, {})
			if event.is_empty() or int(event.get("damage", 0)) <= 0:
				conflicts.append(_finding("damage_number_without_damage", "high", "damage number requires positive damage", channel_id))
		if int(channel["channel"]) == Channel.HIT_STOP:
			total_hit_stop += int(channel["duration_ms"])
			if int(channel["duration_ms"]) > max_hit_stop_ms:
				conflicts.append(_finding("hit_stop_over_budget", "high", "hit-stop duration exceeds the budget", channel_id))
		if int(channel["channel"]) == Channel.CAMERA_SHAKE:
			max_shake = maxf(max_shake, float(channel["intensity"]))
			if float(channel["intensity"]) > max_shake_amplitude:
				conflicts.append(_finding("shake_over_budget", "high", "camera shake exceeds the budget", channel_id))
		var active := _active_at(start)
		peak_concurrency = maxi(peak_concurrency, active)
		if active > max_concurrent_channels:
			conflicts.append(_finding("concurrency_over_budget", "high", "too many concurrent channels at this start", channel_id))
	if _channels.size() > max_total_channels:
		conflicts.append(_finding("total_channels_over_budget", "high", "channel count exceeds max_total_channels"))
	var timeline: Array = []
	var ordered := _channel_order.duplicate()
	ordered.sort_custom(func(a, b):
		var ca: Dictionary = _channels[a]
		var cb: Dictionary = _channels[b]
		if int(ca["start_ms"]) != int(cb["start_ms"]):
			return int(ca["start_ms"]) < int(cb["start_ms"])
		if int(ca["priority"]) != int(cb["priority"]):
			return int(ca["priority"]) > int(cb["priority"])
		return a < b
	)
	for channel_id in ordered:
		var channel: Dictionary = _channels[channel_id]
		var entry := {
			"channel_id": channel_id,
			"channel": CHANNEL_NAMES[int(channel["channel"])],
			"start_ms": int(channel["start_ms"]),
			"duration_ms": int(channel["duration_ms"]),
			"end_ms": int(channel["start_ms"]) + int(channel["duration_ms"]),
			"intensity": channel["intensity"],
			"priority": int(channel["priority"]),
		}
		if not String(channel["event_id"]).is_empty():
			entry["event_id"] = channel["event_id"]
		if not String(channel["target_id"]).is_empty():
			entry["target_id"] = channel["target_id"]
		timeline.append(entry)
	var report := {
		"schema_version": "feedback.plan.v1",
		"verdict": _verdict(conflicts),
		"attack": {
			"attack_id": _attack_id,
			"phases": _export_phases(),
			"total_duration_ms": total,
		},
		"hit_events": _export_events(),
		"timeline": timeline,
		"budget": {
			"max_hit_stop_ms": max_hit_stop_ms,
			"max_shake_amplitude": max_shake_amplitude,
			"max_concurrent_channels": max_concurrent_channels,
			"max_total_channels": max_total_channels,
		},
		"metrics": {
			"total_channels": _channels.size(),
			"peak_concurrency": peak_concurrency,
			"total_hit_stop_ms": total_hit_stop,
			"max_shake_intensity": snappedf(max_shake, 0.001),
			"damage_numbers": damage_numbers,
		},
		"conflicts": _sorted_findings(conflicts),
		"summary": _summary(conflicts),
		"limitations": _limitations(),
	}
	_last_plan = report
	return report


func export_observation(observation_id: String, captured_at_utc: String, provenance: Dictionary) -> Dictionary:
	last_error = ""
	if not _is_contract_id(observation_id):
		last_error = "observation id does not match the contract"
		return {}
	if captured_at_utc.is_empty():
		last_error = "captured_at_utc is required"
		return {}
	if not _valid_provenance(provenance):
		return {}
	var generated := plan()
	if generated["verdict"] != "SAFE_CONFIG_HEURISTIC":
		last_error = "resolve feedback conflicts before exporting an observation"
		return {}
	var channels: Array = []
	for entry in generated["timeline"]:
		var channel := {
			"channel_id": entry["channel_id"],
			"channel": entry["channel"],
			"start_ms": entry["start_ms"],
			"duration_ms": entry["duration_ms"],
			"intensity": entry["intensity"],
			"priority": entry["priority"],
		}
		if entry.has("event_id"):
			channel["event_id"] = entry["event_id"]
		if entry.has("target_id"):
			channel["target_id"] = entry["target_id"]
		channels.append(channel)
	return {
		"schema_version": "feedback.v1",
		"observation_id": observation_id,
		"captured_at_utc": captured_at_utc,
		"attack": {
			"attack_id": generated["attack"]["attack_id"],
			"phases": generated["attack"]["phases"],
		},
		"hit_events": generated["hit_events"],
		"feedback_channels": channels,
		"budget": generated["budget"],
		"performance": {
			"measurement_status": "UNAVAILABLE",
			"frame_interval": {"status": "UNAVAILABLE", "provider": "SceneTree._process(delta)", "unavailable_reason": "planner does not render"},
			"gpu_render_time": {"status": "UNAVAILABLE", "unavailable_reason": "planner does not render"},
			"cpu_render_time": {"status": "UNAVAILABLE", "unavailable_reason": "planner does not render"},
			"draw_calls": {"status": "UNAVAILABLE", "unavailable_reason": "planner does not render"},
			"renderer_allocation_bytes": {"status": "UNAVAILABLE", "unavailable_reason": "planner does not render"},
		},
		"provenance": provenance.duplicate(true),
	}


func _total_duration() -> int:
	var total := 0
	for phase in _phases:
		total += int(phase["duration_ms"])
	return total


func _active_at(instant: int) -> int:
	var active := 0
	for channel_id in _channel_order:
		var channel: Dictionary = _channels[channel_id]
		var start := int(channel["start_ms"])
		var end := start + int(channel["duration_ms"])
		if start <= instant and instant < end:
			active += 1
	return active


func _export_phases() -> Array:
	var phases: Array = []
	for phase in _phases:
		phases.append({"phase": PHASE_NAMES[int(phase["phase"])], "duration_ms": int(phase["duration_ms"])})
	return phases


func _export_events() -> Array:
	var events: Array = []
	var ids := _event_order.duplicate()
	ids.sort()
	for event_id in ids:
		var event: Dictionary = _events[event_id]
		events.append({
			"event_id": event_id,
			"at_ms": int(event["at_ms"]),
			"target_id": event["target_id"],
			"damage": int(event["damage"]),
			"critical": event["critical"],
			"element": ELEMENT_NAMES[int(event["element"])],
		})
	return events


func _verdict(conflicts: Array) -> String:
	for finding in conflicts:
		if finding["severity"] == "high" or finding["severity"] == "medium":
			return "CONFLICTS_REPORTED"
	return "SAFE_CONFIG_HEURISTIC"


func _summary(conflicts: Array) -> Dictionary:
	var summary := {"high": 0, "medium": 0, "low": 0, "info": 0}
	for finding in conflicts:
		summary[finding["severity"]] += 1
	return summary


func _finding(code: String, severity: String, message: String, subject_id := "", subject_field := "channel_id") -> Dictionary:
	var finding := {"code": code, "severity": severity, "message": message}
	if not subject_id.is_empty():
		finding[subject_field] = subject_id
	return finding


func _sorted_findings(findings: Array) -> Array:
	var order := {"high": 0, "medium": 1, "low": 2, "info": 3}
	findings.sort_custom(func(a, b):
		if order[a["severity"]] == order[b["severity"]]:
			return String(a["code"]) < String(b["code"])
		return order[a["severity"]] < order[b["severity"]]
	)
	return findings


func _limitations() -> Array[String]:
	return [
		"planning only: no animation, camera, shader, scene or renderer is created",
		"hit-stop and shake budgets are arithmetic, not measured game feel",
		"concurrency counts channel intervals at their start instants, not rendered overlap",
		"priority orders the timeline but does not resolve or suppress conflicts",
		"readability and runtime cost are INCONCLUSIVE_NOT_RUN",
		"no scene, engine or project.godot integration",
	]


func _invalid(reason: String) -> Dictionary:
	last_error = reason
	var report := {
		"schema_version": "feedback.plan.v1",
		"verdict": "INVALID_INPUT",
		"attack": {},
		"hit_events": [],
		"timeline": [],
		"budget": {
			"max_hit_stop_ms": max_hit_stop_ms,
			"max_shake_amplitude": max_shake_amplitude,
			"max_concurrent_channels": max_concurrent_channels,
			"max_total_channels": max_total_channels,
		},
		"metrics": {},
		"conflicts": [],
		"summary": {"high": 0, "medium": 0, "low": 0, "info": 0},
		"limitations": _limitations(),
		"reason": reason,
	}
	_last_plan = report
	return report


func _is_integer(value) -> bool:
	return value is int or (value is float and is_finite(value) and value == floor(value))


func _is_contract_id(value: String) -> bool:
	if value.length() < 2 or value.length() > 64:
		return false
	for index in range(value.length()):
		var character := value[index]
		if index == 0:
			if not "abcdefghijklmnopqrstuvwxyz0123456789".contains(character):
				return false
		elif not "abcdefghijklmnopqrstuvwxyz0123456789._-".contains(character):
			return false
	return true


func _valid_provenance(provenance: Dictionary) -> bool:
	for key in ["base_sha", "head_sha", "godot_version", "hardware", "capture_mode", "measurement_status"]:
		if not provenance.has(key):
			last_error = "provenance missing " + key
			return false
	if not _is_sha(provenance["base_sha"]) or not _is_sha(provenance["head_sha"]):
		last_error = "provenance SHAs must be lowercase 40-hex"
		return false
	var hardware = provenance["hardware"]
	if not (hardware is Dictionary) or not hardware.has("gpu_model") or not hardware.has("driver_version"):
		last_error = "provenance hardware incomplete"
		return false
	if not ["windowed", "fullscreen", "headless"].has(provenance["capture_mode"]):
		last_error = "invalid capture mode"
		return false
	if not ["MEASURED", "UNAVAILABLE"].has(provenance["measurement_status"]):
		last_error = "invalid provenance measurement status"
		return false
	if provenance["measurement_status"] == "MEASURED" and not provenance.has("evidence_uri"):
		last_error = "MEASURED provenance requires evidence_uri"
		return false
	return true


func _is_sha(value: String) -> bool:
	if value.length() != 40:
		return false
	for character in value:
		if not "0123456789abcdef".contains(character):
			return false
	return true


func get_last_plan() -> Dictionary:
	return _last_plan


func clear() -> void:
	_attack_id = ""
	_phases.clear()
	_events.clear()
	_event_order.clear()
	_channels.clear()
	_channel_order.clear()
	_last_plan = {}
	last_error = ""
	max_hit_stop_ms = 80
	max_shake_amplitude = 0.8
	max_concurrent_channels = 5
	max_total_channels = 8
