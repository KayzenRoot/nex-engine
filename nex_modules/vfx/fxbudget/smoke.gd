extends SceneTree

# Headless deterministic smoke for NEX M05-FXBUDGET FXBudgetPlanner.
# godot --headless --path nex_modules/vfx/fxbudget --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _emitter(emitter_id: String, kind: String, amount: int, gpu := false, light_bridge := false) -> Dictionary:
	return {
		"emitter_id": emitter_id, "kind": kind, "amount": amount,
		"lifetime_ms": 500, "gpu": gpu, "light_bridge": light_bridge,
	}


func _authority() -> Dictionary:
	return {"damage_owner": "gameplay", "hit_detection": "gameplay", "cancel_on_death": true}


func _spells() -> Array:
	return [
		{
			"spell_id": "ember-bolt", "element": "fire",
			"phases": [
				{"phase": "cast", "duration_ms": 300, "emitters": [_emitter("cast-spark", "particles", 64, true)]},
				{"phase": "travel", "duration_ms": 200, "emitters": [_emitter("travel-trail", "trail", 32)]},
				{"phase": "impact", "duration_ms": 150, "emitters": [
					_emitter("impact-burst", "particles", 128, true),
					_emitter("impact-light", "light", 1, false, true),
				]},
				{"phase": "linger", "duration_ms": 4000, "emitters": [_emitter("linger-decal", "decal", 1)]},
			],
			"gameplay_authority": _authority(),
			"decal_policy": {"max_decals": 8, "fade_ms": 4000},
		},
		{
			"spell_id": "frost-nova", "element": "ice",
			"phases": [
				{"phase": "impact", "duration_ms": 1500, "emitters": [_emitter("nova-burst", "particles", 256, true)]},
				{"phase": "linger", "duration_ms": 3000, "emitters": [_emitter("nova-decal", "decal", 2)]},
			],
			"gameplay_authority": _authority(),
			"decal_policy": {"max_decals": 4, "fade_ms": 3000},
		},
	]


func _finding(report: Dictionary, code: String) -> bool:
	for item in report["findings"]:
		if item["code"] == code:
			return true
	return false


func _recommendation(report: Dictionary, action: String) -> bool:
	for item in report["recommendations"]:
		if item["action"] == action:
			return true
	return false


