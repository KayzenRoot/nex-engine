extends Node
class_name LightRigPlanner

# NEX-M03-S01 prototype: deterministic light-rig planner.
# Planning only: no light, shadow map, GI probe, shader or renderer is created.
# Vocabulary and limits follow the integrated lighting.v1 contract.

enum LightType { DIRECTIONAL, OMNI, SPOT }
enum AmbientSource { COLOR, SKY, DISABLED }
enum Tonemap { LINEAR, REINHARD, FILMIC, ACES }
enum GiMode { DISABLED, SDFGI, VOXELGI, LIGHTMAPGI }

const LIGHT_TYPE_NAMES: Array[String] = ["directional", "omni", "spot"]
const AMBIENT_SOURCE_NAMES: Array[String] = ["color", "sky", "disabled"]
const TONEMAP_NAMES: Array[String] = ["linear", "reinhard", "filmic", "aces"]
const GI_MODE_NAMES: Array[String] = ["disabled", "sdfgi", "voxelgi", "lightmapgi"]

const MAX_LIGHTS := 128
const MAX_SHADOWED_LIGHTS := 16
const MAX_CASCADES := 4
const MAX_ATLAS_SIZE := 8192
const MIN_ATLAS_SIZE := 256
const MAX_ENERGY := 16.0
const MAX_CULL_MASK := 1048575
const MAX_RANGE_M := 200.0
const MAX_SPOT_ANGLE_DEGREES := 90.0

@export var max_lights := MAX_LIGHTS
@export var max_shadowed_lights := 4
@export var max_cascades := 4
@export var atlas_size := 4096

var last_error := ""
var _lights: Dictionary = {}
var _environment: Dictionary = {}
var _last_plan: Dictionary = {}


func _init() -> void:
	_reset_environment()


func _reset_environment() -> void:
	_environment = {
		"ambient_source": AmbientSource.COLOR,
		"ambient_color": Color(0.05, 0.07, 0.1, 1.0),
		"ambient_energy": 0.6,
		"tonemap": Tonemap.FILMIC,
		"glow": true,
		"fog_enabled": false,
		"fog_density": 0.0,
		"fog_light_energy": 0.0,
		"gi_mode": GiMode.DISABLED,
		"gi_energy": 0.0,
	}


func configure(config := {}) -> bool:
	last_error = ""
	var next_lights := int(config.get("max_lights", max_lights))
	var next_shadowed := int(config.get("max_shadowed_lights", max_shadowed_lights))
	var next_cascades := int(config.get("max_cascades", max_cascades))
	var next_atlas := int(config.get("atlas_size", atlas_size))
	if next_lights < 1 or next_lights > MAX_LIGHTS:
		last_error = "max_lights outside [1,128]"
		return false
	if next_shadowed < 0 or next_shadowed > MAX_SHADOWED_LIGHTS:
		last_error = "max_shadowed_lights outside [0,16]"
		return false
	if next_cascades < 1 or next_cascades > MAX_CASCADES:
		last_error = "max_cascades outside [1,4]"
		return false
	if next_atlas < MIN_ATLAS_SIZE or next_atlas > MAX_ATLAS_SIZE:
		last_error = "atlas_size outside [256,8192]"
		return false
	max_lights = next_lights
	max_shadowed_lights = next_shadowed
	max_cascades = next_cascades
	atlas_size = next_atlas
	return true


