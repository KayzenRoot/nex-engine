extends Node3D
class_name DepthCompositionSolver

# NEX-M02-S03 prototype: deterministic depth/composition planner.
# Primitives are mock world-space spheres with a radius; no rendering occurs.
# Passes: opaque/decal front-to-back, alpha back-to-front, overlay last.
# Hysteresis stabilizes near-equal depths across camera motion. Z-fight risk,
# alpha-over-critical and overlay-gameplay conflicts are reported, never hidden.
# This does not modify shaders, materials, M04 or the engine.

enum Kind { OPAQUE, ALPHA, OVERLAY, DECAL }

@export var depth_epsilon_m := 0.01
@export var hysteresis_m := 0.03
@export var max_primitives := 512

var last_error := ""
var _camera_position := Vector3.ZERO
var _camera_direction := Vector3(0.0, 0.0, -1.0)
var _projection := "perspective"
var _primitives: Dictionary = {}
var _last_opaque: Array = []
var _last_alpha: Array = []
var _last_plan: Dictionary = {}


func configure(config: Dictionary) -> bool:
	last_error = ""
	var next_projection := str(config.get("projection", _projection)).to_lower()
	if next_projection != "perspective" and next_projection != "orthographic":
		last_error = "projection must be perspective or orthographic"
		return false
	var next_epsilon := float(config.get("depth_epsilon_m", depth_epsilon_m))
	var next_hysteresis := float(config.get("hysteresis_m", hysteresis_m))
	var next_max := int(config.get("max_primitives", max_primitives))
	if not is_finite(next_epsilon) or next_epsilon < 0.0 or next_epsilon > 1.0:
		last_error = "depth_epsilon_m outside [0,1]"
		return false
	if not is_finite(next_hysteresis) or next_hysteresis < next_epsilon or next_hysteresis > 1.0:
		last_error = "hysteresis_m outside [epsilon,1]"
		return false
	if next_max < 1 or next_max > 4096:
		last_error = "max_primitives outside [1,4096]"
		return false
	_projection = next_projection
	depth_epsilon_m = next_epsilon
	hysteresis_m = next_hysteresis
	max_primitives = next_max
	return true


func set_camera(position: Vector3, direction: Vector3) -> bool:
	last_error = ""
	if direction.length() < 0.001:
		last_error = "camera direction is degenerate"
		return false
	_camera_position = position
	_camera_direction = direction.normalized()
	return true


func register_primitive(id: String, kind: Kind, position: Vector3, radius: float, gameplay_critical := false, overlay_blocks_gameplay := false) -> bool:
	last_error = ""
	if id.is_empty():
		last_error = "primitive id is empty"
		return false
	if _primitives.has(id):
		last_error = "duplicate primitive id: " + id
		return false
	if kind < Kind.OPAQUE or kind > Kind.DECAL:
		last_error = "invalid primitive kind"
		return false
	if not is_finite(radius) or radius < 0.0:
		last_error = "radius must be finite and nonnegative"
		return false
	if _primitives.size() >= max_primitives:
		last_error = "max_primitives reached"
		return false
	_primitives[id] = {
		"kind": kind, "position": position, "radius": radius,
		"gameplay_critical": gameplay_critical, "overlay_blocks_gameplay": overlay_blocks_gameplay,
	}
	return true


func clear_primitives() -> void:
	_primitives.clear()
	_last_opaque = []
	_last_alpha = []
	_last_plan = {}


