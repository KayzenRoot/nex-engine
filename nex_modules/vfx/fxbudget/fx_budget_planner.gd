extends Node
class_name FXBudgetPlanner

# NEX-M05-FXBUDGET prototype: deterministic spell-FX budget planner.
# Planning only: no particle, emitter, light, decal or renderer is created.
# Vocabulary follows the integrated spellfx.v1 contract.

const REPORT_SCHEMA := "fx_budget.report.v1"
const ELEMENTS: Array[String] = ["fire", "ice", "lightning", "arcane", "nature", "physical"]
const PHASES: Array[String] = ["cast", "travel", "impact", "linger"]
const KINDS: Array[String] = ["particles", "trail", "beam", "decal", "light"]
const MAX_EMITTERS := 256
const MAX_PARTICLES := 1000000
const MAX_GPU_EMITTERS := 64
const MAX_DECALS := 256
const TIGHT_RATIO := 0.90

var max_emitters := 64
var max_particles := 20000
var max_gpu_emitters := 16
var max_decals := 64
var last_error := ""
var _last_report: Dictionary = {}


func configure(config := {}) -> bool:
	last_error = ""
	var next_emitters := int(config.get("max_emitters", max_emitters))
	var next_particles := int(config.get("max_particles", max_particles))
	var next_gpu := int(config.get("max_gpu_emitters", max_gpu_emitters))
	var next_decals := int(config.get("max_decals", max_decals))
	if next_emitters < 0 or next_emitters > MAX_EMITTERS:
		last_error = "max_emitters outside [0,256]"
		return false
	if next_particles < 0 or next_particles > MAX_PARTICLES:
		last_error = "max_particles outside [0,1000000]"
		return false
	if next_gpu < 0 or next_gpu > MAX_GPU_EMITTERS:
		last_error = "max_gpu_emitters outside [0,64]"
		return false
	if next_decals < 0 or next_decals > MAX_DECALS:
		last_error = "max_decals outside [0,256]"
		return false
	max_emitters = next_emitters
	max_particles = next_particles
	max_gpu_emitters = next_gpu
	max_decals = next_decals
	return true


