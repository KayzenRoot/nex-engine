extends Node
class_name StreamGuard

# NEX M06-S05 StreamGuard: async ResourceLoader state machine with a small
# cache. It never calls load_threaded_get before the resource is READY.

const MAX_CACHE := 64
const VALID_STATES := ["idle", "loading", "ready", "failed"]

var max_cache := MAX_CACHE
var last_error := ""
var _entries: Dictionary = {}
var _cache: Dictionary = {}


func configure(config := {}) -> bool:
	last_error = ""
	var requested := int(config.get("max_cache", max_cache))
	if requested < 1 or requested > MAX_CACHE:
		last_error = "max_cache outside [1,%d]" % MAX_CACHE
		return false
	max_cache = requested
	return true


func _valid_path(path: String) -> bool:
	if not path.begins_with("res://") or path.contains("..") or path.length() < 8:
		return false
	return true


func request(path: String) -> Dictionary:
	last_error = ""
	if not _valid_path(path):
		last_error = "path must be a res:// path without traversal"
		return {"accepted": false, "reason": last_error}
	if _cache.has(path):
		return {"accepted": true, "duplicate": true, "state": "ready"}
	if _entries.has(path):
		return {"accepted": true, "duplicate": true, "state": String(_entries[path]["state"])}
	if _cache.size() >= max_cache:
		last_error = "cache_full"
		return {"accepted": false, "reason": last_error}
	var error := ResourceLoader.load_threaded_request(path)
	if error != OK:
		_entries[path] = {"state": "failed", "error": error, "started_usec": Time.get_ticks_usec()}
		last_error = "load_threaded_request failed"
		return {"accepted": false, "reason": last_error, "state": "failed"}
	_entries[path] = {"state": "loading", "error": OK, "started_usec": Time.get_ticks_usec()}
	return {"accepted": true, "duplicate": false, "state": "loading"}


func poll() -> Dictionary:
	var ready: Array[String] = []
	var failed: Array[String] = []
	for path in _entries.keys():
		var entry: Dictionary = _entries[path]
		if String(entry["state"]) != "loading":
			continue
		var status := ResourceLoader.load_threaded_get_status(path)
		if status == ResourceLoader.THREAD_LOAD_LOADED:
			var resource := ResourceLoader.load_threaded_get(path)
			_cache[path] = resource
			entry["state"] = "ready"
			entry["elapsed_ms"] = (Time.get_ticks_usec() - int(entry["started_usec"])) / 1000.0
			ready.append(path)
		elif status == ResourceLoader.THREAD_LOAD_FAILED or status == ResourceLoader.THREAD_LOAD_INVALID_RESOURCE:
			entry["state"] = "failed"
			entry["error"] = status
			failed.append(path)
	return {"ready": ready, "failed": failed, "state": get_state()}


func get_resource(path: String) -> Resource:
	if not _cache.has(path):
		return null
	return _cache[path]


func get_entries() -> Dictionary:
	return _entries.duplicate(true)


func get_state() -> Dictionary:
	var counts := {"idle": 0, "loading": 0, "ready": 0, "failed": 0}
	for entry in _entries.values():
		var state := String(entry["state"])
		if counts.has(state):
			counts[state] += 1
	return {"entries": _entries.size(), "cached": _cache.size(), "counts": counts,
		"max_cache": max_cache}


func clear() -> void:
	_entries.clear()
	_cache.clear()
	last_error = ""
