extends Node
class_name PresetResolver

# NEX-M09-RESOLVER prototype: deterministic preset-pack resolver.
# Planning only: no preset is applied to the engine, project.godot or a scene.
# Vocabulary follows the integrated preset_pack.v1 contract.

const RESOLUTION_SCHEMA := "preset_resolution.v1"
const PACK_SCHEMA := "preset_pack.v1"
const TIERS: Array[String] = ["low", "medium", "high", "ultra", "custom"]
const STANDARD_TIERS: Array[String] = ["low", "medium", "high", "ultra"]
const SHADOW_RANK := {"off": 0, "low": 1, "medium": 2, "high": 3, "ultra": 4}
const HARDWARE_TIERS: Array[String] = ["integrated", "desktop", "enthusiast"]
const BLOCKS: Array[String] = ["rendering", "lighting", "performance", "composition", "feedback", "accessibility"]
const DRIVERS: Array[String] = ["vulkan", "d3d12", "opengl3"]
const MSAA: Array[String] = ["off", "2x", "4x", "8x"]
const SHADOW_QUALITY: Array[String] = ["off", "low", "medium", "high", "ultra"]
const TONEMAPS: Array[String] = ["linear", "reinhard", "filmic", "aces"]
const DEPTH_POLICIES: Array[String] = ["inherit_3d", "override_per_layer", "hybrid"]

var hardware_tier := "desktop"
var godot_version := "4.7.2-stable"
var available_contracts: Array[String] = ["render_core.v1", "lighting.v1", "performance.v1", "composition.v1", "feedback.v1"]
var required_contracts: Array[String] = ["render_core.v1", "lighting.v1", "performance.v1"]
var last_error := ""
var _pack: Dictionary = {}
var _presets: Dictionary = {}
var _by_tier: Dictionary = {}
var _last_resolution: Dictionary = {}


func configure(config := {}) -> bool:
	last_error = ""
	var next_hardware := String(config.get("hardware_tier", hardware_tier))
	var next_godot := String(config.get("godot_version", godot_version))
	var next_available = config.get("available_contracts", available_contracts)
	var next_required = config.get("required_contracts", required_contracts)
	if not HARDWARE_TIERS.has(next_hardware):
		last_error = "hardware_tier is invalid"
		return false
	if next_godot.strip_edges().is_empty():
		last_error = "godot_version is required"
		return false
	if not next_available is Array or not next_required is Array:
		last_error = "contract lists must be arrays"
		return false
	var available: Array[String] = []
	for value in next_available:
		available.append(String(value))
	var required: Array[String] = []
	for value in next_required:
		required.append(String(value))
	hardware_tier = next_hardware
	godot_version = next_godot
	available_contracts = available
	required_contracts = required
	return true


func load_pack(pack: Dictionary) -> bool:
	last_error = ""
	if String(pack.get("schema_version", "")) != PACK_SCHEMA:
		last_error = "pack schema_version must be " + PACK_SCHEMA
		return false
	if not _is_contract_id(String(pack.get("pack_id", ""))):
		last_error = "pack_id does not match the contract"
		return false
	var presets = pack.get("presets")
	if not presets is Array or presets.is_empty() or presets.size() > 16:
		last_error = "presets must contain 1..16 entries"
		return false
	var compatibility = pack.get("compatibility")
	if not compatibility is Dictionary:
		last_error = "compatibility is required"
		return false
	var compatibility_error := _validate_compatibility(compatibility)
	if not compatibility_error.is_empty():
		last_error = compatibility_error
		return false
	var next_presets: Dictionary = {}
	var next_by_tier: Dictionary = {}
	for preset in presets:
		if not preset is Dictionary:
			last_error = "preset must be an object"
			return false
		var preset_id := String(preset.get("preset_id", ""))
		if not _is_contract_id(preset_id):
			last_error = "preset_id does not match the contract"
			return false
		if next_presets.has(preset_id):
			last_error = "duplicate preset_id: " + preset_id
			return false
		var tier := String(preset.get("tier", ""))
		if not TIERS.has(tier):
			last_error = "invalid preset tier"
			return false
		if tier != "custom":
			if next_by_tier.has(tier):
				last_error = "duplicate standard tier: " + tier
				return false
			next_by_tier[tier] = preset_id
		var settings = preset.get("settings")
		if not settings is Dictionary:
			last_error = "preset settings are required"
			return false
		var settings_error := _validate_settings(settings)
		if not settings_error.is_empty():
			last_error = preset_id + ": " + settings_error
			return false
		next_presets[preset_id] = {
			"preset_id": preset_id,
			"label": String(preset.get("label", "")),
			"tier": tier,
			"settings": settings.duplicate(true),
		}
	var ladder_error := _validate_tier_ladder(next_by_tier, next_presets)
	if not ladder_error.is_empty():
		last_error = ladder_error
		return false
	_pack = {"pack_id": pack["pack_id"], "compatibility": compatibility.duplicate(true)}
	_presets = next_presets
	_by_tier = next_by_tier
	return true