func analyze(spells: Array) -> Dictionary:
	last_error = ""
	var validation := _validate(spells)
	if not validation.is_empty():
		return _invalid(validation)
	var totals := {"spells": spells.size(), "emitters": 0, "particles": 0, "gpu_emitters": 0, "decals": 0, "light_bridges": 0, "duration_ms": 0}
	var per_spell: Array = []
	var particle_entries: Array = []
	var gpu_entries: Array = []
	for spell in spells:
		var spell_totals := {"emitters": 0, "particles": 0, "gpu_emitters": 0, "decals": 0, "duration_ms": 0}
		for phase in spell["phases"]:
			spell_totals["duration_ms"] += int(phase["duration_ms"])
			for emitter in phase["emitters"]:
				var amount := int(emitter["amount"])
				spell_totals["emitters"] += 1
				spell_totals["particles"] += amount
				if bool(emitter["gpu"]):
					spell_totals["gpu_emitters"] += 1
					gpu_entries.append({"spell_id": spell["spell_id"], "emitter_id": emitter["emitter_id"], "amount": amount})
				if emitter["kind"] == "decal":
					spell_totals["decals"] += 1
				if bool(emitter["light_bridge"]):
					totals["light_bridges"] += 1
				if emitter["kind"] in ["particles", "trail", "beam"]:
					particle_entries.append({"spell_id": spell["spell_id"], "emitter_id": emitter["emitter_id"], "amount": amount})
		per_spell.append({
			"spell_id": spell["spell_id"],
			"element": spell["element"],
			"phases": spell["phases"].size(),
			"emitters": spell_totals["emitters"],
			"particles": spell_totals["particles"],
			"gpu_emitters": spell_totals["gpu_emitters"],
			"decals": spell_totals["decals"],
			"duration_ms": spell_totals["duration_ms"],
		})
		for key in ["emitters", "particles", "gpu_emitters", "decals", "duration_ms"]:
			totals[key] += spell_totals[key]
	per_spell.sort_custom(func(a, b): return String(a["spell_id"]) < String(b["spell_id"]))
	var findings: Array = []
	if totals["emitters"] > max_emitters:
		findings.append(_finding("over_emitters", "high", "emitter count exceeds the budget"))
	elif _tight(totals["emitters"], max_emitters):
		findings.append(_finding("tight_emitters", "medium", "emitter count is close to the budget"))
	if totals["particles"] > max_particles:
		findings.append(_finding("over_particles", "high", "particle amount exceeds the budget"))
	elif _tight(totals["particles"], max_particles):
		findings.append(_finding("tight_particles", "medium", "particle amount is close to the budget"))
	if totals["gpu_emitters"] > max_gpu_emitters:
		findings.append(_finding("over_gpu_emitters", "high", "GPU emitter count exceeds the budget"))
	elif _tight(totals["gpu_emitters"], max_gpu_emitters):
		findings.append(_finding("tight_gpu_emitters", "medium", "GPU emitter count is close to the budget"))
	if totals["decals"] > max_decals:
		findings.append(_finding("over_decals", "high", "decal count exceeds the budget"))
	elif _tight(totals["decals"], max_decals):
		findings.append(_finding("tight_decals", "medium", "decal count is close to the budget"))
	var particles_plan := _reduce_particles(particle_entries, max_particles)
	var gpu_plan := _reduce_gpu(gpu_entries, max_gpu_emitters)
	var verdict := _verdict(totals)
	var report := {
		"schema_version": REPORT_SCHEMA,
		"verdict": verdict,
		"totals": totals,
		"budget": {
			"max_emitters": max_emitters,
			"max_particles": max_particles,
			"max_gpu_emitters": max_gpu_emitters,
			"max_decals": max_decals,
		},
		"per_spell": per_spell,
		"reduction_plan": {
			"particles": particles_plan,
			"gpu_emitters": gpu_plan,
		},
		"findings": _sorted_findings(findings),
		"recommendations": _recommendations(totals),
		"limitations": _limitations(),
	}
	_last_report = report
	return report


func _validate(spells: Array) -> String:
	for index in range(spells.size()):
		var spell = spells[index]
		if not spell is Dictionary:
			return "spells[%d] must be an object" % index
		if not spell.has("spell_id") or not spell["spell_id"] is String or not _is_contract_id(String(spell["spell_id"])):
			return "spells[%d].spell_id does not match spellfx.v1" % index
		if not spell.has("element") or not ELEMENTS.has(String(spell["element"])):
			return "spells[%d].element is invalid" % index
		if not spell.has("phases") or not spell["phases"] is Array:
			return "spells[%d] requires phases" % index
		var phase_names: Array[String] = []
		var emitter_ids: Array[String] = []
		var total_duration := 0
		for phase_index in range(spell["phases"].size()):
			var phase = spell["phases"][phase_index]
			if not phase is Dictionary:
				return "spells[%d].phases[%d] must be an object" % [index, phase_index]
			var phase_name := String(phase.get("phase", ""))
			if not PHASES.has(phase_name):
				return "spells[%d].phases[%d].phase is invalid" % [index, phase_index]
			if phase_names.has(phase_name):
				return "spells[%d]: duplicate phase %s" % [index, phase_name]
			phase_names.append(phase_name)
			if not phase.has("duration_ms") or not _is_integer(phase["duration_ms"]):
				return "spells[%d].phases[%d].duration_ms must be an integer" % [index, phase_index]
			total_duration += int(phase["duration_ms"])
			if int(phase["duration_ms"]) < 0 or int(phase["duration_ms"]) > 60000:
				return "spells[%d].phases[%d].duration_ms outside [0,60000]" % [index, phase_index]
			if not phase.has("emitters") or not phase["emitters"] is Array or phase["emitters"].is_empty():
				return "spells[%d].phases[%d] requires emitters" % [index, phase_index]
			for emitter_index in range(phase["emitters"].size()):
				var error := _validate_emitter(phase["emitters"][emitter_index], index, phase_index, emitter_index)
				if not error.is_empty():
					return error
				var emitter_id := String(phase["emitters"][emitter_index]["emitter_id"])
				if emitter_ids.has(emitter_id):
					return "spells[%d]: duplicate emitter_id %s" % [index, emitter_id]
				emitter_ids.append(emitter_id)
		if not phase_names.has("impact"):
			return "spells[%d]: impact phase is required" % index
		if total_duration > 60000:
			return "spells[%d]: total duration exceeds 60000 ms" % index
		var authority = spell.get("gameplay_authority")
		if not authority is Dictionary:
			return "spells[%d] requires gameplay_authority" % index
		if authority.get("damage_owner") != "gameplay" or authority.get("hit_detection") != "gameplay":
			return "spells[%d].gameplay_authority must remain gameplay" % index
		if spell.has("decal_policy"):
			var policy = spell["decal_policy"]
			if not policy is Dictionary:
				return "spells[%d].decal_policy must be an object" % index
			if int(policy.get("max_decals", 0)) > max_decals:
				return "spells[%d].decal_policy exceeds max_decals" % index
	return ""