func _run() -> void:
	var packed := load("res://main.tscn") as PackedScene
	_check(packed != null, "main scene loads")
	if packed == null:
		_finish()
		return
	var planner = packed.instantiate()
	root.add_child(planner)
	await process_frame

	_check(planner.configure({}), "default configuration accepted")
	_check(not planner.configure({"max_emitters": 257}), "emitter budget above limit rejected")
	_check(not planner.configure({"max_particles": -1}), "negative particle budget rejected")
	_check(not planner.configure({"max_gpu_emitters": 65}), "GPU budget above limit rejected")
	_check(not planner.configure({"max_decals": 257}), "decal budget above limit rejected")
	_check(planner.configure({"max_emitters": 64, "max_particles": 20000, "max_gpu_emitters": 16, "max_decals": 64}), "valid configuration accepted")

	var empty: Dictionary = planner.analyze([])
	_check(empty["verdict"] == "FIT", "empty spell set fits")
	_check(empty["totals"]["spells"] == 0, "empty spell count")

	var report: Dictionary = planner.analyze(_spells())
	_check(report["schema_version"] == "fx_budget.report.v1", "report schema version")
	_check(report["verdict"] == "FIT", "fixture fits default budget")
	_check(report["totals"]["spells"] == 2, "spell count")
	_check(report["totals"]["emitters"] == 7, "emitter total")
	_check(report["totals"]["particles"] == 484, "particle total")
	_check(report["totals"]["gpu_emitters"] == 3, "GPU emitter total")
	_check(report["totals"]["decals"] == 2, "decal total")
	_check(report["totals"]["light_bridges"] == 1, "light bridge total")
	_check(report["per_spell"].size() == 2, "per-spell entries")
	_check(report["per_spell"][0]["spell_id"] == "ember-bolt", "per-spell sorted by id")
	_check(report["per_spell"][0]["emitters"] == 5, "ember emitter count")
	_check(report["per_spell"][1]["particles"] == 258, "frost particle count")
	_check(report["limitations"].size() >= 5, "limitations documented")
	_check(JSON.stringify(report) == JSON.stringify(planner.analyze(_spells())), "analysis is deterministic")
	_check(JSON.stringify(planner.get_last_report()) == JSON.stringify(report), "last report retained")

	planner.configure({"max_particles": 300})
	var over_particles: Dictionary = planner.analyze(_spells())
	_check(over_particles["verdict"] == "OVER_BUDGET", "particle budget exceeded")
	_check(_finding(over_particles, "over_particles"), "over particles finding")
	_check(over_particles["reduction_plan"]["particles"]["steps_count"] > 0, "particle reduction steps generated")
	_check(over_particles["reduction_plan"]["particles"]["projected_particles"] <= 300, "particle plan reaches the budget")
	_check(over_particles["reduction_plan"]["particles"]["steps"][0].has("from_amount"), "particle step records source amount")
	_check(_recommendation(over_particles, "reduce_particles"), "particle recommendation present")

	planner.configure({"max_particles": 20000, "max_gpu_emitters": 1})
	var over_gpu: Dictionary = planner.analyze(_spells())
	_check(over_gpu["verdict"] == "OVER_BUDGET", "GPU budget exceeded")
	_check(_finding(over_gpu, "over_gpu_emitters"), "over GPU finding")
	_check(over_gpu["reduction_plan"]["gpu_emitters"]["steps_count"] == 2, "two GPU emitters converted")
	_check(over_gpu["reduction_plan"]["gpu_emitters"]["projected_gpu_emitters"] == 1, "GPU plan reaches the budget")
	_check(over_gpu["reduction_plan"]["gpu_emitters"]["steps"][0]["action"] == "convert_to_cpu", "GPU step action")
	_check(_recommendation(over_gpu, "convert_gpu_to_cpu"), "GPU recommendation present")

	planner.configure({"max_gpu_emitters": 16, "max_emitters": 4})
	var over_emitters: Dictionary = planner.analyze(_spells())
	_check(over_emitters["verdict"] == "OVER_BUDGET", "emitter budget exceeded")
	_check(_recommendation(over_emitters, "merge_or_drop_emitters"), "emitter merge recommendation")

	planner.configure({"max_emitters": 64, "max_decals": 1})
	var decal_spells: Array = _spells()
	decal_spells[0]["decal_policy"]["max_decals"] = 1
	decal_spells[1]["decal_policy"]["max_decals"] = 1
	var over_decals: Dictionary = planner.analyze(decal_spells)
	_check(over_decals["verdict"] == "OVER_BUDGET", "decal budget exceeded")
	_check(_recommendation(over_decals, "reduce_decal_emitters"), "decal recommendation")

	planner.configure({"max_decals": 64, "max_particles": int(484 * 1.05)})
	_check(planner.analyze(_spells())["verdict"] == "TIGHT", "small headroom yields tight verdict")

	planner.configure({"max_particles": 20000})
	var duplicate: Array = _spells()
	duplicate[0]["phases"][1]["emitters"][0]["emitter_id"] = "cast-spark"
	_check(planner.analyze(duplicate)["verdict"] == "INVALID_INPUT", "duplicate emitter id rejected")

	var no_impact: Array = _spells()
	no_impact[1]["phases"] = [no_impact[1]["phases"][1]]
	_check(planner.analyze(no_impact)["verdict"] == "INVALID_INPUT", "missing impact rejected")

	var visual: Array = _spells()
	visual[0]["gameplay_authority"]["damage_owner"] = "visual_only"
	_check(planner.analyze(visual)["verdict"] == "INVALID_INPUT", "visual-only authority rejected")

	var bridge: Array = _spells()
	bridge[0]["phases"][2]["emitters"][1]["light_bridge"] = false
	_check(planner.analyze(bridge)["verdict"] == "INVALID_INPUT", "light bridge mismatch rejected")

	var element: Array = _spells()
	element[0]["element"] = "holy"
	_check(planner.analyze(element)["verdict"] == "INVALID_INPUT", "unknown element rejected")

	var long_spell: Array = _spells()
	long_spell[0]["phases"][3]["duration_ms"] = 60000
	_check(planner.analyze(long_spell)["verdict"] == "INVALID_INPUT", "duration above limit rejected")

	var duplicate_phase: Array = _spells()
	duplicate_phase[0]["phases"][1]["phase"] = "cast"
	_check(planner.analyze(duplicate_phase)["verdict"] == "INVALID_INPUT", "duplicate phase rejected")

	var short_id: Array = _spells()
	short_id[0]["phases"][0]["emitters"][0]["emitter_id"] = "x"
	_check(planner.analyze(short_id)["verdict"] == "INVALID_INPUT", "short emitter id rejected")

	var big_amount: Array = _spells()
	big_amount[0]["phases"][0]["emitters"][0]["amount"] = 100001
	_check(planner.analyze(big_amount)["verdict"] == "INVALID_INPUT", "amount above limit rejected")

	var dark_light: Array = _spells()
	dark_light[0]["phases"][2]["emitters"][1]["amount"] = 0
	_check(planner.analyze(dark_light)["verdict"] == "INVALID_INPUT", "light amount below one rejected")

	var policy: Array = _spells()
	policy[1]["decal_policy"]["max_decals"] = 65
	_check(planner.analyze(policy)["verdict"] == "INVALID_INPUT", "decal policy above budget rejected")

	var no_authority: Array = _spells()
	no_authority[0].erase("gameplay_authority")
	_check(planner.analyze(no_authority)["verdict"] == "INVALID_INPUT", "missing gameplay authority rejected")

	var empty_phase: Array = _spells()
	empty_phase[0]["phases"][0]["emitters"] = []
	_check(planner.analyze(empty_phase)["verdict"] == "INVALID_INPUT", "empty phase emitters rejected")

	var invalid: Dictionary = planner.analyze([{"spell_id": "x"}])
	_check(invalid["verdict"] == "INVALID_INPUT", "malformed spell rejected")
	_check(invalid.has("reason"), "invalid report carries a reason")

	planner.clear()
	_check(planner.max_particles == 20000 and planner.max_emitters == 64, "clear restores budgets")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M05_FXBUDGET_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M05_FXBUDGET_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
