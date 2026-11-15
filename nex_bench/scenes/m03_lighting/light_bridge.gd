extends Node
class_name LightBridge

# NEX M03-S05 LightBridge: versioned, deterministic request bridge between
# visual effects and the M03 light allocator. Planning only: no light is
# created here; the renderer/allocator consumes accepted requests.
# Vocabulary follows lighting.v1.

const MAX_REQUESTS := 64
const MAX_ACTIVE := 16
const MAX_PER_GROUP := 8
const MAX_TIMEOUT_MS := 2000
const SHADOW_POLICIES: Array[String] = ["none", "soft", "hard"]

var max_active := MAX_ACTIVE
var max_per_group := MAX_PER_GROUP
var timeout_ms := 500
var last_error := ""
var _now_ms := 0
var _requests: Dictionary = {}
var _order: Array[String] = []


func configure(config := {}) -> bool:
	last_error = ""
	var next_active := int(config.get("max_active", max_active))
	var next_group := int(config.get("max_per_group", max_per_group))
	var next_timeout := int(config.get("timeout_ms", timeout_ms))
	if next_active < 1 or next_active > MAX_ACTIVE:
		last_error = "max_active outside [1,16]"
		return false
	if next_group < 1 or next_group > MAX_PER_GROUP:
		last_error = "max_per_group outside [1,8]"
		return false
	if next_timeout < 0 or next_timeout > MAX_TIMEOUT_MS:
		last_error = "timeout_ms outside [0,2000]"
		return false
	max_active = next_active
	max_per_group = next_group
	timeout_ms = next_timeout
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


func _number(value) -> bool:
	return (value is int or value is float) and is_finite(float(value))


func _valid_request(request) -> String:
	if not request is Dictionary:
		return "request must be an object"
	for key in ["request_id", "effect_id", "budget_group", "shadow_policy"]:
		if not request.has(key) or not _valid_id(request[key]):
			return key + " is invalid"
	if not request.has("position") or not request["position"] is Array or request["position"].size() != 3:
		return "position must be an array of 3"
	for value in request["position"]:
		if not _number(value):
			return "position values must be finite"
	if not request.has("color") or not request["color"] is Array or request["color"].size() != 4:
		return "color must be an array of 4"
	for value in request["color"]:
		if not _number(value) or float(value) < 0.0 or float(value) > 1.0:
			return "color values must be within [0,1]"
	if not request.has("radius") or not _number(request["radius"]) or float(request["radius"]) < 0.0 or float(request["radius"]) > 50.0:
		return "radius outside [0,50]"
	if not request.has("intensity") or not _number(request["intensity"]) or float(request["intensity"]) < 0.0 or float(request["intensity"]) > 100.0:
		return "intensity outside [0,100]"
	if not request.has("duration_ms") or not _number(request["duration_ms"]):
		return "duration_ms must be finite"
	if int(request["duration_ms"]) < 0 or int(request["duration_ms"]) > 10000:
		return "duration_ms outside [0,10000]"
	if not request.has("priority") or not _number(request["priority"]):
		return "priority must be finite"
	if int(request["priority"]) < 0 or int(request["priority"]) > 10:
		return "priority outside [0,10]"
	if not SHADOW_POLICIES.has(String(request["shadow_policy"])):
		return "shadow_policy is invalid"
	return ""


func _group_count(group: String) -> int:
	var count := 0
	for id in _requests.keys():
		if String(_requests[id]["budget_group"]) == group:
			count += 1
	return count


func _lowest_priority() -> String:
	var chosen := ""
	for id in _order:
		if not _requests.has(id):
			continue
		if chosen.is_empty() or int(_requests[id]["priority"]) < int(_requests[chosen]["priority"]):
			chosen = id
	return chosen


func submit(request: Dictionary) -> Dictionary:
	last_error = ""
	var error := _valid_request(request)
	if not error.is_empty():
		last_error = error
		return {"accepted": false, "reason": error}
	var request_id := String(request["request_id"])
	if _requests.has(request_id):
		last_error = "duplicate request_id"
		return {"accepted": false, "reason": last_error}
	if _requests.size() >= MAX_REQUESTS:
		last_error = "max requests reached"
		return {"accepted": false, "reason": last_error}
	var preempted: Array[String] = []
	if _requests.size() >= max_active:
		var victim := _lowest_priority()
		if victim.is_empty() or int(request["priority"]) <= int(_requests[victim]["priority"]):
			last_error = "budget_full"
			return {"accepted": false, "reason": last_error}
		_requests.erase(victim)
		_order.erase(victim)
		preempted.append(victim)
	var group := String(request["budget_group"])
	if _group_count(group) >= max_per_group:
		last_error = "group_full"
		return {"accepted": false, "reason": last_error}
	var entry := request.duplicate(true)
	entry["accepted_at_ms"] = _now_ms
	entry["expires_at_ms"] = _now_ms + int(request["duration_ms"])
	_requests[request_id] = entry
	_order.append(request_id)
	return {"accepted": true, "request_id": request_id, "preempted": preempted}


func tick(now_ms: int) -> Array[String]:
	_now_ms = maxi(_now_ms, now_ms)
	var expired: Array[String] = []
	for id in _order.duplicate():
		if not _requests.has(id):
			continue
		if int(_requests[id]["expires_at_ms"]) <= _now_ms:
			_requests.erase(id)
			_order.erase(id)
			expired.append(id)
	return expired


func get_state() -> Dictionary:
	var groups := {}
	for id in _requests.keys():
		var group := String(_requests[id]["budget_group"])
		groups[group] = int(groups.get(group, 0)) + 1
	return {
		"now_ms": _now_ms,
		"active": _requests.size(),
		"max_active": max_active,
		"max_per_group": max_per_group,
		"groups": groups,
		"requests": _requests.keys(),
	}


func clear() -> void:
	_requests.clear()
	_order.clear()
	_now_ms = 0
	last_error = ""
