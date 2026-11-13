extends Node
class_name LightBudgetArbiter

# NEX-M03-LIGHTBUDGET prototype: deterministic lighting-budget arbiter.
# Projects GPU cost from the verified S05 Lighting Matrix coefficients and
# recommends an ordered degradation ladder. Analysis only: no rendering.

const REPORT_SCHEMA := "light_budget.report.v1"
const MODEL_ID := "nex_light_cost_model.v1"
const MODEL_SOURCE := "nex_bench S05 Lighting Matrix, RTX 5050, single session, GPU p95 at 25 proxies"
const MODEL_KEYS: Array[String] = [
	"base_gpu_ms",
	"per_omni_light_ms",
	"directional_shadow_ms",
	"per_omni_shadow_ms",
	"per_particle_emitter_ms",
	"shadow_vfx_interaction_ms",
]
const DEFAULT_MODEL := {
	"base_gpu_ms": 0.181,
	"per_omni_light_ms": 0.0245,
	"directional_shadow_ms": 0.100,
	"per_omni_shadow_ms": 0.02025,
	"per_particle_emitter_ms": 0.01375,
	"shadow_vfx_interaction_ms": 0.679,
}
const MAX_OMNI_LIGHTS := 128
const MAX_SHADOWED_OMNI_LIGHTS := 16
const MAX_PARTICLE_EMITTERS := 64
const TIGHT_HEADROOM_RATIO := 0.10

var budget_ms := 8.33
var last_error := ""
var _model: Dictionary = DEFAULT_MODEL.duplicate(true)
var _last_report: Dictionary = {}


func configure(config := {}) -> bool:
	last_error = ""
	var next_budget := float(config.get("budget_ms", budget_ms))
	if not is_finite(next_budget) or next_budget < 0.5 or next_budget > 1000.0:
		last_error = "budget_ms outside [0.5,1000]"
		return false
	var next_model: Dictionary = _model.duplicate(true)
	var overrides = config.get("model", {})
	if not overrides is Dictionary:
		last_error = "model must be an object"
		return false
	for key in overrides.keys():
		if not MODEL_KEYS.has(key):
			last_error = "unknown cost model key: " + str(key)
			return false
		var value := float(overrides[key])
		if not is_finite(value) or value < 0.0:
			last_error = "cost coefficient must be finite and nonnegative: " + str(key)
			return false
		next_model[key] = value
	budget_ms = next_budget
	_model = next_model
	return true


func estimate(scene: Dictionary) -> Dictionary:
	last_error = ""
	var scene_error := _validate_scene(scene)
	if not scene_error.is_empty():
		return _invalid(scene_error)
	var report := _build_report(scene)
	_last_report = report
	return report


func arbitrate(scene: Dictionary) -> Dictionary:
	last_error = ""
	var scene_error := _validate_scene(scene)
	if not scene_error.is_empty():
		return _invalid(scene_error)
	var report := _build_report(scene)
	var steps: Array = []
	var recommended := "none"
	var recommended_scene: Dictionary = scene.duplicate(true)
	if report["verdict"] != "FIT":
		for candidate in _candidates(scene):
			var projected := _project(candidate["scene"])
			var step := {
				"step_id": candidate["step_id"],
				"quality_cost": candidate["quality_cost"],
				"scene": candidate["scene"],
				"projected_gpu_ms": snappedf(projected["total_ms"], 0.001),
				"verdict": _verdict(projected["total_ms"]),
			}
			step["fits"] = step["verdict"] == "FIT"
			steps.append(step)
			if recommended == "none" and step["fits"]:
				recommended = candidate["step_id"]
				recommended_scene = candidate["scene"].duplicate(true)
	report["degradation_steps"] = steps
	report["recommended_step"] = recommended
	report["recommended_scene"] = recommended_scene
	_last_report = report
	return report


func _validate_scene(scene: Dictionary) -> String:
	for key in ["omni_lights", "shadowed_omni_lights", "directional_shadow", "particle_emitters"]:
		if not scene.has(key):
			return "scene missing " + key
	if not _is_integer(scene["omni_lights"]):
		return "omni_lights must be an integer"
	if not _is_integer(scene["shadowed_omni_lights"]):
		return "shadowed_omni_lights must be an integer"
	if not _is_integer(scene["particle_emitters"]):
		return "particle_emitters must be an integer"
	if not scene["directional_shadow"] is bool:
		return "directional_shadow must be boolean"
	var omni := int(scene["omni_lights"])
	var shadowed := int(scene["shadowed_omni_lights"])
	var particles := int(scene["particle_emitters"])
	if omni < 0 or omni > MAX_OMNI_LIGHTS:
		return "omni_lights outside [0,128]"
	if shadowed < 0 or shadowed > MAX_SHADOWED_OMNI_LIGHTS or shadowed > omni:
		return "shadowed_omni_lights outside [0,min(16,omni_lights)]"
	if particles < 0 or particles > MAX_PARTICLE_EMITTERS:
		return "particle_emitters outside [0,64]"
	return ""