func configure_environment(config := {}) -> bool:
	last_error = ""
	var next: Dictionary = _environment.duplicate()
	if config.has("ambient_source"):
		var source := int(config["ambient_source"])
		if source < AmbientSource.COLOR or source > AmbientSource.DISABLED:
			last_error = "invalid ambient source"
			return false
		next["ambient_source"] = source
	if config.has("ambient_color"):
		var color: Color = config["ambient_color"]
		if not _valid_color(color):
			last_error = "ambient color outside [0,1]"
			return false
		next["ambient_color"] = color
	if config.has("ambient_energy"):
		var energy := float(config["ambient_energy"])
		if not is_finite(energy) or energy < 0.0 or energy > 8.0:
			last_error = "ambient energy outside [0,8]"
			return false
		next["ambient_energy"] = energy
	if config.has("tonemap"):
		var tonemap := int(config["tonemap"])
		if tonemap < Tonemap.LINEAR or tonemap > Tonemap.ACES:
			last_error = "invalid tonemap"
			return false
		next["tonemap"] = tonemap
	if config.has("glow"):
		next["glow"] = bool(config["glow"])
	if config.has("fog_density"):
		var density := float(config["fog_density"])
		if not is_finite(density) or density < 0.0 or density > 1.0:
			last_error = "fog density outside [0,1]"
			return false
		next["fog_density"] = density
		next["fog_enabled"] = density > 0.0
	if config.has("fog_light_energy"):
		var fog_energy := float(config["fog_light_energy"])
		if not is_finite(fog_energy) or fog_energy < 0.0 or fog_energy > 8.0:
			last_error = "fog light energy outside [0,8]"
			return false
		next["fog_light_energy"] = fog_energy
	if config.has("gi_mode"):
		var gi_mode := int(config["gi_mode"])
		if gi_mode < GiMode.DISABLED or gi_mode > GiMode.LIGHTMAPGI:
			last_error = "invalid GI mode"
			return false
		next["gi_mode"] = gi_mode
	if config.has("gi_energy"):
		var gi_energy := float(config["gi_energy"])
		if not is_finite(gi_energy) or gi_energy < 0.0 or gi_energy > 4.0:
			last_error = "GI energy outside [0,4]"
			return false
		next["gi_energy"] = gi_energy
	_environment = next
	return true


func register_light(light_id: String, light_type: int, color: Color, energy: float,
		shadow_enabled: bool = false, shadow_bias: float = 0.05, shadow_softness: float = 0.0,
		cull_mask: int = 1, range_m: float = 0.0, spot_angle_degrees: float = 0.0,
		cascades: int = 0) -> bool:
	last_error = ""
	if light_id.is_empty():
		last_error = "light id is empty"
		return false
	if _lights.has(light_id):
		last_error = "duplicate light id: " + light_id
		return false
	if _lights.size() >= max_lights:
		last_error = "max_lights reached"
		return false
	if light_type < LightType.DIRECTIONAL or light_type > LightType.SPOT:
		last_error = "invalid light type"
		return false
	if not _valid_color(color):
		last_error = "light color outside [0,1]"
		return false
	if not is_finite(energy) or energy < 0.0 or energy > MAX_ENERGY:
		last_error = "light energy outside [0,16]"
		return false
	if not is_finite(shadow_bias) or shadow_bias < 0.0 or shadow_bias > 1.0:
		last_error = "shadow bias outside [0,1]"
		return false
	if not is_finite(shadow_softness) or shadow_softness < 0.0 or shadow_softness > 1.0:
		last_error = "shadow softness outside [0,1]"
		return false
	if cull_mask < 1 or cull_mask > MAX_CULL_MASK:
		last_error = "cull mask outside [1,1048575]"
		return false
	if shadow_enabled and energy == 0.0:
		last_error = "shadow caster requires energy > 0"
		return false
	if not _valid_type_fields(light_type, range_m, spot_angle_degrees, cascades):
		return false
	_lights[light_id] = {
		"light_type": light_type,
		"color": color,
		"energy": energy,
		"shadow_enabled": shadow_enabled,
		"shadow_bias": shadow_bias,
		"shadow_softness": shadow_softness,
		"cull_mask": cull_mask,
		"range_m": range_m,
		"spot_angle_degrees": spot_angle_degrees,
		"cascades": cascades,
	}
	return true


func _valid_type_fields(light_type: int, range_m: float, spot_angle_degrees: float, cascades: int) -> bool:
	if light_type == LightType.DIRECTIONAL:
		if range_m != 0.0 or spot_angle_degrees != 0.0:
			last_error = "directional light forbids range and spot angle"
			return false
		if cascades < 0 or cascades > MAX_CASCADES:
			last_error = "directional cascades outside [1,4]"
			return false
		return true
	if light_type == LightType.OMNI:
		if spot_angle_degrees != 0.0 or cascades != 0:
			last_error = "omni light forbids spot angle and cascades"
			return false
		return _valid_range(range_m)
	if cascades != 0:
		last_error = "spot light forbids cascades"
		return false
	if not _valid_range(range_m):
		return false
	if spot_angle_degrees != 0.0:
		if not is_finite(spot_angle_degrees) or spot_angle_degrees <= 0.0 or spot_angle_degrees > MAX_SPOT_ANGLE_DEGREES:
			last_error = "spot angle outside (0,90]"
			return false
	return true


