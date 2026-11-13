extends Node
class_name CompositionPlanner

# NEX-M08-COMPOSITION prototype: deterministic 2.5D composition planner.
# Planning only: no layer, viewport, shader, scene or renderer is created.
# Vocabulary follows the integrated composition.v1 contract.

enum LayerRole { BACKGROUND, GAMEPLAY, FOREGROUND, HUD }
enum BlendMode { NORMAL, ADD, MULTIPLY, SCREEN }
enum DepthPolicy { INHERIT_3D, OVERRIDE_PER_LAYER, HYBRID }
enum ConflictPolicy { REPORT, BLOCK }

const ROLE_NAMES: Array[String] = ["background", "gameplay", "foreground", "hud"]
const BLEND_NAMES: Array[String] = ["normal", "add", "multiply", "screen"]
const DEPTH_POLICY_NAMES: Array[String] = ["inherit_3d", "override_per_layer", "hybrid"]
const CONFLICT_POLICY_NAMES: Array[String] = ["report", "block"]
const ENTITY_ROLE_NAMES: Array[String] = ["player", "threat", "objective"]
const ROLE_RANK: Array[int] = [0, 1, 2, 3]
const PARALLAX_BANDS := [[0.0, 0.8], [0.9, 1.1], [1.2, 2.0], [0.0, 0.0]]
const MAX_LAYERS := 32
const MAX_ENTITIES := 64

var max_layers := MAX_LAYERS
var max_alpha_over_gameplay := 0.5
var depth_policy := DepthPolicy.HYBRID
var critical_guard := true
var hud_layer_id := ""
var overlay_may_cover_gameplay := false
var conflict_policy := ConflictPolicy.REPORT
var last_error := ""
var _layers: Dictionary = {}
var _order: Array[String] = []
var _critical: Dictionary = {}
var _base_plan: Dictionary = {}
var _last_plan: Dictionary = {}


func _init() -> void:
	_reset_base_plan()


func _reset_base_plan() -> void:
	_base_plan = {
		"plan_schema": "none",
		"opaque_count": 0,
		"alpha_count": 0,
		"overlay_count": 0,
		"z_fight_risks": 0,
		"alpha_over_critical": 0,
		"overlay_gameplay_conflicts": 0,
	}


func configure(config := {}) -> bool:
	last_error = ""
	var next_layers := int(config.get("max_layers", max_layers))
	var next_alpha := float(config.get("max_alpha_over_gameplay", max_alpha_over_gameplay))
	if next_layers < 1 or next_layers > MAX_LAYERS:
		last_error = "max_layers outside [1,32]"
		return false
	if not is_finite(next_alpha) or next_alpha < 0.0 or next_alpha > 1.0:
		last_error = "max_alpha_over_gameplay outside [0,1]"
		return false
	max_layers = next_layers
	max_alpha_over_gameplay = next_alpha
	return true


func set_base_plan(plan: Dictionary) -> bool:
	last_error = ""
	var schema := String(plan.get("plan_schema", ""))
	if schema != "none" and schema != "depth_composition.plan.v1":
		last_error = "plan_schema is invalid"
		return false
	var next := {"plan_schema": schema}
	for key in ["opaque_count", "alpha_count", "overlay_count", "z_fight_risks", "alpha_over_critical", "overlay_gameplay_conflicts"]:
		if not plan.has(key) or not _is_integer(plan[key]):
			last_error = "base plan requires integer " + key
			return false
		var value := int(plan[key])
		if value < 0 or value > 1000000:
			last_error = key + " outside [0,1000000]"
			return false
		next[key] = value
	if schema == "none":
		for key in ["opaque_count", "alpha_count", "overlay_count", "z_fight_risks", "alpha_over_critical", "overlay_gameplay_conflicts"]:
			if int(next[key]) != 0:
				last_error = "plan_schema none requires zero counts"
				return false
	else:
		if not plan.has("plan_sha256") or not plan["plan_sha256"] is String or not _is_sha256(String(plan["plan_sha256"])):
			last_error = "real 3D plan requires a lowercase 64-hex digest"
			return false
		next["plan_sha256"] = String(plan["plan_sha256"])
	_base_plan = next
	return true