func _is_integer(value) -> bool:
	return value is int or (value is float and is_finite(value) and value == floor(value))


func _project(scene: Dictionary) -> Dictionary:
	var omni := int(scene["omni_lights"])
	var shadowed := int(scene["shadowed_omni_lights"])
	var particles := int(scene["particle_emitters"])
	var directional := bool(scene["directional_shadow"])
	var base_ms := float(_model["base_gpu_ms"])
	var omni_ms := float(omni) * float(_model["per_omni_light_ms"])
	var directional_ms := float(_model["directional_shadow_ms"]) if directional else 0.0
	var omni_shadow_ms := float(shadowed) * float(_model["per_omni_shadow_ms"])
	var particle_ms := float(particles) * float(_model["per_particle_emitter_ms"])
	var interaction_ms := 0.0
	if directional and particles > 0:
		interaction_ms = float(_model["shadow_vfx_interaction_ms"])
	var total := base_ms + omni_ms + directional_ms + omni_shadow_ms + particle_ms + interaction_ms
	return {
		"base_ms": base_ms,
		"omni_lights_ms": snappedf(omni_ms, 0.001),
		"directional_shadow_ms": snappedf(directional_ms, 0.001),
		"omni_shadows_ms": snappedf(omni_shadow_ms, 0.001),
		"particles_ms": snappedf(particle_ms, 0.001),
		"interaction_ms": snappedf(interaction_ms, 0.001),
		"total_ms": total,
	}


func _build_report(scene: Dictionary) -> Dictionary:
	var breakdown := _project(scene)
	var total := float(breakdown["total_ms"])
	var headroom := budget_ms - total
	return {
		"schema_version": REPORT_SCHEMA,
		"model_id": MODEL_ID,
		"model_source": MODEL_SOURCE,
		"budget_ms": budget_ms,
		"scene": scene.duplicate(true),
		"breakdown": breakdown,
		"projected_gpu_ms": snappedf(total, 0.001),
		"headroom_ms": snappedf(headroom, 0.001),
		"verdict": _verdict(total),
		"limitations": _limitations(),
	}


func _verdict(total: float) -> String:
	if total > budget_ms:
		return "OVER_BUDGET"
	if budget_ms - total < budget_ms * TIGHT_HEADROOM_RATIO:
		return "TIGHT"
	return "FIT"


func _candidates(scene: Dictionary) -> Array:
	var candidates: Array = []
	var omni := int(scene["omni_lights"])
	var shadowed := int(scene["shadowed_omni_lights"])
	var particles := int(scene["particle_emitters"])
	if particles > 0:
		candidates.append(_candidate(scene, "halve_particle_emitters", "low", {"particle_emitters": particles / 2}))
	if bool(scene["directional_shadow"]):
		candidates.append(_candidate(scene, "disable_directional_shadow", "high", {"directional_shadow": false}))
	if shadowed > 0:
		candidates.append(_candidate(scene, "disable_omni_shadows", "medium", {"shadowed_omni_lights": 0}))
	if omni > 0:
		var next_omni := omni / 2
		candidates.append(_candidate(scene, "halve_omni_lights", "high", {
			"omni_lights": next_omni,
			"shadowed_omni_lights": mini(shadowed, next_omni),
		}))
	if omni > 0:
		candidates.append(_candidate(scene, "disable_omni_lights", "high", {
			"omni_lights": 0,
			"shadowed_omni_lights": 0,
		}))
	return candidates


func _candidate(scene: Dictionary, step_id: String, quality_cost: String, changes: Dictionary) -> Dictionary:
	var next: Dictionary = scene.duplicate(true)
	for key in changes.keys():
		next[key] = changes[key]
	return {"step_id": step_id, "quality_cost": quality_cost, "scene": next}


func _limitations() -> Array[String]:
	return [
		"projection only: coefficients come from one synthetic S05 session on an RTX 5050",
		"coefficients are GPU p95 deltas at 25 proxies, not frame time or FPS",
		"the interaction term is calibrated from a single combined preset capture",
		"coefficients do not generalize to other scenes, drivers, hardware or resolutions",
		"degradation steps are planning options, not quality-validated settings",
		"no new GPU capture, rendering or engine integration is performed",
	]


func _invalid(reason: String) -> Dictionary:
	last_error = reason
	var report := {
		"schema_version": REPORT_SCHEMA,
		"model_id": MODEL_ID,
		"model_source": MODEL_SOURCE,
		"budget_ms": budget_ms,
		"scene": {},
		"breakdown": {},
		"projected_gpu_ms": 0.0,
		"headroom_ms": 0.0,
		"verdict": "INVALID_INPUT",
		"limitations": _limitations(),
		"reason": reason,
		"degradation_steps": [],
		"recommended_step": "none",
		"recommended_scene": {},
	}
	_last_report = report
	return report


func get_last_report() -> Dictionary:
	return _last_report


func reset_model() -> void:
	_model = DEFAULT_MODEL.duplicate(true)


func clear() -> void:
	budget_ms = 8.33
	_model = DEFAULT_MODEL.duplicate(true)
	last_error = ""
	_last_report = {}
