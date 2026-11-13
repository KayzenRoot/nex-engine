extends SceneTree

# Headless deterministic smoke for NEX M08-COMPOSITION CompositionPlanner.
# godot --headless --path nex_modules/render2_5d/composition --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _base(risks := 0) -> Dictionary:
	return {
		"plan_schema": "depth_composition.plan.v1",
		"plan_sha256": "a".repeat(64),
		"opaque_count": 12,
		"alpha_count": 4,
		"overlay_count": 2,
		"z_fight_risks": risks,
		"alpha_over_critical": 0,
		"overlay_gameplay_conflicts": 0,
	}


func _fresh(planner, options := {}) -> void:
	planner.clear()
	planner.configure({})
	planner.set_base_plan(options.get("base", _base()))
	planner.set_policies({
		"depth_policy": options.get("depth_policy", 2),
		"critical_guard": options.get("critical_guard", true),
		"hud_layer_id": options.get("hud_layer_id", "hud"),
		"overlay_may_cover_gameplay": options.get("overlay_cover", false),
		"conflict_policy": options.get("conflict_policy", 0),
	})
	planner.register_layer("sky", 0, options.get("sky_parallax", 0.2), 0, 1.0)
	planner.register_layer("world", 1, 1.0, 0, 1.0, true, false, options.get("world_override", false), 1.0)
	planner.register_layer("dust", 2, 1.4, 1, options.get("dust_alpha", 0.35), false, true)
	if not options.get("no_hud", false):
		planner.register_layer("hud", 3, 0.0, 0, 1.0, false, options.get("hud_cover", false), options.get("hud_override", false), 1.0)
	planner.register_critical_entity("player", 0, options.get("player_visible", true))
	planner.register_critical_entity("threat-01", 1, options.get("threat_visible", true))


func _has(report: Dictionary, code: String) -> bool:
	for finding in report["conflicts"]:
		if finding["code"] == code:
			return true
	return false


func _ids(plan: Dictionary) -> Array:
	var ids: Array = []
	for layer in plan["layers"]:
		ids.append(layer["layer_id"])
	return ids