func plan() -> Dictionary:
	var depths: Dictionary = {}
	var opaque: Array = []
	var alpha: Array = []
	var overlay: Array = []
	for id in _primitives.keys():
		var primitive: Dictionary = _primitives[id]
		var center: float = (primitive["position"] - _camera_position).dot(_camera_direction)
		depths[id] = {"center": center, "near": center - primitive["radius"], "far": center + primitive["radius"]}
		match int(primitive["kind"]):
			Kind.OPAQUE, Kind.DECAL:
				opaque.append(id)
			Kind.ALPHA:
				alpha.append(id)
			Kind.OVERLAY:
				overlay.append(id)
	opaque.sort_custom(func(a, b): return _less(a, b, depths, true))
	alpha.sort_custom(func(a, b): return _less(a, b, depths, false))
	overlay.sort()

	var previous_opaque := _last_opaque.duplicate()
	var previous_alpha := _last_alpha.duplicate()
	var stable_opaque := _stabilize(opaque, depths, previous_opaque)
	var stable_alpha := _stabilize(alpha, depths, previous_alpha)
	var order_stable := stable_opaque == previous_opaque and stable_alpha == previous_alpha
	_last_opaque = stable_opaque.duplicate()
	_last_alpha = stable_alpha.duplicate()

	var z_fights: Array = []
	for first in range(stable_opaque.size()):
		for second in range(first + 1, stable_opaque.size()):
			var a: String = stable_opaque[first]
			var b: String = stable_opaque[second]
			var da: Dictionary = depths[a]
			var db: Dictionary = depths[b]
			if da["near"] <= db["far"] and db["near"] <= da["far"] and absf(float(da["center"]) - float(db["center"])) <= depth_epsilon_m:
				z_fights.append({"a": a, "b": b, "delta": absf(float(da["center"]) - float(db["center"]))})

	var critical_ids: Array = []
	for id in _primitives.keys():
		if bool(_primitives[id]["gameplay_critical"]):
			critical_ids.append(id)
	var alpha_over: Array = []
	for alpha_id in stable_alpha:
		for critical_id in critical_ids:
			if float(depths[alpha_id]["center"]) < float(depths[critical_id]["center"]):
				alpha_over.append(alpha_id)
				break
	var overlay_conflicts: Array = []
	for overlay_id in overlay:
		if bool(_primitives[overlay_id]["overlay_blocks_gameplay"]) and not critical_ids.is_empty():
			overlay_conflicts.append(overlay_id)

	_last_plan = {
		"projection": _projection,
		"camera": {"position": _vector_array(_camera_position), "direction": _vector_array(_camera_direction)},
		"passes": {"opaque": stable_opaque, "alpha": stable_alpha, "overlay": overlay},
		"depths": depths,
		"z_fight_risks": z_fights,
		"alpha_over_critical": alpha_over,
		"overlay_gameplay_conflicts": overlay_conflicts,
		"order_stable": order_stable,
		"limitations": [
			"mock spheres, view-axis depth only; no rasterization",
			"alpha_over_critical is conservative depth-based, not pixel coverage",
			"edge pixels/aliasing cannot be evaluated without rendering",
			"orthographic and perspective share view-axis ordering in this prototype",
			"M08 2.5D composition contract is a draft, not an admitted implementation",
		],
	}
	return _last_plan.duplicate(true)


func get_plan() -> Dictionary:
	return _last_plan.duplicate(true)


func _less(a: String, b: String, depths: Dictionary, ascending: bool) -> bool:
	var da: float = depths[a]["center"]
	var db: float = depths[b]["center"]
	if is_equal_approx(da, db):
		return a < b
	return da < db if ascending else da > db


func _stabilize(ordered: Array, depths: Dictionary, previous: Array) -> Array:
	var result := ordered.duplicate()
	if previous.is_empty():
		return result
	var previous_index: Dictionary = {}
	for index in range(previous.size()):
		previous_index[previous[index]] = index
	for index in range(result.size() - 1):
		var a: String = result[index]
		var b: String = result[index + 1]
		if not previous_index.has(a) or not previous_index.has(b):
			continue
		if absf(float(depths[a]["center"]) - float(depths[b]["center"])) < hysteresis_m and int(previous_index[a]) > int(previous_index[b]):
			result[index] = b
			result[index + 1] = a
	return result


func _vector_array(value: Vector3) -> Array:
	return [value.x, value.y, value.z]
