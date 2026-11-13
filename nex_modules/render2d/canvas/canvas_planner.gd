extends Node
class_name CanvasPlanner

# NEX-M07-S01 prototype: deterministic 2D canvas/batching planner.
# Planning only: no rendering, shaders, materials, lights or particles are created.
# The plan follows the integrated render2d.v1 contract vocabulary.

enum BlendMode { MIX, ADD, SUB, MUL, PREMUL_ALPHA }
enum LightingMode { UNSHADED, CANVAS_LIGHT }

@export var max_layers := 4096
@export var max_draw_calls := 1024
@export var max_lights := 8

var last_error := ""
var _layers: Dictionary = {}
var _materials: Dictionary = {}
var _lights: Dictionary = {}
var _particles: Dictionary = {}
var _last_plan: Dictionary = {}


func configure(config := {}) -> bool:
	last_error = ""
	var next_layers := int(config.get("max_layers", max_layers))
	var next_draw_calls := int(config.get("max_draw_calls", max_draw_calls))
	var next_lights := int(config.get("max_lights", max_lights))
	if next_layers < 1 or next_layers > 16384:
		last_error = "max_layers outside [1,16384]"
		return false
	if next_draw_calls < 1 or next_draw_calls > 10000:
		last_error = "max_draw_calls outside [1,10000]"
		return false
	if next_lights < 0 or next_lights > 64:
		last_error = "max_lights outside [0,64]"
		return false
	max_layers = next_layers
	max_draw_calls = next_draw_calls
	max_lights = next_lights
	return true


func register_material(id: String, shader_id: String, lighting_mode: LightingMode) -> bool:
	last_error = ""
	if id.is_empty() or shader_id.is_empty():
		last_error = "material id and shader id are required"
		return false
	if _materials.has(id):
		last_error = "duplicate material id: " + id
		return false
	if lighting_mode < LightingMode.UNSHADED or lighting_mode > LightingMode.CANVAS_LIGHT:
		last_error = "invalid lighting mode"
		return false
	_materials[id] = {"shader_id": shader_id, "lighting_mode": lighting_mode}
	return true


func register_layer(id: String, z_index: int, blend_mode: BlendMode, material_id: String,
		position := Vector2.ZERO, scale := Vector2.ONE, rotation_deg := 0.0, visible := true) -> bool:
	last_error = ""
	if id.is_empty():
		last_error = "layer id is empty"
		return false
	if _layers.has(id):
		last_error = "duplicate layer id: " + id
		return false
	if not _materials.has(material_id):
		last_error = "layer references an unknown material: " + material_id
		return false
	if blend_mode < BlendMode.MIX or blend_mode > BlendMode.PREMUL_ALPHA:
		last_error = "invalid blend mode"
		return false
	if z_index < -4096 or z_index > 4096:
		last_error = "z_index outside [-4096,4096]"
		return false
	if not _finite_vector(position) or not _finite_vector(scale) or not is_finite(rotation_deg):
		last_error = "layer transform must be finite"
		return false
	if scale.x <= 0.0 or scale.y <= 0.0:
		last_error = "layer scale must be positive"
		return false
	if _layers.size() >= max_layers:
		last_error = "max_layers reached"
		return false
	_layers[id] = {
		"z_index": z_index, "blend_mode": blend_mode, "material_id": material_id,
		"position": position, "scale": scale, "rotation_deg": rotation_deg, "visible": visible,
	}
	return true


func register_light(id: String, light_type: int, energy: float) -> bool:
	last_error = ""
	if id.is_empty():
		last_error = "light id is empty"
		return false
	if _lights.has(id):
		last_error = "duplicate light id: " + id
		return false
	if light_type < 0 or light_type > 1:
		last_error = "invalid light type"
		return false
	if not is_finite(energy) or energy < 0.0 or energy > 100.0:
		last_error = "light energy outside [0,100]"
		return false
	_lights[id] = {"light_type": light_type, "energy": energy}
	return true


