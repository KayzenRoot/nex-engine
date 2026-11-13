extends Node3D
class_name RenderPassport

# NEX-M02-S05 prototype: capability matrix and reversible graphics profiles.
# Inventory/passport only: no rendering, no project.godot writes, no remote
# hardware collection, and no capability inferred from a GPU marketing name.
# Documented capability states remain DOCUMENTED_UNVERIFIED unless a runtime
# probe supplies the actual value.

const MATRIX_PATH := "res://capability_matrix.v1.json"
const PROFILES_PATH := "res://profiles.v1.json"

var last_error := ""
var matrix: Dictionary = {}
var profiles_doc: Dictionary = {}
var _last_report: Dictionary = {}


func _ready() -> void:
	load_data()


func load_data() -> bool:
	var loaded_matrix = _read_json(MATRIX_PATH)
	var loaded_profiles = _read_json(PROFILES_PATH)
	if not (loaded_matrix is Dictionary) or loaded_matrix.is_empty():
		last_error = "capability matrix is missing or invalid"
		return false
	if not (loaded_profiles is Dictionary) or loaded_profiles.is_empty():
		last_error = "profiles document is missing or invalid"
		return false
	return configure({"matrix": loaded_matrix, "profiles": loaded_profiles})


func configure(overrides := {}) -> bool:
	last_error = ""
	var next_matrix = overrides.get("matrix", matrix)
	var next_profiles = overrides.get("profiles", profiles_doc)
	if not _validate_matrix(next_matrix):
		return false
	if not _validate_profiles(next_profiles):
		return false
	matrix = next_matrix
	profiles_doc = next_profiles
	return true


func list_profiles() -> Array:
	if profiles_doc.is_empty():
		return []
	return profiles_doc["profiles"].keys()


func build_passport(inventory: Dictionary, probe := {}) -> Dictionary:
	last_error = ""
	if not (probe is Dictionary):
		probe = {}
	var reason := _inventory_error(inventory)
	if not reason.is_empty():
		return _inconclusive_passport(reason)
	var effective := _resolve_effective(inventory)
	var capabilities: Array = []
	var probed := false
	for capability in matrix["capabilities"]:
		var id := str(capability["id"])
		var state := str(capability["states"].get(effective["renderer"], "UNKNOWN"))
		var verification := "DOCUMENTED_UNVERIFIED"
		if probe.has(id) and probe[id] is bool:
			state = "MEASURED_ENABLED" if bool(probe[id]) else "MEASURED_DISABLED"
			verification = "RUNTIME_PROBED"
			probed = true
		capabilities.append({
			"id": id,
			"category": str(capability["category"]),
			"state": state,
			"verification": verification,
			"source": str(capability["source"]),
		})
	_last_report = {
		"verdict": "OK",
		"action": "PASSPORT_READY",
		"inventory": {
			"godot": str(inventory.get("godot", "")),
			"os": str(inventory.get("os", "")),
			"renderer": str(inventory.get("renderer", "")),
			"driver": str(inventory.get("driver", "")),
			"gpu": str(inventory.get("gpu", "")),
			"vram_mib": inventory.get("vram_mib", 0),
		},
		"effective": effective,
		"probe_status": "RUNTIME_PROBED" if probed else "INCONCLUSIVE_NOT_PROBED",
		"capabilities": capabilities,
		"flags": {
			"project_godot_writes": false,
			"personal_hardware_collected": false,
			"gpu_name_implies_capability": false,
		},
		"limitations": _limitations(),
	}
	return _last_report.duplicate(true)


func select_profile(name: String, inventory: Dictionary, probe := {}) -> Dictionary:
	last_error = ""
	if profiles_doc.is_empty() or not profiles_doc["profiles"].has(name):
		last_error = "unknown profile: " + name
		return _inconclusive_profile(name, last_error)
	var passport := build_passport(inventory, probe)
	if passport["verdict"] != "OK":
		var report := _inconclusive_profile(name, str(passport.get("error", "inventory is inconclusive")))
		report["passport"] = passport
		return report
	var settings: Dictionary = profiles_doc["profiles"][name].duplicate(true)
	var states: Dictionary = {}
	for capability in passport["capabilities"]:
		states[capability["id"]] = capability["state"]
	var degraded_features: Array = []
	var feature_map := {
		"mesh_lod": "visibility.mesh_lod",
		"visibility_ranges": "visibility.visibility_ranges",
		"occlusion_culling": "visibility.occlusion_culling",
	}
	for key in feature_map.keys():
		var capability_id: String = feature_map[key]
		var state := str(states.get(capability_id, "UNKNOWN"))
		var supported: bool = state == "SUPPORTED" or state == "MEASURED_ENABLED"
		var wanted := bool(settings.get(key, false))
		settings[key] = wanted and supported
		if wanted and not settings[key]:
			degraded_features.append(key)
	settings["renderer"] = passport["effective"]["renderer"]
	settings["driver"] = passport["effective"]["driver"]
	var degraded: bool = bool(passport["effective"]["degraded"]) or not degraded_features.is_empty()
	var report := {
		"verdict": "DEGRADED" if degraded else "OK",
		"action": "USE_PROFILE",
		"profile": name,
		"settings": settings,
		"passport": passport,
		"degraded_features": degraded_features,
		"reversible": true,
		"writes_project_godot": false,
		"limitations": _limitations(),
	}
	_last_report = report
	return report.duplicate(true)