func set_policies(config := {}) -> bool:
	last_error = ""
	var next_depth := int(config.get("depth_policy", depth_policy))
	var next_policy := int(config.get("conflict_policy", conflict_policy))
	var next_guard := bool(config.get("critical_guard", critical_guard))
	var next_hud := String(config.get("hud_layer_id", hud_layer_id))
	var next_cover := bool(config.get("overlay_may_cover_gameplay", overlay_may_cover_gameplay))
	if next_depth < DepthPolicy.INHERIT_3D or next_depth > DepthPolicy.HYBRID:
		last_error = "invalid depth policy"
		return false
	if next_policy < ConflictPolicy.REPORT or next_policy > ConflictPolicy.BLOCK:
		last_error = "invalid conflict policy"
		return false
	if not next_hud.is_empty() and not _is_contract_id(next_hud):
		last_error = "hud_layer_id does not match the contract"
		return false
	depth_policy = next_depth
	conflict_policy = next_policy
	critical_guard = next_guard
	hud_layer_id = next_hud
	overlay_may_cover_gameplay = next_cover
	return true


func register_layer(layer_id: String, role: int, parallax: float, blend_mode: int, alpha: float,
		gameplay_critical := false, may_cover_gameplay := false, has_depth_override := false,
		depth_override_m := 0.0) -> bool:
	last_error = ""
	if not _is_contract_id(layer_id):
		last_error = "layer id does not match the contract"
		return false
	if _layers.has(layer_id):
		last_error = "duplicate layer id: " + layer_id
		return false
	if _layers.size() >= max_layers:
		last_error = "max_layers reached"
		return false
	if role < LayerRole.BACKGROUND or role > LayerRole.HUD:
		last_error = "invalid layer role"
		return false
	if blend_mode < BlendMode.NORMAL or blend_mode > BlendMode.SCREEN:
		last_error = "invalid blend mode"
		return false
	if not is_finite(parallax) or parallax < 0.0 or parallax > 4.0:
		last_error = "parallax outside [0,4]"
		return false
	if not is_finite(alpha) or alpha < 0.0 or alpha > 1.0:
		last_error = "alpha outside [0,1]"
		return false
	if has_depth_override and (not is_finite(depth_override_m) or depth_override_m < -1000.0 or depth_override_m > 1000.0):
		last_error = "depth_override_m outside [-1000,1000]"
		return false
	_layers[layer_id] = {
		"role": role, "parallax": parallax, "blend_mode": blend_mode, "alpha": alpha,
		"gameplay_critical": gameplay_critical, "may_cover_gameplay": may_cover_gameplay,
		"has_depth_override": has_depth_override, "depth_override_m": depth_override_m,
		"stack_index": _order.size(),
	}
	_order.append(layer_id)
	return true


func register_critical_entity(entity_id: String, role: int, must_remain_visible := true) -> bool:
	last_error = ""
	if not _is_contract_id(entity_id):
		last_error = "entity id does not match the contract"
		return false
	if _critical.has(entity_id):
		last_error = "duplicate entity id: " + entity_id
		return false
	if _critical.size() >= MAX_ENTITIES:
		last_error = "max critical entities reached"
		return false
	if role < 0 or role > 2:
		last_error = "invalid critical entity role"
		return false
	_critical[entity_id] = {"role": role, "must_remain_visible": must_remain_visible}
	return true


