extends Node
class_name ShadowStabilityAnalyzer

# NEX-M03-SHADOWSTAB prototype: deterministic shadow-stability risk analyzer.
# Analysis only: no shadow map, filter, light or renderer is created.
# Consumes lighting.plan.v1 (light-rig planner) or lighting.v1 observations.

const REPORT_SCHEMA := "shadow_stability.report.v1"
const PLAN_SCHEMA := "lighting.plan.v1"
const OBSERVATION_SCHEMA := "lighting.v1"
const LIGHT_TYPES: Array[String] = ["directional", "omni", "spot"]
const LIMITS := {
	"atlas_min": 256,
	"atlas_max": 8192,
	"max_shadowed_lights": 16,
	"max_cascades": 4,
	"low_bias": 0.02,
	"high_bias": 0.5,
	"softness": 0.6,
	"low_atlas": 2048,
	"min_spot_angle": 5.0,
}

var camera_near_m := 0.1
var camera_far_m := 500.0
var split_lambda := 0.75
var last_error := ""
var _last_report: Dictionary = {}


func configure(config := {}) -> bool:
	last_error = ""
	var next_near := float(config.get("camera_near_m", camera_near_m))
	var next_far := float(config.get("camera_far_m", camera_far_m))
	var next_lambda := float(config.get("split_lambda", split_lambda))
	if not is_finite(next_near) or next_near <= 0.0 or next_near > 10.0:
		last_error = "camera_near_m outside (0,10]"
		return false
	if not is_finite(next_far) or next_far <= next_near or next_far > 10000.0:
		last_error = "camera_far_m outside (near,10000]"
		return false
	if not is_finite(next_lambda) or next_lambda < 0.0 or next_lambda > 1.0:
		last_error = "split_lambda outside [0,1]"
		return false
	camera_near_m = next_near
	camera_far_m = next_far
	split_lambda = next_lambda
	return true


func analyze_plan(plan: Dictionary) -> Dictionary:
	last_error = ""
	if plan.get("schema_version", "") != PLAN_SCHEMA:
		return _inconclusive("plan schema_version must be " + PLAN_SCHEMA)
	var lights = plan.get("lights")
	var budget = plan.get("shadow_budget")
	if not lights is Array:
		return _inconclusive("plan lights must be an array")
	if not budget is Dictionary:
		return _inconclusive("plan shadow_budget must be an object")
	var budget_error := _validate_budget(budget)
	if not budget_error.is_empty():
		return _inconclusive(budget_error)
	return _analyze(lights, budget, true)


func analyze_observation(observation: Dictionary) -> Dictionary:
	last_error = ""
	if observation.get("schema_version", "") != OBSERVATION_SCHEMA:
		return _inconclusive("observation schema_version must be " + OBSERVATION_SCHEMA)
	var lights = observation.get("lights")
	var budget = observation.get("shadow_budget")
	if not lights is Array:
		return _inconclusive("observation lights must be an array")
	if not budget is Dictionary:
		return _inconclusive("observation shadow_budget must be an object")
	var budget_error := _validate_budget(budget)
	if not budget_error.is_empty():
		return _inconclusive(budget_error)
	return _analyze(lights, budget, false)


func _validate_budget(budget: Dictionary) -> String:
	for key in ["max_shadowed_lights", "directional_cascades", "atlas_size"]:
		if not budget.has(key):
			return "shadow_budget missing " + key
		if not _is_integer(budget[key]):
			return "shadow_budget." + key + " must be an integer"
	var max_shadowed := int(budget["max_shadowed_lights"])
	var cascades := int(budget["directional_cascades"])
	var atlas := int(budget["atlas_size"])
	if max_shadowed < 0 or max_shadowed > LIMITS["max_shadowed_lights"]:
		return "shadow_budget.max_shadowed_lights outside [0,16]"
	if cascades < 1 or cascades > LIMITS["max_cascades"]:
		return "shadow_budget.directional_cascades outside [1,4]"
	if atlas < LIMITS["atlas_min"] or atlas > LIMITS["atlas_max"]:
		return "shadow_budget.atlas_size outside [256,8192]"
	return ""


func _is_integer(value) -> bool:
	return value is int or (value is float and is_finite(value) and value == floor(value))


func _is_number(value) -> bool:
	return (value is int or value is float) and not (value is bool) and is_finite(float(value))