func _validate_emitter(emitter, spell_index: int, phase_index: int, emitter_index: int) -> String:
	var prefix := "spells[%d].phases[%d].emitters[%d]" % [spell_index, phase_index, emitter_index]
	if not emitter is Dictionary:
		return prefix + " must be an object"
	if not emitter.has("emitter_id") or not emitter["emitter_id"] is String or not _is_contract_id(String(emitter["emitter_id"])):
		return prefix + ".emitter_id does not match spellfx.v1"
	if not emitter.has("kind") or not KINDS.has(String(emitter["kind"])):
		return prefix + ".kind is invalid"
	if not emitter.has("amount") or not _is_integer(emitter["amount"]):
		return prefix + ".amount must be an integer"
	if int(emitter["amount"]) < 0 or int(emitter["amount"]) > 100000:
		return prefix + ".amount outside [0,100000]"
	if not emitter.has("lifetime_ms") or not _is_integer(emitter["lifetime_ms"]):
		return prefix + ".lifetime_ms must be an integer"
	if int(emitter["lifetime_ms"]) < 0 or int(emitter["lifetime_ms"]) > 60000:
		return prefix + ".lifetime_ms outside [0,60000]"
	for key in ["gpu", "light_bridge"]:
		if not emitter.has(key) or not emitter[key] is bool:
			return prefix + "." + key + " must be boolean"
	var is_light: bool = emitter["kind"] == "light"
	if is_light != bool(emitter["light_bridge"]):
		return prefix + ": light_bridge mismatch"
	if emitter["kind"] in ["light", "decal"] and int(emitter["amount"]) < 1:
		return prefix + ": light/decal requires amount >= 1"
	return ""


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


func _tight(value: int, limit: int) -> bool:
	return limit > 0 and float(value) >= float(limit) * TIGHT_RATIO


func _verdict(totals: Dictionary) -> String:
	if (
		totals["emitters"] > max_emitters
		or totals["particles"] > max_particles
		or totals["gpu_emitters"] > max_gpu_emitters
		or totals["decals"] > max_decals
	):
		return "OVER_BUDGET"
	if (
		_tight(totals["emitters"], max_emitters)
		or _tight(totals["particles"], max_particles)
		or _tight(totals["gpu_emitters"], max_gpu_emitters)
		or _tight(totals["decals"], max_decals)
	):
		return "TIGHT"
	return "FIT"


func _reduce_particles(entries: Array, target: int) -> Dictionary:
	var working: Array = []
	var total := 0
	for entry in entries:
		var copy: Dictionary = entry.duplicate(true)
		working.append(copy)
		total += int(copy["amount"])
	working.sort_custom(func(a, b):
		if int(a["amount"]) == int(b["amount"]):
			return String(a["emitter_id"]) < String(b["emitter_id"])
		return int(a["amount"]) > int(b["amount"])
	)
	var steps: Array = []
	var rounds := 0
	while total > target and rounds < 64:
		var progress := false
		for entry in working:
			if total <= target:
				break
			var amount := int(entry["amount"])
			if amount <= 0:
				continue
			var next_amount := amount / 2
			var saved := amount - next_amount
			entry["amount"] = next_amount
			total -= saved
			steps.append({
				"spell_id": entry["spell_id"],
				"emitter_id": entry["emitter_id"],
				"from_amount": amount,
				"to_amount": next_amount,
				"saved_particles": saved,
			})
			progress = true
		if not progress:
			break
		rounds += 1
	return {"steps": steps, "projected_particles": total, "steps_count": steps.size()}


