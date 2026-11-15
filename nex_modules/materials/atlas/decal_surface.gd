extends Node
class_name DecalSurface

# NEX M04-S05 DecalSurfaceRequest: versioned request bridge for Decal3D
# projections. Planning only; the renderer consumes accepted requests.

const BLEND_MODES: Array[String] = ["mix", "add", "mul"]
const MAX_DECALS := 64
const MAX_PER_SURFACE := 16

var max_decals := MAX_DECALS
var max_per_surface := MAX_PER_SURFACE
var last_error := ""
var _now_ms := 0
var _requests: Dictionary = {}
var _order: Array[String] = []


func configure(config := {}) -> bool:
	last_error = ""
	var next_decals := int(config.get("max_decals", max_decals))
	var next_surface := int(config.get("max_per_surface", max_per_surface))
	if next_decals < 1 or next_decals > MAX_DECALS:
		last_error = "max_decals outside [1,64]"
		return false
	if next_surface < 1 or next_surface > MAX_PER_SURFACE:
		last_error = "max_per_surface outside [1,16]"
		return false
	max_decals = next_decals
	max_per_surface = next_surface
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
	for key in ["request_id", "effect_id", "surface_tag", "blend"]:
		if not request.has(key) or not _valid_id(request[key]):
			return key + " is invalid"
	if not BLEND_MODES.has(String(request["blend"])):
		return "blend is invalid"
	if not request.has("position") or not request["position"] is Array or request["position"].size() != 3:
		return "position must be an array of 3"
	if not request.has("projection") or not request["projection"] is Array or request["projection"].size() != 3:
		return "projection must be an array of 3"
	for value in request["position"] + request["projection"]:
		if not (value is int or value is float) or not is_finite(float(value)):
			return "position/projection values must be finite"
	if not request.has("duration_ms") or not request.has("fade_ms") or not request.has("priority"):
		return "duration_ms, fade_ms and priority are required"
	if int(request["duration_ms"]) < 0 or int(request["duration_ms"]) > 60000:
		return "duration_ms outside [0,60000]"
	if int(request["fade_ms"]) < 0 or int(request["fade_ms"]) > 60000:
		return "fade_ms outside [0,60000]"
	if int(request["priority"]) < 0 or int(request["priority"]) > 10:
		return "priority outside [0,10]"
	return ""


func _surface_count(tag: String) -> int:
	var count := 0
	for id in _requests.keys():
		if String(_requests[id]["surface_tag"]) == tag:
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
	var preempted: Array[String] = []
	if _requests.size() >= max_decals:
		var victim := _lowest_priority()
		if victim.is_empty() or int(request["priority"]) <= int(_requests[victim]["priority"]):
			last_error = "budget_full"
			return {"accepted": false, "reason": last_error}
		_requests.erase(victim)
		_order.erase(victim)
		preempted.append(victim)
	var surface := String(request["surface_tag"])
	if _surface_count(surface) >= max_per_surface:
		last_error = "surface_full"
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
	return {
		"now_ms": _now_ms,
		"active": _requests.size(),
		"max_decals": max_decals,
		"max_per_surface": max_per_surface,
		"requests": _requests.keys(),
	}


func clear() -> void:
	_requests.clear()
	_order.clear()
	_now_ms = 0
	last_error = ""
