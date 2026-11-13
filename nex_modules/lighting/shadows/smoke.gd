extends SceneTree

# Headless deterministic smoke for NEX M03-SHADOWSTAB ShadowStabilityAnalyzer.
# godot --headless --path nex_modules/lighting/shadows --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _plan() -> Dictionary:
	return {
		"schema_version": "lighting.plan.v1",
		"environment": {},
		"lights": [
			{
				"light_id": "sun", "light_type": "directional", "energy": 1.2,
				"shadow_enabled": true, "shadow_assigned": true, "shadow_slot": 0,
				"shadow_bias": 0.05, "shadow_softness": 0.2, "cascades": 3,
			},
			{
				"light_id": "lamp", "light_type": "omni", "energy": 3.0,
				"shadow_enabled": true, "shadow_assigned": true, "shadow_slot": 1,
				"shadow_bias": 0.1, "shadow_softness": 0.4, "range_m": 8.0,
			},
			{
				"light_id": "gate", "light_type": "spot", "energy": 2.0,
				"shadow_enabled": false, "shadow_assigned": false, "shadow_slot": -1,
				"shadow_bias": 0.05, "shadow_softness": 0.1, "spot_angle_degrees": 35.0,
			},
			{
				"light_id": "torch", "light_type": "spot", "energy": 2.0,
				"shadow_enabled": true, "shadow_assigned": true, "shadow_slot": 2,
				"shadow_bias": 0.03, "shadow_softness": 0.7, "spot_angle_degrees": 3.0,
			},
		],
		"shadow_budget": {"max_shadowed_lights": 4, "directional_cascades": 3, "atlas_size": 4096},
	}


func _observation() -> Dictionary:
	var observation := _plan()
	observation["schema_version"] = "lighting.v1"
	observation.erase("environment")
	observation["observation_id"] = "m03-shadowstability-001"
	for light in observation["lights"]:
		light.erase("shadow_assigned")
		light.erase("shadow_slot")
	return observation


func _find(report: Dictionary, code: String) -> bool:
	for finding in report["findings"]:
		if finding["code"] == code:
			return true
	return false