func _provenance() -> Dictionary:
	return {
		"base_sha": "b".repeat(40),
		"head_sha": "c".repeat(40),
		"godot_version": "4.7.2-stable",
		"hardware": {"gpu_model": "NVIDIA GeForce RTX 5050", "driver_version": "617.14"},
		"capture_mode": "headless",
		"measurement_status": "UNAVAILABLE",
	}


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
	_check(not planner.configure({"max_layers": 0}), "zero max layers rejected")
	_check(not planner.configure({"max_layers": 33}), "max layers above limit rejected")
	_check(not planner.configure({"max_alpha_over_gameplay": 1.5}), "alpha guard above one rejected")
	_check(planner.configure({"max_layers": 32, "max_alpha_over_gameplay": 0.5}), "valid configuration accepted")

	_check(planner.set_base_plan({"plan_schema": "none", "opaque_count": 0, "alpha_count": 0, "overlay_count": 0, "z_fight_risks": 0, "alpha_over_critical": 0, "overlay_gameplay_conflicts": 0}), "empty base plan accepted")
	_check(not planner.set_base_plan({"plan_schema": "none", "opaque_count": 1, "alpha_count": 0, "overlay_count": 0, "z_fight_risks": 0, "alpha_over_critical": 0, "overlay_gameplay_conflicts": 0}), "none plan with counts rejected")
	_check(not planner.set_base_plan({"plan_schema": "depth_composition.plan.v1", "opaque_count": 1, "alpha_count": 0, "overlay_count": 0, "z_fight_risks": 0, "alpha_over_critical": 0, "overlay_gameplay_conflicts": 0}), "real plan without digest rejected")
	_check(not planner.set_base_plan({"plan_schema": "other", "opaque_count": 0, "alpha_count": 0, "overlay_count": 0, "z_fight_risks": 0, "alpha_over_critical": 0, "overlay_gameplay_conflicts": 0}), "invalid plan schema rejected")
	_check(planner.set_base_plan(_base()), "real base plan accepted")

	_check(planner.set_policies({}), "default policies accepted")
	_check(not planner.set_policies({"depth_policy": 3}), "invalid depth policy rejected")
	_check(not planner.set_policies({"conflict_policy": 2}), "invalid conflict policy rejected")
	_check(not planner.set_policies({"hud_layer_id": "HUD"}), "invalid hud id rejected")
	_check(planner.set_policies({"depth_policy": 2, "critical_guard": true, "hud_layer_id": "hud", "overlay_may_cover_gameplay": false, "conflict_policy": 0}), "valid policies accepted")

	_fresh(planner)
	var plan: Dictionary = planner.plan()
	_check(plan["verdict"] == "SAFE_CONFIG_HEURISTIC", "safe fixture verdict")
	_check(plan["schema_version"] == "composition.plan.v1", "plan schema version")
	_check(plan["layers"].size() == 4, "all layers exported")
	_check(_ids(plan) == ["sky", "world", "dust", "hud"], "draw order grouped by role")
	_check(plan["layers"][0]["draw_index"] == 0, "first draw index")
	_check(plan["layers"][3]["draw_index"] == 3, "hud draw index last")
	_check(plan["layers"][3]["effective_parallax"] == 0.0, "hud parallax is zero")
	_check(plan["layers"][1]["effective_parallax"] == 1.0, "gameplay parallax preserved")
	_check(plan["summary"]["high"] == 0 and plan["summary"]["medium"] == 0, "safe fixture has no high/medium conflicts")
	_check(plan["base_3d_plan"]["plan_sha256"] == "a".repeat(64), "base plan preserved")
	_check(plan["policies"]["depth_policy"] == "hybrid", "depth policy exported")
	_check(plan["policies"]["conflict_policy"] == "report", "conflict policy exported")
	_check(plan["critical_entities"][0]["entity_id"] == "player", "critical entities sorted")
	_check(plan["critical_entities"].size() == 2, "critical entities exported")
	_check(plan["limitations"].size() >= 5, "limitations documented")
	_check(JSON.stringify(plan) == JSON.stringify(planner.plan()), "plan is deterministic")
	_check(JSON.stringify(planner.get_last_plan()) == JSON.stringify(plan), "last plan retained")

	_fresh(planner, {"sky_parallax": 1.0})
	plan = planner.plan()
	_check(_has(plan, "parallax_mismatch"), "parallax mismatch flagged")
	_check(plan["verdict"] == "SAFE_CONFIG_HEURISTIC", "low-only conflict keeps heuristic verdict")

	_fresh(planner, {"dust_alpha": 0.8})
	plan = planner.plan()
	_check(_has(plan, "alpha_over_critical"), "alpha over critical flagged")
	_check(plan["verdict"] == "CONFLICTS_REPORTED", "alpha conflict produces reported verdict")

	_fresh(planner, {"critical_guard": false})
	_check(_has(planner.plan(), "critical_guard_missing"), "missing critical guard flagged")

	_fresh(planner, {"hud_cover": true})
	plan = planner.plan()
	_check(_has(plan, "hud_covers_gameplay"), "hud covering gameplay flagged")
	_check(plan["summary"]["medium"] >= 1, "report policy yields medium conflict")

	_fresh(planner, {"hud_cover": true, "conflict_policy": 1})
	_check(_has(planner.plan(), "hud_covers_gameplay"), "block policy still reports hud conflict")

	_fresh(planner, {"hud_override": true})
	_check(_has(planner.plan(), "hud_depth_override"), "hud depth override flagged")

	_fresh(planner, {"depth_policy": 0, "world_override": true})
	_check(_has(planner.plan(), "depth_override_under_inherit"), "inherit_3d override flagged")

	_fresh(planner, {"depth_policy": 1})
	_check(_has(planner.plan(), "missing_depth_override"), "override_per_layer missing override flagged")

	_fresh(planner, {"base": _base(1)})
	_check(_has(planner.plan(), "base_z_fight_risk"), "base z-fight risk flagged")

	var alpha_base := _base()
	alpha_base["alpha_over_critical"] = 1
	_fresh(planner, {"base": alpha_base})
	_check(_has(planner.plan(), "base_alpha_over_critical"), "base alpha-over-critical flagged")

	var overlay_base := _base()
	overlay_base["overlay_gameplay_conflicts"] = 1
	_fresh(planner, {"base": overlay_base})
	_check(_has(planner.plan(), "base_overlay_gameplay_conflict"), "base overlay conflict flagged")

	_fresh(planner, {"no_hud": true})
	plan = planner.plan()
	_check(_has(plan, "hud_layer_missing"), "missing hud layer flagged")
	_check(_has(plan, "hud_reference_invalid"), "missing hud reference flagged")

	_fresh(planner, {"hud_layer_id": "world"})
	_check(_has(planner.plan(), "hud_reference_invalid"), "hud reference to non-hud flagged")

	_fresh(planner, {"player_visible": false, "threat_visible": false})
	plan = planner.plan()
	_check(_has(plan, "critical_layer_without_entity"), "critical layer without visible entity flagged")
	_check(plan["summary"]["high"] == 0, "no high conflicts without visible critical entity")

	_fresh(planner)
	planner.clear()
	_check(planner.plan()["verdict"] == "INVALID_INPUT", "empty stack is invalid")

	_fresh(planner)
	planner.clear()
	planner.register_layer("sky", 0, 0.2, 0, 1.0)
	_check(planner.plan()["verdict"] == "INVALID_INPUT", "missing critical entities is invalid")

	_fresh(planner)
	planner.clear()
	planner.configure({"max_layers": 2})
	planner.register_layer("one", 0, 0.2, 0, 1.0)
	planner.register_layer("two", 1, 1.0, 0, 1.0)
	_check(not planner.register_layer("three", 2, 1.4, 0, 1.0), "max layers enforced")

	_fresh(planner)
	planner.clear()
	planner.register_layer("hud", 3, 0.0, 0, 1.0)
	planner.register_layer("sky", 0, 0.2, 0, 1.0)
	planner.register_layer("world", 1, 1.0, 0, 1.0, true)
	planner.register_critical_entity("player", 0, true)
	plan = planner.plan()
	_check(_has(plan, "stack_reordered"), "stack reorder reported")
	_check(_ids(plan) == ["sky", "world", "hud"], "reordered draw stack groups roles")

	_fresh(planner)
	var observation: Dictionary = planner.export_observation("m08-smoke-001", "2026-11-13T12:00:00Z", _provenance())
	_check(observation.get("schema_version", "") == "composition.v1", "observation exports composition.v1")
	_check(observation["performance"]["measurement_status"] == "UNAVAILABLE", "observation performance is unavailable")
	_check(observation["layer_stack"].size() == 4, "observation carries all layers")
	_check(not observation["layer_stack"][0].has("draw_index"), "observation omits planner-only fields")
	_check(not observation["layer_stack"][3].has("depth_override_m"), "observation hud has no depth override")
	_check(observation["alpha_policy"]["sort"] == "back_to_front", "observation alpha sort")
	_check(observation["overlay_safety"]["hud_layer_id"] == "hud", "observation hud reference")

	var bad_sha := _provenance()
	bad_sha["base_sha"] = "B".repeat(40)
	_check(planner.export_observation("m08-smoke-002", "2026-11-13T12:00:00Z", bad_sha).is_empty(), "invalid SHA rejected")
	var measured := _provenance()
	measured["measurement_status"] = "MEASURED"
	_check(planner.export_observation("m08-smoke-003", "2026-11-13T12:00:00Z", measured).is_empty(), "measured provenance requires evidence")
	measured["evidence_uri"] = "evidence://m08-smoke"
	_check(not planner.export_observation("m08-smoke-004", "2026-11-13T12:00:00Z", measured).is_empty(), "measured provenance with evidence accepted")

	planner.clear()
	_check(planner.max_layers == 32 and planner.max_alpha_over_gameplay == 0.5, "clear restores defaults")
	_check(planner.plan()["verdict"] == "INVALID_INPUT", "cleared planner is invalid")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M08_COMPOSITION_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M08_COMPOSITION_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