func _reduce_gpu(entries: Array, target: int) -> Dictionary:
	var working: Array = []
	for entry in entries:
		working.append(entry.duplicate(true))
	working.sort_custom(func(a, b):
		if int(a["amount"]) == int(b["amount"]):
			return String(a["emitter_id"]) < String(b["emitter_id"])
		return int(a["amount"]) < int(b["amount"])
	)
	var steps: Array = []
	while working.size() > target:
		var entry: Dictionary = working.pop_front()
		steps.append({
			"spell_id": entry["spell_id"],
			"emitter_id": entry["emitter_id"],
			"action": "convert_to_cpu",
		})
	return {"steps": steps, "projected_gpu_emitters": working.size(), "steps_count": steps.size()}


func _finding(code: String, severity: String, message: String) -> Dictionary:
	return {"code": code, "severity": severity, "message": message}


func _sorted_findings(findings: Array) -> Array:
	var order := {"high": 0, "medium": 1, "low": 2, "info": 3}
	findings.sort_custom(func(a, b):
		if order[a["severity"]] == order[b["severity"]]:
			return String(a["code"]) < String(b["code"])
		return order[a["severity"]] < order[b["severity"]]
	)
	return findings


func _recommendations(totals: Dictionary) -> Array:
	var recommendations: Array = []
	if totals["particles"] > max_particles:
		recommendations.append({"action": "reduce_particles", "quality_cost": "medium", "excess": totals["particles"] - max_particles})
	if totals["gpu_emitters"] > max_gpu_emitters:
		recommendations.append({"action": "convert_gpu_to_cpu", "quality_cost": "high", "excess": totals["gpu_emitters"] - max_gpu_emitters})
	if totals["emitters"] > max_emitters:
		recommendations.append({"action": "merge_or_drop_emitters", "quality_cost": "high", "excess": totals["emitters"] - max_emitters})
	if totals["decals"] > max_decals:
		recommendations.append({"action": "reduce_decal_emitters", "quality_cost": "medium", "excess": totals["decals"] - max_decals})
	return recommendations


func _limitations() -> Array[String]:
	return [
		"planning only: no particle, emitter, light, decal or renderer is created",
		"particle totals are arithmetic amounts, not simulated alive particles or overdraw",
		"GPU-to-CPU conversion is a planning suggestion, not a measured trade-off",
		"emitter merging and decal reduction have no projected scene in this prototype",
		"visual clarity and runtime cost are INCONCLUSIVE_NOT_RUN",
		"no scene, engine or project.godot integration",
	]


func _invalid(reason: String) -> Dictionary:
	last_error = reason
	var report := {
		"schema_version": REPORT_SCHEMA,
		"verdict": "INVALID_INPUT",
		"totals": {"spells": 0, "emitters": 0, "particles": 0, "gpu_emitters": 0, "decals": 0, "light_bridges": 0, "duration_ms": 0},
		"budget": {
			"max_emitters": max_emitters,
			"max_particles": max_particles,
			"max_gpu_emitters": max_gpu_emitters,
			"max_decals": max_decals,
		},
		"per_spell": [],
		"reduction_plan": {"particles": {"steps": [], "projected_particles": 0, "steps_count": 0}, "gpu_emitters": {"steps": [], "projected_gpu_emitters": 0, "steps_count": 0}},
		"findings": [],
		"recommendations": [],
		"limitations": _limitations(),
		"reason": reason,
	}
	_last_report = report
	return report


func get_last_report() -> Dictionary:
	return _last_report


func clear() -> void:
	max_emitters = 64
	max_particles = 20000
	max_gpu_emitters = 16
	max_decals = 64
	last_error = ""
	_last_report = {}