func resolve_tier(tier: String, overrides := {}) -> Dictionary:
	if not _by_tier.has(tier):
		return _invalid("tier is not present in the pack: " + tier)
	return _resolve(_by_tier[tier], overrides)


func resolve_preset(preset_id: String, overrides := {}) -> Dictionary:
	if not _presets.has(preset_id):
		return _invalid("preset is not present in the pack: " + preset_id)
	return _resolve(preset_id, overrides)


func _resolve(preset_id: String, overrides) -> Dictionary:
	last_error = ""
	if _pack.is_empty():
		return _invalid("no preset pack is loaded")
	if not overrides is Dictionary:
		return _invalid("overrides must be an object")
	var compatibility_error := _check_compatibility()
	if not compatibility_error.is_empty():
		return _incompatible(compatibility_error)
	var preset: Dictionary = _presets[preset_id]
	var merged: Dictionary = preset["settings"].duplicate(true)
	var applied: Array[String] = []
	for block_name in overrides.keys():
		var block_key := String(block_name)
		if not BLOCKS.has(block_key):
			return _invalid("unknown settings block: " + block_key)
		var block_overrides = overrides[block_name]
		if not block_overrides is Dictionary:
			return _invalid("override block must be an object: " + block_key)
		if not merged.has(block_key):
			merged[block_key] = {}
		for key in block_overrides.keys():
			merged[block_key][String(key)] = block_overrides[key]
			applied.append(block_key + "." + String(key))
	var settings_error := _validate_settings(merged)
	if not settings_error.is_empty():
		return _invalid(settings_error)
	applied.sort()
	var resolution := {
		"schema_version": RESOLUTION_SCHEMA,
		"status": "RESOLVED",
		"pack_id": _pack["pack_id"],
		"preset_id": preset_id,
		"tier": preset["tier"],
		"settings": merged,
		"overrides_applied": applied,
		"compatibility": {
			"hardware_tier": hardware_tier,
			"godot_version": godot_version,
			"required_contracts": required_contracts.duplicate(),
			"pack_contract_versions": _pack["compatibility"]["contract_versions"].duplicate(),
		},
		"warnings": _warnings(preset["tier"], merged),
		"limitations": _limitations(),
	}
	_last_resolution = resolution
	return resolution


func _check_compatibility() -> String:
	var compatibility: Dictionary = _pack["compatibility"]
	var pack_hardware := String(compatibility["hardware_tier"])
	if HARDWARE_TIERS.find(pack_hardware) > HARDWARE_TIERS.find(hardware_tier):
		return "pack requires " + pack_hardware + " hardware"
	for contract in required_contracts:
		if not compatibility["contract_versions"].has(contract):
			return "pack does not declare required contract " + contract
		if not available_contracts.has(contract):
			return "environment does not provide required contract " + contract
	if not _matches_godot(String(compatibility["godot_version_range"])):
		return "pack Godot range does not match " + godot_version
	return ""


func _matches_godot(range_text: String) -> bool:
	var cleaned := godot_version.strip_edges().replace("-stable", "")
	var range_clean := range_text.strip_edges()
	if range_clean.ends_with(".x"):
		return cleaned.begins_with(range_clean.trim_suffix("x"))
	return cleaned == range_clean or cleaned.begins_with(range_clean + ".")


func _validate_tier_ladder(by_tier: Dictionary, presets: Dictionary) -> String:
	for index in range(STANDARD_TIERS.size() - 1):
		var lower := STANDARD_TIERS[index]
		var higher := STANDARD_TIERS[index + 1]
		if not by_tier.has(lower) or not by_tier.has(higher):
			continue
		var low_settings: Dictionary = presets[by_tier[lower]]["settings"]
		var high_settings: Dictionary = presets[by_tier[higher]]["settings"]
		var low_rendering: Dictionary = low_settings.get("rendering", {})
		var high_rendering: Dictionary = high_settings.get("rendering", {})
		if low_rendering.has("resolution_scale") and high_rendering.has("resolution_scale"):
			if float(high_rendering["resolution_scale"]) < float(low_rendering["resolution_scale"]):
				return higher + " resolution_scale is below " + lower
		if low_rendering.has("shadow_quality") and high_rendering.has("shadow_quality"):
			if SHADOW_RANK[high_rendering["shadow_quality"]] < SHADOW_RANK[low_rendering["shadow_quality"]]:
				return higher + " shadow_quality is below " + lower
		var low_lighting: Dictionary = low_settings.get("lighting", {})
		var high_lighting: Dictionary = high_settings.get("lighting", {})
		if low_lighting.has("shadow_atlas_size") and high_lighting.has("shadow_atlas_size"):
			if int(high_lighting["shadow_atlas_size"]) < int(low_lighting["shadow_atlas_size"]):
				return higher + " shadow_atlas_size is below " + lower
		var low_performance: Dictionary = low_settings.get("performance", {})
		var high_performance: Dictionary = high_settings.get("performance", {})
		if low_performance.has("target_fps") and high_performance.has("target_fps"):
			if int(high_performance["target_fps"]) < int(low_performance["target_fps"]):
				return higher + " target_fps is below " + lower
	return ""