func plan() -> Dictionary:
	last_error = ""
	if _layers.is_empty():
		return _invalid("layer stack is empty")
	if _critical.is_empty():
		return _invalid("at least one critical entity is required")
	var ordered := _order.duplicate()
	ordered.sort_custom(func(a, b):
		var rank_a: int = ROLE_RANK[_layers[a]["role"]]
		var rank_b: int = ROLE_RANK[_layers[b]["role"]]
		if rank_a == rank_b:
			return int(_layers[a]["stack_index"]) < int(_layers[b]["stack_index"])
		return rank_a < rank_b
	)
	var conflicts: Array = []
	if ordered != _order:
		conflicts.append(_finding("stack_reordered", "info", "layers were grouped by role for draw order"))
	var has_visible_critical := false
	for entity_id in _critical.keys():
		if bool(_critical[entity_id]["must_remain_visible"]):
			has_visible_critical = true
	var hud_found := false
	for layer_id in ordered:
		var layer: Dictionary = _layers[layer_id]
		var role := int(layer["role"])
		if role == LayerRole.HUD:
			hud_found = true
			if bool(layer["has_depth_override"]):
				conflicts.append(_finding("hud_depth_override", "high", "hud layer declares a depth override", layer_id))
			if bool(layer["may_cover_gameplay"]) and has_visible_critical:
				var severity := "high" if conflict_policy == ConflictPolicy.BLOCK else "medium"
				conflicts.append(_finding("hud_covers_gameplay", severity, "hud may cover a visible critical entity", layer_id))
		if depth_policy == DepthPolicy.INHERIT_3D and bool(layer["has_depth_override"]):
			conflicts.append(_finding("depth_override_under_inherit", "high", "inherit_3d forbids layer depth overrides", layer_id))
		if depth_policy == DepthPolicy.OVERRIDE_PER_LAYER and role != LayerRole.HUD and not bool(layer["has_depth_override"]):
			conflicts.append(_finding("missing_depth_override", "medium", "override_per_layer requires a depth override", layer_id))
		var covers_gameplay := role == LayerRole.FOREGROUND or bool(layer["may_cover_gameplay"])
		if covers_gameplay and has_visible_critical and float(layer["alpha"]) > max_alpha_over_gameplay:
			conflicts.append(_finding("alpha_over_critical", "high", "layer alpha exceeds the critical guard limit", layer_id))
		var band: Array = PARALLAX_BANDS[role]
		if float(layer["parallax"]) < float(band[0]) or float(layer["parallax"]) > float(band[1]):
			conflicts.append(_finding("parallax_mismatch", "low", "parallax is outside the role band", layer_id))
		if bool(layer["gameplay_critical"]) and not has_visible_critical:
			conflicts.append(_finding("critical_layer_without_entity", "low", "gameplay-critical layer has no critical entity", layer_id))
	if not hud_found:
		conflicts.append(_finding("hud_layer_missing", "high", "no hud layer in the stack"))
	if not hud_layer_id.is_empty() and (not _layers.has(hud_layer_id) or int(_layers[hud_layer_id]["role"]) != LayerRole.HUD):
		conflicts.append(_finding("hud_reference_invalid", "high", "overlay_safety.hud_layer_id does not reference a hud layer"))
	if has_visible_critical and not critical_guard:
		conflicts.append(_finding("critical_guard_missing", "high", "critical entities require alpha_policy.critical_guard"))
	if int(_base_plan["z_fight_risks"]) > 0:
		conflicts.append(_finding("base_z_fight_risk", "medium", "base 3D plan reports z-fight risks"))
	if int(_base_plan["alpha_over_critical"]) > 0:
		conflicts.append(_finding("base_alpha_over_critical", "high", "base 3D plan reports alpha over critical"))
	if int(_base_plan["overlay_gameplay_conflicts"]) > 0:
		conflicts.append(_finding("base_overlay_gameplay_conflict", "high", "base 3D plan reports overlay/gameplay conflicts"))
	var exported_layers: Array = []
	for index in range(ordered.size()):
		var layer_id: String = ordered[index]
		var layer: Dictionary = _layers[layer_id]
		var role := int(layer["role"])
		var entry := {
			"layer_id": layer_id,
			"role": ROLE_NAMES[role],
			"stack_index": int(layer["stack_index"]),
			"draw_index": index,
			"parallax": layer["parallax"],
			"effective_parallax": 0.0 if role == LayerRole.HUD else layer["parallax"],
			"blend_mode": BLEND_NAMES[int(layer["blend_mode"])],
			"alpha": layer["alpha"],
			"depth_mode": "override" if bool(layer["has_depth_override"]) else "inherit_3d",
			"gameplay_critical": layer["gameplay_critical"],
			"may_cover_gameplay": layer["may_cover_gameplay"],
		}
		if bool(layer["has_depth_override"]) and role != LayerRole.HUD:
			entry["depth_override_m"] = layer["depth_override_m"]
		exported_layers.append(entry)
	var report := {
		"schema_version": "composition.plan.v1",
		"verdict": _verdict(conflicts),
		"base_3d_plan": _base_plan.duplicate(true),
		"policies": {
			"depth_policy": DEPTH_POLICY_NAMES[depth_policy],
			"critical_guard": critical_guard,
			"hud_layer_id": hud_layer_id,
			"overlay_may_cover_gameplay": overlay_may_cover_gameplay,
			"conflict_policy": CONFLICT_POLICY_NAMES[conflict_policy],
		},
		"layers": exported_layers,
		"critical_entities": _export_entities(),
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
	if generated["verdict"] == "INVALID_INPUT":
		return {}
	var stack: Array = []
	for layer in generated["layers"]:
		var entry := {
			"layer_id": layer["layer_id"],
			"role": layer["role"],
			"parallax": layer["parallax"],
			"blend_mode": layer["blend_mode"],
			"alpha": layer["alpha"],
			"gameplay_critical": layer["gameplay_critical"],
			"may_cover_gameplay": layer["may_cover_gameplay"],
		}
		if layer.has("depth_override_m"):
			entry["depth_override_m"] = layer["depth_override_m"]
		stack.append(entry)
	return {
		"schema_version": "composition.v1",
		"observation_id": observation_id,
		"captured_at_utc": captured_at_utc,
		"base_3d_plan": generated["base_3d_plan"],
		"layer_stack": stack,
		"depth_policy": generated["policies"]["depth_policy"],
		"alpha_policy": {
			"sort": "back_to_front",
			"critical_guard": generated["policies"]["critical_guard"],
			"max_alpha_over_gameplay": max_alpha_over_gameplay,
		},
		"overlay_safety": {
			"hud_layer_id": generated["policies"]["hud_layer_id"],
			"may_cover_gameplay": generated["policies"]["overlay_may_cover_gameplay"],
			"conflict_policy": generated["policies"]["conflict_policy"],
		},
		"critical_entities": generated["critical_entities"],
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


func _export_entities() -> Array:
	var entities: Array = []
	var ids := _critical.keys()
	ids.sort()
	for entity_id in ids:
		entities.append({
			"entity_id": entity_id,
			"role": ENTITY_ROLE_NAMES[int(_critical[entity_id]["role"])],
			"must_remain_visible": _critical[entity_id]["must_remain_visible"],
		})
	return entities


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


func _finding(code: String, severity: String, message: String, layer_id := "") -> Dictionary:
	var finding := {"code": code, "severity": severity, "message": message}
	if not layer_id.is_empty():
		finding["layer_id"] = layer_id
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
		"planning only: no layer, viewport, shader, scene or renderer is created",
		"alpha-over-critical is depth/alpha arithmetic, not pixel coverage",
		"parallax bands are planning heuristics, not camera measurements",
		"the planner groups layers by role for draw order; it does not reorder 3D primitives",
		"visual composition and runtime cost are INCONCLUSIVE_NOT_RUN",
		"no scene, engine or project.godot integration",
	]


func _invalid(reason: String) -> Dictionary:
	last_error = reason
	var report := {
		"schema_version": "composition.plan.v1",
		"verdict": "INVALID_INPUT",
		"base_3d_plan": _base_plan.duplicate(true),
		"policies": {},
		"layers": [],
		"critical_entities": [],
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


func _is_sha256(value: String) -> bool:
	if value.length() != 64:
		return false
	for character in value:
		if not "0123456789abcdef".contains(character):
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
	_layers.clear()
	_order.clear()
	_critical.clear()
	_last_plan = {}
	last_error = ""
	max_layers = MAX_LAYERS
	max_alpha_over_gameplay = 0.5
	depth_policy = DepthPolicy.HYBRID
	critical_guard = true
	hud_layer_id = ""
	overlay_may_cover_gameplay = false
	conflict_policy = ConflictPolicy.REPORT
	_reset_base_plan()