func _analyze(lights: Array, budget: Dictionary, has_assignment: bool) -> Dictionary:
	var findings: Array = []
	var shadowed := 0
	var directional_shadowed := 0
	var shadow_tiles := 0
	var min_bias := 1.0
	var max_bias := 0.0
	for index in range(lights.size()):
		var light = lights[index]
		if not light is Dictionary:
			return _inconclusive("lights[%d] must be an object" % index)
		var light_error := _validate_light(light, index)
		if not light_error.is_empty():
			return _inconclusive(light_error)
		var light_id: String = light["light_id"]
		if not light.get("shadow_enabled", false):
			continue
		shadowed += 1
		var bias := float(light.get("shadow_bias", 0.0))
		min_bias = minf(min_bias, bias)
		max_bias = maxf(max_bias, bias)
		if float(light.get("energy", 0.0)) <= 0.0:
			findings.append(_finding("shadow_caster_without_energy", "high", "shadow caster has no energy", light_id))
		if bias < LIMITS["low_bias"]:
			findings.append(_finding("low_bias_acne_risk", "medium", "shadow bias is below the heuristic floor", light_id))
		if bias > LIMITS["high_bias"]:
			findings.append(_finding("high_bias_peter_panning_risk", "medium", "shadow bias may detach contact shadows", light_id))
		if light["light_type"] == "directional":
			directional_shadowed += 1
			var cascades := int(light.get("cascades", 0))
			if cascades < 1:
				findings.append(_finding("directional_cascades_missing", "medium", "directional shadow has no cascades", light_id))
			elif cascades > int(budget["directional_cascades"]):
				findings.append(_finding("directional_cascades_exceed_budget", "high", "directional cascades exceed the budget", light_id))
			shadow_tiles += maxi(cascades, 1)
		else:
			shadow_tiles += 1
		if light["light_type"] == "spot" and light.has("spot_angle_degrees"):
			if float(light["spot_angle_degrees"]) <= LIMITS["min_spot_angle"]:
				findings.append(_finding("spot_angle_degenerate", "low", "very narrow spotlight may produce an unstable projection", light_id))
	if has_assignment:
		for index in range(lights.size()):
			var light: Dictionary = lights[index]
			if not light.get("shadow_assigned", false) and light.get("shadow_enabled", false):
				findings.append(_finding("caster_without_shadow_slot", "high", "shadow caster was demoted by the planner", light["light_id"]))
			if light.get("shadow_enabled", false) and not light.has("shadow_assigned"):
				findings.append(_finding("shadow_assignment_missing", "medium", "plan light lacks shadow_assigned", light["light_id"]))
	if shadowed == 0:
		findings.append(_finding("no_shadow_workload", "info", "no shadow caster in the input"))
	elif shadowed > int(budget["max_shadowed_lights"]):
		findings.append(_finding("shadow_budget_exceeded", "high", "shadowed lights exceed max_shadowed_lights"))
	if shadowed > 0 and int(budget["max_shadowed_lights"]) == 0:
		findings.append(_finding("shadow_budget_zero", "high", "shadow casters exist with a zero shadow budget"))
	var atlas := int(budget["atlas_size"])
	for light in lights:
		if light.get("shadow_enabled", false) and float(light.get("shadow_softness", 0.0)) > LIMITS["softness"] and atlas < LIMITS["low_atlas"]:
			findings.append(_finding("soft_shadow_low_atlas", "low", "soft shadows with a small atlas may band", light["light_id"]))
	var tile_budget := int(atlas / 256)
	var pressure_ratio := 0.0
	if tile_budget > 0:
		pressure_ratio = float(shadow_tiles) / float(tile_budget)
	if pressure_ratio > 1.0:
		findings.append(_finding("atlas_pressure", "medium", "estimated shadow tiles exceed the atlas tile budget"))
	var report := {
		"schema_version": REPORT_SCHEMA,
		"verdict": _verdict(findings),
		"source_schema": PLAN_SCHEMA if has_assignment else OBSERVATION_SCHEMA,
		"camera": {
			"near_m": camera_near_m,
			"far_m": camera_far_m,
			"split_lambda": split_lambda,
		},
		"cascade_splits_m": _cascade_splits(int(budget["directional_cascades"])),
		"metrics": {
			"shadowed_lights": shadowed,
			"directional_shadowed_lights": directional_shadowed,
			"shadow_tiles_estimate": shadow_tiles,
			"atlas_tile_budget": tile_budget,
			"atlas_pressure_ratio": snappedf(pressure_ratio, 0.001),
			"min_shadow_bias": snappedf(min_bias, 0.001) if shadowed > 0 else 0.0,
			"max_shadow_bias": snappedf(max_bias, 0.001),
		},
		"findings": _sorted_findings(findings),
		"summary": _summary(findings),
		"limitations": _limitations(),
	}
	_last_report = report
	return report