func switch_profile(from_name: String, to_name: String, inventory: Dictionary, probe := {}) -> Dictionary:
	last_error = ""
	var from_report := select_profile(from_name, inventory, probe)
	var to_report := select_profile(to_name, inventory, probe)
	if from_report["verdict"] == "INCONCLUSIVE" or to_report["verdict"] == "INCONCLUSIVE":
		last_error = "profile switch blocked: " + str(last_error)
		return {
			"verdict": "INCONCLUSIVE",
			"action": "BLOCKED_INCONCLUSIVE",
			"from": from_name,
			"to": to_name,
			"error": last_error,
			"writes_project_godot": false,
			"reversible": true,
			"limitations": _limitations(),
		}
	var from_settings: Dictionary = from_report["settings"]
	var to_settings: Dictionary = to_report["settings"]
	var diff: Dictionary = {}
	for key in to_settings.keys():
		if from_settings.get(key) != to_settings[key]:
			diff[key] = {"from": from_settings.get(key), "to": to_settings[key]}
	var revert := select_profile(from_name, inventory, probe)
	var round_trip: bool = revert["settings"] == from_settings
	var report := {
		"verdict": "OK" if to_report["verdict"] == "OK" and round_trip else "DEGRADED",
		"action": "SWITCH_PROFILE",
		"from": from_name,
		"to": to_name,
		"diff": diff,
		"round_trip": round_trip,
		"from_settings": from_settings,
		"to_settings": to_settings,
		"writes_project_godot": false,
		"reversible": true,
		"limitations": _limitations(),
	}
	_last_report = report
	return report.duplicate(true)


func get_report() -> Dictionary:
	return _last_report.duplicate(true)


func _resolve_effective(inventory: Dictionary) -> Dictionary:
	var renderer := str(inventory["renderer"])
	var driver := str(inventory["driver"])
	var chain: Array = []
	var degraded := false
	if renderer == "forward_plus":
		if driver == "vulkan" and inventory.get("vulkan_available", true) == false:
			chain.append("forward_plus+d3d12")
			if inventory.get("d3d12_available", true) == false:
				chain.append("gl_compatibility+opengl3")
				renderer = "gl_compatibility"
				driver = "opengl3"
				degraded = true
			else:
				driver = "d3d12"
		elif driver == "d3d12" and inventory.get("d3d12_available", true) == false:
			chain.append("gl_compatibility+opengl3")
			renderer = "gl_compatibility"
			driver = "opengl3"
			degraded = true
	if renderer == "gl_compatibility":
		degraded = true
	return {"renderer": renderer, "driver": driver, "degraded": degraded, "fallback_chain": chain}


func _inventory_error(inventory: Dictionary) -> String:
	if not (inventory is Dictionary) or inventory.is_empty():
		return "inventory must be a non-empty dictionary"
	if not str(inventory.get("godot", "")).begins_with("4.7"):
		return "only Godot 4.7 inventory is supported"
	if str(inventory.get("os", "")) != "Windows":
		return "Windows is the only audited reference OS"
	if str(inventory.get("gpu", "")).is_empty():
		return "gpu inventory is required"
	if not _is_number(inventory.get("vram_mib", null)) or float(inventory["vram_mib"]) <= 0.0:
		return "vram_mib must be a positive number"
	var renderer := str(inventory.get("renderer", ""))
	if not matrix.get("drivers", {}).has(renderer):
		return "unknown renderer: " + renderer
	var driver := str(inventory.get("driver", ""))
	if not matrix["drivers"][renderer].has(driver):
		return "driver not valid for renderer: " + driver
	for key in ["vulkan_available", "d3d12_available"]:
		if inventory.has(key) and not (inventory[key] is bool):
			return key + " must be boolean"
	return ""


func _validate_matrix(candidate) -> bool:
	if not (candidate is Dictionary) or candidate.is_empty():
		last_error = "matrix must be a non-empty dictionary"
		return false
	if str(candidate.get("schema_version", "")) != "nex_m02_capability_matrix.v1":
		last_error = "unsupported matrix schema"
		return false
	var capabilities = candidate.get("capabilities")
	if not (capabilities is Array) or capabilities.is_empty():
		last_error = "matrix capabilities must be a non-empty array"
		return false
	var allowed_states := ["SUPPORTED", "UNSUPPORTED", "FALLBACK", "REQUIRES_MEASUREMENT", "UNKNOWN"]
	for capability in capabilities:
		if not (capability is Dictionary):
			last_error = "capability entry must be a dictionary"
			return false
		for key in ["id", "category", "states", "source"]:
			if not capability.has(key):
				last_error = "capability missing " + key
				return false
		if not (capability["states"] is Dictionary):
			last_error = "capability states must be a dictionary"
			return false
		for renderer in ["forward_plus", "gl_compatibility"]:
			if not capability["states"].has(renderer) or not allowed_states.has(str(capability["states"][renderer])):
				last_error = "capability state invalid for " + str(capability.get("id", "?"))
				return false
	if not (candidate.get("drivers") is Dictionary) or not (candidate.get("fallbacks") is Dictionary):
		last_error = "matrix drivers/fallbacks must be dictionaries"
		return false
	return true