func _valid_range(range_m: float) -> bool:
	if range_m == 0.0:
		return true
	if not is_finite(range_m) or range_m < 0.0 or range_m > MAX_RANGE_M:
		last_error = "range outside (0,200]"
		return false
	return true


func _valid_color(color: Color) -> bool:
	for component in [color.r, color.g, color.b, color.a]:
		if not is_finite(component) or component < 0.0 or component > 1.0:
			return false
	return true


func plan() -> Dictionary:
	var lights := _sorted_lights()
	var warnings: Array[String] = []
	if lights.is_empty():
		warnings.append("no_lights")
	if lights.size() > max_lights:
		warnings.append("light_budget_exceeded")
	var shadow_slots := _assign_shadow_slots(lights)
	if shadow_slots["demoted"] > 0:
		warnings.append("shadow_budget_exceeded")
	var effective_cascades := mini(max_cascades, MAX_CASCADES)
	var cascade_overflow := false
	for light in lights:
		if light["light_type"] == LightType.DIRECTIONAL and light["cascades"] > effective_cascades:
			cascade_overflow = true
	if cascade_overflow:
		warnings.append("directional_cascade_exceeded")
	var exported: Array = []
	for light in lights:
		exported.append(_export_light(light, shadow_slots["assigned"].get(light["light_id"], -1), effective_cascades))
	var plan := {
		"schema_version": "lighting.plan.v1",
		"environment": _export_environment(),
		"lights": exported,
		"shadow_budget": {
			"max_shadowed_lights": max_shadowed_lights,
			"directional_cascades": effective_cascades,
			"atlas_size": atlas_size,
		},
		"totals": {
			"lights": lights.size(),
			"directional_lights": _count_type(lights, LightType.DIRECTIONAL),
			"omni_lights": _count_type(lights, LightType.OMNI),
			"spot_lights": _count_type(lights, LightType.SPOT),
			"shadowed_lights": shadow_slots["assigned"].size(),
			"shadow_slots_used": shadow_slots["assigned"].size(),
			"estimated_shadow_maps": shadow_slots["maps"],
		},
		"warnings": warnings,
		"limitations": _limitations(),
	}
	_last_plan = plan
	return plan


func _sorted_lights() -> Array:
	var ids := _lights.keys()
	ids.sort()
	var result: Array = []
	for light_id in ids:
		var light: Dictionary = _lights[light_id].duplicate()
		light["light_id"] = light_id
		if light["light_type"] == LightType.DIRECTIONAL and light["cascades"] == 0:
			light["cascades"] = 1
		result.append(light)
	return result


func _assign_shadow_slots(lights: Array) -> Dictionary:
	var candidates: Array = []
	for light in lights:
		if light["shadow_enabled"]:
			candidates.append(light)
	candidates.sort_custom(func(a, b):
		if a["energy"] == b["energy"]:
			return a["light_id"] < b["light_id"]
		return a["energy"] > b["energy"]
	)
	var slots := mini(max_shadowed_lights, candidates.size())
	var assigned: Dictionary = {}
	var maps := 0
	for index in range(candidates.size()):
		if index >= slots:
			break
		var light: Dictionary = candidates[index]
		assigned[light["light_id"]] = index
		if light["light_type"] == LightType.DIRECTIONAL:
			maps += mini(light["cascades"], max_cascades)
		else:
			maps += 1
	return {"assigned": assigned, "maps": maps, "demoted": candidates.size() - slots}