func register_particle(emitter_id: String, amount: int, emitting: bool) -> bool:
	last_error = ""
	if emitter_id.is_empty():
		last_error = "emitter id is empty"
		return false
	if _particles.has(emitter_id):
		last_error = "duplicate emitter id: " + emitter_id
		return false
	if amount < 0 or amount > 100000:
		last_error = "particle amount outside [0,100000]"
		return false
	if emitting and amount < 1:
		last_error = "an emitting emitter requires amount >= 1"
		return false
	_particles[emitter_id] = {"amount": amount, "emitting": emitting}
	return true


func clear() -> void:
	_layers.clear()
	_materials.clear()
	_lights.clear()
	_particles.clear()
	_last_plan = {}


func plan() -> Dictionary:
	var visible_ids: Array = []
	for id in _layers.keys():
		if bool(_layers[id]["visible"]):
			visible_ids.append(id)
	visible_ids.sort_custom(func(a, b): return _layer_less(a, b))
	var batches: Array = []
	var layers_plan: Array = []
	for id in visible_ids:
		var layer: Dictionary = _layers[id]
		var batch_index: int = batches.size() - 1
		if batches.is_empty() or not _same_batch(batches[batches.size() - 1], layer):
			batches.append({"material_id": layer["material_id"], "blend_mode": layer["blend_mode"], "layer_ids": []})
			batch_index = batches.size() - 1
		batches[batch_index]["layer_ids"].append(id)
		layers_plan.append({
			"id": id, "z_index": int(layer["z_index"]), "blend_mode": int(layer["blend_mode"]),
			"material_id": layer["material_id"], "batch_index": batch_index,
			"position": [layer["position"].x, layer["position"].y],
			"scale": [layer["scale"].x, layer["scale"].y],
			"rotation_deg": layer["rotation_deg"], "visible": true,
		})
	var emitting_particles := 0
	var particles_plan: Array = []
	for emitter_id in _particles.keys():
		var particle: Dictionary = _particles[emitter_id]
		var draw_calls := 1 if bool(particle["emitting"]) else 0
		emitting_particles += draw_calls
		particles_plan.append({"emitter_id": emitter_id, "amount": int(particle["amount"]),
							   "emitting": bool(particle["emitting"]), "draw_calls": draw_calls})
	var batch_groups := batches.size()
	var draw_calls := batch_groups + emitting_particles
	var warnings: Array = []
	if draw_calls > max_draw_calls:
		warnings.append("draw_call_budget_exceeded")
	if _lights.size() > max_lights:
		warnings.append("light_budget_exceeded")
	if _lighting_without_lights(visible_ids):
		warnings.append("lighting_without_lights")
	_last_plan = {
		"layers": layers_plan,
		"batches": batches,
		"lights": _lights.keys(),
		"particles": particles_plan,
		"totals": {
			"visible_layers": layers_plan.size(),
			"batches": batch_groups,
			"batch_groups": batch_groups,
			"draw_calls": draw_calls,
			"state_changes": maxi(0, batch_groups - 1),
			"lights": _lights.size(),
			"emitting_particles": emitting_particles,
		},
		"warnings": warnings,
		"limitations": [
			"planning only; no rendering, material, light or particle is created",
			"draw calls are an estimate from deterministic batches, not GPU-measured",
			"performance/frame-time/VRAM is INCONCLUSIVE_NOT_RUN",
			"shader/material implementation belongs to M04/M05/M08 and was not touched",
			"contract render2d.v1 vocabulary is mirrored, not redefined",
		],
	}
	return _last_plan.duplicate(true)


func get_plan() -> Dictionary:
	return _last_plan.duplicate(true)


func _layer_less(a: String, b: String) -> bool:
	var za: int = int(_layers[a]["z_index"])
	var zb: int = int(_layers[b]["z_index"])
	if za == zb:
		return a < b
	return za < zb


func _same_batch(batch: Dictionary, layer: Dictionary) -> bool:
	return str(batch["material_id"]) == str(layer["material_id"]) and int(batch["blend_mode"]) == int(layer["blend_mode"])


func _lighting_without_lights(visible_ids: Array) -> bool:
	if not _lights.is_empty():
		return false
	for id in visible_ids:
		var material_id: String = _layers[id]["material_id"]
		if int(_materials[material_id]["lighting_mode"]) == LightingMode.CANVAS_LIGHT:
			return true
	return false


func _finite_vector(value: Vector2) -> bool:
	return is_finite(value.x) and is_finite(value.y)