func _validate_profiles(candidate) -> bool:
	if not (candidate is Dictionary) or candidate.is_empty():
		last_error = "profiles must be a non-empty dictionary"
		return false
	if str(candidate.get("schema_version", "")) != "nex_m02_profiles.v1":
		last_error = "unsupported profiles schema"
		return false
	var profiles = candidate.get("profiles")
	if not (profiles is Dictionary):
		last_error = "profiles map is required"
		return false
	var expected := ["balanced", "performance", "quality"]
	if profiles.keys().size() != expected.size():
		last_error = "exactly quality, balanced and performance are allowed"
		return false
	for name in expected:
		if not profiles.has(name):
			last_error = "missing profile: " + name
			return false
		if not _validate_profile(profiles[name]):
			return false
	if not profiles.has(str(candidate.get("defaults", ""))):
		last_error = "defaults must name an existing profile"
		return false
	return true


func _validate_profile(profile) -> bool:
	if not (profile is Dictionary):
		last_error = "profile must be a dictionary"
		return false
	for key in ["renderer", "driver", "render_scale", "msaa", "vsync", "max_fps", "mesh_lod",
				"visibility_ranges", "occlusion_culling", "camera_distance_m", "pixel_snap"]:
		if not profile.has(key):
			last_error = "profile missing " + key
			return false
	if str(profile["renderer"]) not in ["forward_plus", "gl_compatibility"]:
		last_error = "profile renderer invalid"
		return false
	if str(profile["driver"]) not in ["vulkan", "d3d12", "opengl3"]:
		last_error = "profile driver invalid"
		return false
	if matrix.has("drivers") and matrix["drivers"].has(str(profile["renderer"])):
		if not matrix["drivers"][str(profile["renderer"])].has(str(profile["driver"])):
			last_error = "profile driver is not valid for its renderer"
			return false
	if not _is_number(profile["render_scale"]) or float(profile["render_scale"]) < 0.5 or float(profile["render_scale"]) > 1.0:
		last_error = "render_scale outside [0.5,1]"
		return false
	if str(profile["msaa"]) not in ["disabled", "2x", "4x", "8x"]:
		last_error = "msaa invalid"
		return false
	if not _is_integer_number(profile["vsync"]) or int(profile["vsync"]) < 0 or int(profile["vsync"]) > 2:
		last_error = "vsync invalid"
		return false
	if not _is_integer_number(profile["max_fps"]) or int(profile["max_fps"]) < 0 or int(profile["max_fps"]) > 240:
		last_error = "max_fps invalid"
		return false
	for key in ["mesh_lod", "visibility_ranges", "occlusion_culling", "pixel_snap"]:
		if not (profile[key] is bool):
			last_error = key + " must be boolean"
			return false
	if not _is_number(profile["camera_distance_m"]) or float(profile["camera_distance_m"]) < 1.0 or float(profile["camera_distance_m"]) > 200.0:
		last_error = "camera_distance_m outside [1,200]"
		return false
	return true


func _inconclusive_passport(reason: String) -> Dictionary:
	last_error = reason
	_last_report = {
		"verdict": "INCONCLUSIVE",
		"action": "BLOCKED_INCONCLUSIVE",
		"error": reason,
		"effective": {},
		"capabilities": [],
		"probe_status": "INCONCLUSIVE_NOT_PROBED",
		"flags": {
			"project_godot_writes": false,
			"personal_hardware_collected": false,
			"gpu_name_implies_capability": false,
		},
		"limitations": _limitations(),
	}
	return _last_report.duplicate(true)


func _inconclusive_profile(name: String, reason: String) -> Dictionary:
	last_error = reason
	var report := {
		"verdict": "INCONCLUSIVE",
		"action": "BLOCKED_INCONCLUSIVE",
		"profile": name,
		"error": reason,
		"settings": {},
		"degraded_features": [],
		"reversible": true,
		"writes_project_godot": false,
		"limitations": _limitations(),
	}
	_last_report = report
	return report.duplicate(true)


func _read_json(path: String):
	var text := FileAccess.get_file_as_string(path)
	if text.is_empty():
		return {}
	var parsed: Variant = JSON.parse_string(text)
	return parsed if parsed is Dictionary else {}


func _limitations() -> Array:
	return [
		"documentation-derived capability states are unverified until a runtime probe supplies them",
		"no rendering, benchmark, screenshot or frame-time is executed",
		"GPU name never implies a capability; the passport reports inventory and probe separately",
		"no project.godot write, no remote hardware collection and no telemetry upload",
		"profiles are settings, not measured performance; no FPS claim is made",
	]


func _is_number(value) -> bool:
	return (value is int or value is float) and not (value is bool) and is_finite(float(value))


func _is_integer_number(value) -> bool:
	return _is_number(value) and float(value) == floorf(float(value))