func _export_light(light: Dictionary, shadow_slot: int, effective_cascades: int) -> Dictionary:
	var color: Color = light["color"]
	var exported := {
		"light_id": light["light_id"],
		"light_type": LIGHT_TYPE_NAMES[light["light_type"]],
		"color_rgba": [color.r, color.g, color.b, color.a],
		"energy": light["energy"],
		"shadow_enabled": light["shadow_enabled"],
		"shadow_assigned": shadow_slot >= 0,
		"shadow_slot": shadow_slot,
		"shadow_bias": light["shadow_bias"],
		"shadow_softness": light["shadow_softness"],
		"cull_mask": light["cull_mask"],
	}
	if light["light_type"] != LightType.DIRECTIONAL and light["range_m"] > 0.0:
		exported["range_m"] = light["range_m"]
	if light["light_type"] == LightType.SPOT and light["spot_angle_degrees"] > 0.0:
		exported["spot_angle_degrees"] = light["spot_angle_degrees"]
	if light["light_type"] == LightType.DIRECTIONAL:
		exported["cascades"] = mini(light["cascades"], effective_cascades)
	return exported


func _export_environment() -> Dictionary:
	var ambient: Color = _environment["ambient_color"]
	return {
		"ambient_source": AMBIENT_SOURCE_NAMES[_environment["ambient_source"]],
		"ambient_color_rgba": [ambient.r, ambient.g, ambient.b, ambient.a],
		"ambient_energy": _environment["ambient_energy"],
		"tonemap": TONEMAP_NAMES[_environment["tonemap"]],
		"glow": _environment["glow"],
		"fog": {
			"enabled": _environment["fog_enabled"],
			"density": _environment["fog_density"],
			"light_energy": _environment["fog_light_energy"],
		},
		"gi": {
			"mode": GI_MODE_NAMES[_environment["gi_mode"]],
			"energy": _environment["gi_energy"],
		},
	}


func _count_type(lights: Array, light_type: int) -> int:
	var count := 0
	for light in lights:
		if light["light_type"] == light_type:
			count += 1
	return count


func _limitations() -> Array[String]:
	return [
		"planning only: no light, shadow map, GI probe or renderer is created",
		"shadow slots are assigned by energy descending, ties by light id",
		"directional cascades are clamped to the configured budget in the plan",
		"estimated_shadow_maps is an arithmetic estimate, not a GPU measurement",
		"runtime cost and visual quality are INCONCLUSIVE_NOT_RUN",
		"no scene, engine or project.godot integration",
	]


func export_observation(observation_id: String, captured_at_utc: String, provenance: Dictionary) -> Dictionary:
	last_error = ""
	if observation_id.is_empty():
		last_error = "observation id is required"
		return {}
	if captured_at_utc.is_empty():
		last_error = "captured_at_utc is required"
		return {}
	if not _valid_provenance(provenance):
		return {}
	var generated := plan()
	var lights: Array = []
	for light in generated["lights"]:
		var entry := {
			"light_id": light["light_id"],
			"light_type": light["light_type"],
			"color_rgba": light["color_rgba"],
			"energy": light["energy"],
			"shadow_enabled": light["shadow_enabled"],
			"shadow_bias": light["shadow_bias"],
			"shadow_softness": light["shadow_softness"],
			"cull_mask": light["cull_mask"],
		}
		if light.has("range_m"):
			entry["range_m"] = light["range_m"]
		if light.has("spot_angle_degrees"):
			entry["spot_angle_degrees"] = light["spot_angle_degrees"]
		if light.has("cascades"):
			entry["cascades"] = light["cascades"]
		lights.append(entry)
	return {
		"schema_version": "lighting.v1",
		"observation_id": observation_id,
		"captured_at_utc": captured_at_utc,
		"environment": generated["environment"],
		"lights": lights,
		"shadow_budget": generated["shadow_budget"],
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


func _valid_provenance(provenance: Dictionary) -> bool:
	for key in ["base_sha", "head_sha", "godot_version", "hardware", "capture_mode", "measurement_status"]:
		if not provenance.has(key):
			last_error = "provenance missing " + key
			return false
	if not _is_sha(provenance["base_sha"]) or not _is_sha(provenance["head_sha"]):
		last_error = "provenance SHAs must be lowercase 40-hex"
		return false
	var hardware: Dictionary = provenance["hardware"]
	if not hardware.has("gpu_model") or not hardware.has("driver_version"):
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
	_lights.clear()
	_last_plan = {}
	last_error = ""
	_reset_environment()