func _validate_light(light: Dictionary, index: int) -> String:
	if not light.has("light_id") or not light["light_id"] is String or String(light["light_id"]).is_empty():
		return "lights[%d] requires a light_id" % index
	if not light.has("light_type") or not LIGHT_TYPES.has(String(light["light_type"])):
		return "lights[%d] has an invalid light_type" % index
	for key in ["energy", "shadow_bias", "shadow_softness"]:
		if light.has(key) and not _is_number(light[key]):
			return "lights[%d].%s must be a finite number" % [index, key]
	if light.has("shadow_enabled") and not (light["shadow_enabled"] is bool):
		return "lights[%d].shadow_enabled must be boolean" % index
	if light.has("cascades") and not _is_integer(light["cascades"]):
		return "lights[%d].cascades must be an integer" % index
	return ""


func _finding(code: String, severity: String, message: String, light_id := "") -> Dictionary:
	var finding := {"code": code, "severity": severity, "message": message}
	if not light_id.is_empty():
		finding["light_id"] = light_id
	return finding


func _verdict(findings: Array) -> String:
	for finding in findings:
		if finding["severity"] == "high" or finding["severity"] == "medium":
			return "RISK_REPRODUCED"
	for finding in findings:
		if finding["severity"] == "low" or finding["severity"] == "info":
			return "STABLE_CONFIG_HEURISTIC_WITH_NOTES"
	return "STABLE_CONFIG_HEURISTIC"


func _summary(findings: Array) -> Dictionary:
	var summary := {"high": 0, "medium": 0, "low": 0, "info": 0}
	for finding in findings:
		summary[finding["severity"]] += 1
	return summary


func _sorted_findings(findings: Array) -> Array:
	var order := {"high": 0, "medium": 1, "low": 2, "info": 3}
	findings.sort_custom(func(a, b):
		if order[a["severity"]] == order[b["severity"]]:
			return String(a["code"]) < String(b["code"])
		return order[a["severity"]] < order[b["severity"]]
	)
	return findings


func _cascade_splits(cascades: int) -> Array:
	var splits: Array = [snappedf(camera_near_m, 0.001)]
	for index in range(1, cascades + 1):
		var ratio := float(index) / float(cascades)
		var log_split := camera_near_m * pow(camera_far_m / camera_near_m, ratio)
		var uniform_split := camera_near_m + (camera_far_m - camera_near_m) * ratio
		var split := split_lambda * log_split + (1.0 - split_lambda) * uniform_split
		splits.append(snappedf(split, 0.001))
	return splits


func _limitations() -> Array[String]:
	return [
		"heuristic analysis only: no shadow map is rendered or sampled",
		"thresholds are planning heuristics, not measured acne or peter-panning",
		"cascade splits use a practical split scheme with the configured lambda",
		"atlas pressure is an arithmetic tile estimate, not allocator behavior",
		"visual stability and runtime cost are INCONCLUSIVE_NOT_RUN",
		"no scene, engine or project.godot integration",
	]


func _inconclusive(reason: String) -> Dictionary:
	last_error = reason
	var report := {
		"schema_version": REPORT_SCHEMA,
		"verdict": "INCONCLUSIVE",
		"source_schema": "",
		"camera": {
			"near_m": camera_near_m,
			"far_m": camera_far_m,
			"split_lambda": split_lambda,
		},
		"cascade_splits_m": [],
		"metrics": {},
		"findings": [],
		"summary": {"high": 0, "medium": 0, "low": 0, "info": 0},
		"limitations": _limitations(),
		"reason": reason,
	}
	_last_report = report
	return report


func get_last_report() -> Dictionary:
	return _last_report


func clear() -> void:
	camera_near_m = 0.1
	camera_far_m = 500.0
	split_lambda = 0.75
	last_error = ""
	_last_report = {}