func _validate_compatibility(compatibility: Dictionary) -> String:
	var versions = compatibility.get("contract_versions")
	if not versions is Array or versions.is_empty() or versions.size() > 16:
		return "compatibility.contract_versions must contain 1..16 entries"
	var seen: Array[String] = []
	for version in versions:
		var text := String(version)
		if not _is_contract_version(text):
			return "invalid contract version: " + text
		if seen.has(text):
			return "duplicate contract version: " + text
		seen.append(text)
	if not HARDWARE_TIERS.has(String(compatibility.get("hardware_tier", ""))):
		return "invalid compatibility.hardware_tier"
	if String(compatibility.get("godot_version_range", "")).strip_edges().is_empty():
		return "compatibility.godot_version_range is required"
	return ""


func _validate_settings(settings: Dictionary) -> String:
	if settings.is_empty():
		return "settings are empty"
	for block_name in settings.keys():
		if not BLOCKS.has(String(block_name)):
			return "unknown settings block: " + String(block_name)
	if settings.has("rendering"):
		var error := _validate_rendering(settings["rendering"])
		if not error.is_empty():
			return error
	if settings.has("lighting"):
		var error := _validate_lighting(settings["lighting"])
		if not error.is_empty():
			return error
	if settings.has("performance"):
		var error := _validate_performance(settings["performance"])
		if not error.is_empty():
			return error
	if settings.has("composition"):
		var error := _validate_composition(settings["composition"])
		if not error.is_empty():
			return error
	if settings.has("feedback"):
		var error := _validate_feedback(settings["feedback"])
		if not error.is_empty():
			return error
	if settings.has("accessibility"):
		var error := _validate_accessibility(settings["accessibility"])
		if not error.is_empty():
			return error
	return ""


func _validate_rendering(block) -> String:
	if not block is Dictionary:
		return "rendering must be an object"
	if not block.has("renderer_id") or String(block["renderer_id"]).is_empty():
		return "rendering.renderer_id is required"
	if not DRIVERS.has(String(block.get("driver_id", ""))):
		return "rendering.driver_id is invalid"
	if not _number_in_range(block.get("resolution_scale"), 0.25, 2.0):
		return "rendering.resolution_scale outside [0.25,2]"
	if not MSAA.has(String(block.get("msaa", ""))):
		return "rendering.msaa is invalid"
	if not SHADOW_QUALITY.has(String(block.get("shadow_quality", ""))):
		return "rendering.shadow_quality is invalid"
	return ""


func _validate_lighting(block) -> String:
	if not block is Dictionary:
		return "lighting must be an object"
	if not TONEMAPS.has(String(block.get("tonemap", ""))):
		return "lighting.tonemap is invalid"
	if not block.get("glow") is bool:
		return "lighting.glow must be boolean"
	if not _integer_in_range(block.get("shadow_atlas_size"), 256, 8192):
		return "lighting.shadow_atlas_size outside [256,8192]"
	if not _integer_in_range(block.get("max_shadowed_lights"), 0, 16):
		return "lighting.max_shadowed_lights outside [0,16]"
	return ""


func _validate_performance(block) -> String:
	if not block is Dictionary:
		return "performance must be an object"
	if not _integer_in_range(block.get("target_fps"), 30, 240):
		return "performance.target_fps outside [30,240]"
	if not _integer_in_range(block.get("max_draw_calls"), 0, 10000):
		return "performance.max_draw_calls outside [0,10000]"
	if not _number_in_range(block.get("lod_bias"), 0.0, 4.0):
		return "performance.lod_bias outside [0,4]"
	return ""


