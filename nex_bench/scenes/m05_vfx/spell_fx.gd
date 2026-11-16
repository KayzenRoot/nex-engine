extends Node
class_name SpellFX

# NEX M05-S01 SpellFX request bridge: deterministic SpawnFX events with
# idempotency, cancellation and quality tiers. Gameplay authority is data only;
# damage/hitbox remain owned by gameplay.

const QUALITY_TIERS: Array[String] = ["low", "medium", "high"]
const MAX_ACTIVE := 128
const MAX_PER_VFX := 64

var max_active := MAX_ACTIVE
var max_per_vfx := MAX_PER_VFX
var last_error := ""
var _now_ms := 0
var _events: Dictionary = {}
var _order: Array[String] = []


func configure(config := {}) -> bool:
	last_error = ""
	var next_active := int(config.get("max_active", max_active))
	var next_vfx := int(config.get("max_per_vfx", max_per_vfx))
	if next_active < 1 or next_active > MAX_ACTIVE:
		last_error = "max_active outside [1,128]"
		return false
	if next_vfx < 1 or next_vfx > MAX_PER_VFX:
		last_error = "max_per_vfx outside [1,64]"
		return false
	max_active = next_active
	max_per_vfx = next_vfx
	return true


func _valid_id(value) -> bool:
	if not value is String:
		return false
	var text := String(value)
	if text.length() < 2 or text.length() > 64:
		return false
	for index in range(text.length()):
		var character := text[index]
		if index == 0:
			if not "abcdefghijklmnopqrstuvwxyz0123456789".contains(character):
				return false
		elif not "abcdefghijklmnopqrstuvwxyz0123456789._-".contains(character):
			return false
	return true


func _valid_request(request) -> String:
	if not request is Dictionary:
		return "request must be an object"
	for key in ["event_id", "vfx_id", "quality_tier"]:
		if not request.has(key) or not _valid_id(request[key]):
			return key + " is invalid"
	if not QUALITY_TIERS.has(String(request["quality_tier"])):
		return "quality_tier is invalid"
	if not request.has("position") or not request["position"] is Array or request["position"].size() != 3:
		return "position must be an array of 3"
	for value in request["position"]:
		if not (value is int or value is float) or not is_finite(float(value)):
			return "position values must be finite"
	if not request.has("seed") or not (request["seed"] is int):
		return "seed must be an integer"
	if not request.has("lifetime_ms") or not (request["lifetime_ms"] is int):
		return "lifetime_ms must be an integer"
	if int(request["lifetime_ms"]) < 0 or int(request["lifetime_ms"]) > 10000:
		return "lifetime_ms outside [0,10000]"
	if not request.has("priority") or not (request["priority"] is int):
		return "priority must be an integer"
	if int(request["priority"]) < 0 or int(request["priority"]) > 10:
		return "priority outside [0,10]"
	var authority = request.get("gameplay_authority")
	if not (authority is Dictionary):
		return "gameplay_authority is required"
	if authority.get("damage_owner") != "gameplay" or authority.get("hit_detection") != "gameplay":
		return "gameplay authority must remain gameplay"
	if not (authority.get("cancel_on_death") is bool):
		return "cancel_on_death must be boolean"
	return ""


func _vfx_count(vfx_id: String) -> int:
	var count := 0
	for event_id in _events.keys():
		if String(_events[event_id]["vfx_id"]) == vfx_id:
			count += 1
	return count


func submit(request: Dictionary) -> Dictionary:
	last_error = ""
	var error := _valid_request(request)
	if not error.is_empty():
		last_error = error
		return {"accepted": false, "reason": error}
	var event_id := String(request["event_id"])
	if _events.has(event_id):
		return {"accepted": true, "duplicate": true, "event_id": event_id}
	if _events.size() >= max_active:
		last_error = "budget_full"
		return {"accepted": false, "reason": last_error}
	var vfx_id := String(request["vfx_id"])
	if _vfx_count(vfx_id) >= max_per_vfx:
		last_error = "vfx_budget_full"
		return {"accepted": false, "reason": last_error}
	var entry := request.duplicate(true)
	entry["accepted_at_ms"] = _now_ms
	entry["expires_at_ms"] = _now_ms + int(request["lifetime_ms"])
	_events[event_id] = entry
	_order.append(event_id)
	return {"accepted": true, "duplicate": false, "event_id": event_id}


func cancel(event_id: String) -> bool:
	if not _events.has(event_id):
		return false
	_events.erase(event_id)
	_order.erase(event_id)
	return true


func tick(now_ms: int) -> Array[String]:
	_now_ms = maxi(_now_ms, now_ms)
	var expired: Array[String] = []
	for event_id in _order.duplicate():
		if not _events.has(event_id):
			continue
		if int(_events[event_id]["expires_at_ms"]) <= _now_ms:
			_events.erase(event_id)
			_order.erase(event_id)
			expired.append(event_id)
	return expired


func get_state() -> Dictionary:
	return {
		"now_ms": _now_ms,
		"active": _events.size(),
		"max_active": max_active,
		"max_per_vfx": max_per_vfx,
		"events": _events.keys(),
	}


func clear() -> void:
	_events.clear()
	_order.clear()
	_now_ms = 0
	last_error = ""