func _run() -> void:
	var packed := load("res://main.tscn") as PackedScene
	_check(packed != null, "main scene loads")
	if packed == null:
		_finish()
		return
	var analyzer = packed.instantiate()
	root.add_child(analyzer)
	await process_frame

	_check(analyzer.configure({}), "default configuration accepted")
	_check(not analyzer.configure({"camera_near_m": 0.0}), "zero near plane rejected")
	_check(not analyzer.configure({"camera_far_m": 0.05}), "far plane below near rejected")
	_check(not analyzer.configure({"split_lambda": 1.5}), "invalid split lambda rejected")
	_check(analyzer.configure({"camera_near_m": 1.0, "camera_far_m": 100.0, "split_lambda": 1.0}), "valid camera configuration accepted")
	analyzer.clear()
	_check(analyzer.camera_near_m == 0.1 and analyzer.camera_far_m == 500.0, "clear restores configuration")
	_check(not analyzer.configure({"camera_far_m": 20000.0}), "far plane above limit rejected")

	var report: Dictionary = analyzer.analyze_plan(_plan())
	_check(report["schema_version"] == "shadow_stability.report.v1", "report schema version")
	_check(report["verdict"] == "STABLE_CONFIG_HEURISTIC_WITH_NOTES", "valid plan yields heuristic verdict with notes")
	_check(report["summary"]["low"] >= 1, "low severity findings counted")
	_check(report["summary"]["high"] == 0, "valid plan has no high findings")
	_check(_find(report, "spot_angle_degenerate"), "narrow spotlight flagged")
	_check(report["metrics"]["shadowed_lights"] == 3, "shadowed light count")
	_check(report["metrics"]["directional_shadowed_lights"] == 1, "directional shadow count")
	_check(report["metrics"]["shadow_tiles_estimate"] == 5, "shadow tile estimate")
	_check(report["metrics"]["atlas_tile_budget"] == 16, "atlas tile budget")
	_check(report["cascade_splits_m"].size() == 4, "cascade splits include near plus three cascades")
	var splits: Array = report["cascade_splits_m"]
	_check(is_equal_approx(splits[0], 0.1), "first split equals near plane")
	_check(is_equal_approx(splits[3], 500.0), "last split equals far plane")
	_check(splits[1] > splits[0] and splits[2] > splits[1] and splits[3] > splits[2], "cascade splits increase")
	_check(report["limitations"].size() >= 5, "limitations documented")
	_check(not report.has("reason"), "successful report has no reason")
	_check(JSON.stringify(report) == JSON.stringify(analyzer.analyze_plan(_plan())), "plan analysis is deterministic")
	_check(JSON.stringify(analyzer.get_last_report()) == JSON.stringify(report), "last report is retained")

	var low_bias: Dictionary = _plan()
	low_bias["lights"][1]["shadow_bias"] = 0.01
	report = analyzer.analyze_plan(low_bias)
	_check(_find(report, "low_bias_acne_risk"), "low bias flags acne risk")
	_check(report["verdict"] == "RISK_REPRODUCED", "medium finding produces risk verdict")

	var high_bias: Dictionary = _plan()
	high_bias["lights"][1]["shadow_bias"] = 0.6
	_check(_find(analyzer.analyze_plan(high_bias), "high_bias_peter_panning_risk"), "high bias flags peter-panning risk")

	var low_atlas: Dictionary = _plan()
	low_atlas["shadow_budget"]["atlas_size"] = 256
	report = analyzer.analyze_plan(low_atlas)
	_check(_find(report, "atlas_pressure"), "small atlas flags pressure")
	_check(report["metrics"]["atlas_pressure_ratio"] > 1.0, "pressure ratio above one")
	_check(_find(report, "soft_shadow_low_atlas"), "soft shadow with small atlas flagged")

	var zero_budget: Dictionary = _plan()
	zero_budget["shadow_budget"]["max_shadowed_lights"] = 0
	report = analyzer.analyze_plan(zero_budget)
	_check(_find(report, "shadow_budget_zero"), "zero shadow budget flagged")
	_check(_find(report, "shadow_budget_exceeded"), "shadowed lights above budget flagged")

	var cascade_overflow: Dictionary = _plan()
	cascade_overflow["lights"][0]["cascades"] = 4
	_check(_find(analyzer.analyze_plan(cascade_overflow), "directional_cascades_exceed_budget"), "cascade overflow flagged")

	var cascade_missing: Dictionary = _plan()
	cascade_missing["lights"][0]["cascades"] = 0
	_check(_find(analyzer.analyze_plan(cascade_missing), "directional_cascades_missing"), "missing cascades flagged")

	var dark_caster: Dictionary = _plan()
	dark_caster["lights"][0]["energy"] = 0.0
	_check(_find(analyzer.analyze_plan(dark_caster), "shadow_caster_without_energy"), "dark shadow caster flagged")

	var demoted: Dictionary = _plan()
	demoted["lights"][1]["shadow_assigned"] = false
	_check(_find(analyzer.analyze_plan(demoted), "caster_without_shadow_slot"), "demoted caster flagged")

	var missing_assignment: Dictionary = _plan()
	missing_assignment["lights"][1].erase("shadow_assigned")
	_check(_find(analyzer.analyze_plan(missing_assignment), "shadow_assignment_missing"), "missing assignment flagged")

	var no_shadows: Dictionary = _plan()
	for light in no_shadows["lights"]:
		light["shadow_enabled"] = false
	report = analyzer.analyze_plan(no_shadows)
	_check(_find(report, "no_shadow_workload"), "empty shadow workload recorded")
	_check(report["verdict"] == "STABLE_CONFIG_HEURISTIC_WITH_NOTES", "info-only report keeps heuristic notes")

	var observation: Dictionary = _observation()
	report = analyzer.analyze_observation(observation)
	_check(report["source_schema"] == "lighting.v1", "observation source recorded")
	_check(report["metrics"]["shadowed_lights"] == 3, "observation shadow count")
	_check(report["verdict"] == "STABLE_CONFIG_HEURISTIC_WITH_NOTES", "observation analysis verdict")

	var bad_schema: Dictionary = _plan()
	bad_schema["schema_version"] = "lighting.plan.v2"
	report = analyzer.analyze_plan(bad_schema)
	_check(report["verdict"] == "INCONCLUSIVE", "wrong plan schema is inconclusive")
	_check(report.has("reason"), "inconclusive report carries a reason")

	var bad_budget: Dictionary = _plan()
	bad_budget["shadow_budget"]["atlas_size"] = 128
	_check(analyzer.analyze_plan(bad_budget)["verdict"] == "INCONCLUSIVE", "invalid atlas is inconclusive")

	var malformed_light: Dictionary = _plan()
	malformed_light["lights"][0]["light_type"] = "area"
	_check(analyzer.analyze_plan(malformed_light)["verdict"] == "INCONCLUSIVE", "invalid light type is inconclusive")

	var missing_id: Dictionary = _plan()
	missing_id["lights"][0].erase("light_id")
	_check(analyzer.analyze_plan(missing_id)["verdict"] == "INCONCLUSIVE", "missing light id is inconclusive")

	var bad_observation: Dictionary = _observation()
	bad_observation["schema_version"] = "lighting.v0"
	_check(analyzer.analyze_observation(bad_observation)["verdict"] == "INCONCLUSIVE", "wrong observation schema is inconclusive")

	analyzer.configure({"camera_near_m": 1.0, "camera_far_m": 100.0, "split_lambda": 1.0})
	splits = analyzer.analyze_plan(_plan())["cascade_splits_m"]
	_check(is_equal_approx(splits[0], 1.0) and is_equal_approx(splits[3], 100.0), "configured camera drives cascade splits")
	analyzer.clear()
	_check(analyzer.camera_near_m == 0.1 and analyzer.camera_far_m == 500.0, "clear restores camera defaults")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M03_SHADOWSTAB_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M03_SHADOWSTAB_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