func _validate_composition(block) -> String:
	if not block is Dictionary:
		return "composition must be an object"
	if not DEPTH_POLICIES.has(String(block.get("depth_policy", ""))):
		return "composition.depth_policy is invalid"
	if not _number_in_range(block.get("parallax_scale"), 0.0, 2.0):
		return "composition.parallax_scale outside [0,2]"
	return ""


func _validate_feedback(block) -> String:
	if not block is Dictionary:
		return "feedback must be an object"
	if not _number_in_range(block.get("hit_stop_scale"), 0.0, 2.0):
		return "feedback.hit_stop_scale outside [0,2]"
	if not _number_in_range(block.get("shake_scale"), 0.0, 2.0):
		return "feedback.shake_scale outside [0,2]"
	if not block.get("reduced_motion") is bool:
		return "feedback.reduced_motion must be boolean"
	if block["reduced_motion"]:
		if float(block["shake_scale"]) > 0.5:
			return "reduced motion requires shake_scale <= 0.5"
		if float(block["hit_stop_scale"]) > 1.0:
			return "reduced motion requires hit_stop_scale <= 1.0"
	return ""


func _validate_accessibility(block) -> String:
	if not block is Dictionary:
		return "accessibility must be an object"
	if not _number_in_range(block.get("min_text_contrast_ratio"), 3.0, 21.0):
		return "accessibility.min_text_contrast_ratio outside [3,21]"
	if not _integer_in_range(block.get("focus_ring_px"), 1, 16):
		return "accessibility.focus_ring_px outside [1,16]"
	return ""


func _warnings(tier: String, settings: Dictionary) -> Array[String]:
	var warnings: Array[String] = []
	if tier == "custom":
		warnings.append("custom preset is not part of the standard tier ladder")
	if settings.has("feedback") and bool(settings["feedback"].get("reduced_motion", false)):
		warnings.append("reduced motion is enabled")
	return warnings


func _limitations() -> Array[String]:
	return [
		"planning only: no preset is applied to the engine, project.godot or a scene",
		"compatibility is checked against declared versions, not probed hardware",
		"settings are merged deterministically; visual quality is not validated",
		"tier monotonicity is enforced when the pack is loaded, not measured",
		"no FPS, frame-time or quality claim is produced",
		"no scene, engine or project.godot integration",
	]


func _invalid(reason: String) -> Dictionary:
	last_error = reason
	var resolution := {
		"schema_version": RESOLUTION_SCHEMA,
		"status": "INVALID",
		"pack_id": _pack.get("pack_id", ""),
		"preset_id": "",
		"tier": "",
		"settings": {},
		"overrides_applied": [],
		"compatibility": {},
		"warnings": [],
		"limitations": _limitations(),
		"reason": reason,
	}
	_last_resolution = resolution
	return resolution


func _incompatible(reason: String) -> Dictionary:
	last_error = reason
	var resolution := _invalid(reason)
	resolution["status"] = "INCOMPATIBLE"
	_last_resolution = resolution
	return resolution


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


func _is_contract_version(value: String) -> bool:
	var parts := value.split(".v")
	if parts.size() != 2 or parts[0].is_empty() or parts[1].is_empty():
		return false
	for character in parts[1]:
		if not "0123456789".contains(character):
			return false
	return true


func _number_in_range(value, minimum: float, maximum: float) -> bool:
	return (value is int or value is float) and not (value is bool) and is_finite(float(value)) and float(value) >= minimum and float(value) <= maximum


func _integer_in_range(value, minimum: int, maximum: int) -> bool:
	return _is_integer(value) and int(value) >= minimum and int(value) <= maximum


func _is_integer(value) -> bool:
	return value is int or (value is float and is_finite(value) and value == floor(value))


func list_presets() -> Array:
	var entries: Array = []
	for preset_id in _presets.keys():
		var preset: Dictionary = _presets[preset_id]
		entries.append({"preset_id": preset_id, "tier": preset["tier"], "label": preset["label"]})
	entries.sort_custom(func(a, b):
		var rank_a: int = TIERS.find(a["tier"])
		var rank_b: int = TIERS.find(b["tier"])
		if rank_a == rank_b:
			return String(a["preset_id"]) < String(b["preset_id"])
		return rank_a < rank_b
	)
	return entries


func get_last_resolution() -> Dictionary:
	return _last_resolution


func clear() -> void:
	_pack.clear()
	_presets.clear()
	_by_tier.clear()
	_last_resolution = {}
	last_error = ""
	hardware_tier = "desktop"
	godot_version = "4.7.2-stable"
	available_contracts = ["render_core.v1", "lighting.v1", "performance.v1", "composition.v1", "feedback.v1"]
	required_contracts = ["render_core.v1", "lighting.v1", "performance.v1"]
