extends SceneTree

# Headless deterministic smoke for NEX M03-LIGHTRIG LightRigPlanner.
# godot --headless --path nex_modules/lighting/light_rig --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _fresh(planner) -> void:
	planner.clear()
	planner.configure({
		"max_lights": 128,
		"max_shadowed_lights": 4,
		"max_cascades": 4,
		"atlas_size": 4096,
	})


func _light_ids(plan: Dictionary) -> Array:
	var ids: Array = []
	for light in plan["lights"]:
		ids.append(light["light_id"])
	return ids


func _provenance() -> Dictionary:
	return {
		"base_sha": "a".repeat(40),
		"head_sha": "b".repeat(40),
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
	_check(not planner.configure({"max_lights": 0}), "invalid max lights rejected")
	_check(not planner.configure({"max_shadowed_lights": 17}), "invalid shadow budget rejected")
	_check(not planner.configure({"max_cascades": 5}), "invalid cascade budget rejected")
	_check(not planner.configure({"atlas_size": 128}), "invalid atlas size rejected")
	_check(planner.configure({"atlas_size": 8192}), "maximum atlas size accepted")
	_check(planner.configure({}), "configuration restored")

	_check(planner.configure_environment({}), "default environment accepted")
	_check(not planner.configure_environment({"ambient_source": 3}), "invalid ambient source rejected")
	_check(not planner.configure_environment({"tonemap": 4}), "invalid tonemap rejected")
	_check(not planner.configure_environment({"ambient_energy": 9.0}), "invalid ambient energy rejected")
	_check(not planner.configure_environment({"fog_density": 1.5}), "invalid fog density rejected")
	_check(not planner.configure_environment({"gi_mode": 4}), "invalid GI mode rejected")
	_check(not planner.configure_environment({"gi_energy": 5.0}), "invalid GI energy rejected")

	_fresh(planner)
	_check(planner.register_light("key", 0, Color(1, 1, 1), 2.0), "directional light registered")
	_check(not planner.register_light("key", 0, Color(1, 1, 1), 2.0), "duplicate light rejected")
	_check(not planner.register_light("", 0, Color(1, 1, 1), 2.0), "empty light id rejected")
	_check(not planner.register_light("badtype", 3, Color(1, 1, 1), 2.0), "invalid light type rejected")
	_check(not planner.register_light("badcolor", 0, Color(1.5, 0, 0), 2.0), "invalid color rejected")
	_check(not planner.register_light("badenergy", 0, Color(1, 1, 1), -1.0), "negative energy rejected")
	_check(not planner.register_light("bigenergy", 0, Color(1, 1, 1), 17.0), "energy above 16 rejected")
	_check(not planner.register_light("badbias", 0, Color(1, 1, 1), 2.0, false, 1.5), "invalid bias rejected")
	_check(not planner.register_light("badsoft", 0, Color(1, 1, 1), 2.0, false, 0.05, -0.1), "invalid softness rejected")
	_check(not planner.register_light("badcull", 0, Color(1, 1, 1), 2.0, false, 0.05, 0.0, 0), "invalid cull mask rejected")
	_check(not planner.register_light("bigcull", 0, Color(1, 1, 1), 2.0, false, 0.05, 0.0, 1048576), "cull mask above limit rejected")

	_check(not planner.register_light("dirrange", 0, Color(1, 1, 1), 2.0, false, 0.05, 0.0, 1, 5.0), "directional range rejected")
	_check(not planner.register_light("dirangle", 0, Color(1, 1, 1), 2.0, false, 0.05, 0.0, 1, 0.0, 20.0), "directional spot angle rejected")
	_check(not planner.register_light("omnicascades", 1, Color(1, 1, 1), 2.0, false, 0.05, 0.0, 1, 0.0, 0.0, 2), "omni cascades rejected")
	_check(not planner.register_light("omniangle", 1, Color(1, 1, 1), 2.0, false, 0.05, 0.0, 1, 0.0, 20.0), "omni spot angle rejected")
	_check(not planner.register_light("omnirange", 1, Color(1, 1, 1), 2.0, false, 0.05, 0.0, 1, 201.0), "omni range above 200 rejected")
	_check(not planner.register_light("spotangle", 2, Color(1, 1, 1), 2.0, false, 0.05, 0.0, 1, 0.0, 91.0), "spot angle above 90 rejected")
	_check(not planner.register_light("spotcascades", 2, Color(1, 1, 1), 2.0, false, 0.05, 0.0, 1, 0.0, 20.0, 2), "spot cascades rejected")
	_check(not planner.register_light("dark", 1, Color(1, 1, 1), 0.0, true), "shadow caster without energy rejected")

	_fresh(planner)
	planner.register_light("zulu", 0, Color(1, 1, 1), 1.0)
	planner.register_light("alpha", 1, Color(1, 0, 0), 3.0)
	_check(_light_ids(planner.plan()) == ["alpha", "zulu"], "lights sorted by id")

	_fresh(planner)
	planner.register_light("low", 1, Color(1, 1, 1), 1.0, true)
	planner.register_light("high", 1, Color(1, 1, 1), 5.0, true)
	planner.register_light("mid", 1, Color(1, 1, 1), 3.0, true)
	var plan: Dictionary = planner.plan()
	_check(plan["lights"][0]["shadow_slot"] == 0, "highest energy receives first shadow slot")
	_check(plan["lights"][2]["shadow_slot"] == 1, "middle energy receives second shadow slot")
	_check(plan["lights"][1]["shadow_slot"] == 2, "lowest energy receives third shadow slot")
	_check(plan["totals"]["shadowed_lights"] == 3, "all shadowed lights fit the budget")

	_fresh(planner)
	planner.configure({"max_shadowed_lights": 1})
	planner.register_light("a", 1, Color(1, 1, 1), 1.0, true)
	planner.register_light("b", 1, Color(1, 1, 1), 2.0, true)
	plan = planner.plan()
	_check(plan["warnings"].has("shadow_budget_exceeded"), "shadow budget overflow warns")
	_check(plan["totals"]["shadowed_lights"] == 1, "shadow budget limits assigned slots")
	_check(not plan["lights"][0]["shadow_assigned"], "demoted light is marked unassigned")
	_check(plan["totals"]["estimated_shadow_maps"] == 1, "omni shadow map estimated")

	_fresh(planner)
	planner.configure({"max_cascades": 2})
	planner.register_light("sun", 0, Color(1, 1, 1), 1.0, true, 0.05, 0.0, 1, 0.0, 0.0, 3)
	plan = planner.plan()
	_check(plan["warnings"].has("directional_cascade_exceeded"), "cascade budget overflow warns")
	_check(plan["lights"][0]["cascades"] == 2, "cascades clamped in the plan")
	_check(plan["totals"]["estimated_shadow_maps"] == 2, "directional cascades estimate shadow maps")

	_fresh(planner)
	planner.register_light("sun", 0, Color(1, 1, 1), 1.0, true, 0.05, 0.0, 1, 0.0, 0.0, 2)
	planner.register_light("lamp", 1, Color(1, 1, 1), 2.0, true, 0.1, 0.2, 3, 8.0)
	plan = planner.plan()
	_check(plan["totals"]["lights"] == 2, "light count recorded")
	_check(plan["totals"]["directional_lights"] == 1, "directional count recorded")
	_check(plan["totals"]["omni_lights"] == 1, "omni count recorded")
	_check(plan["totals"]["spot_lights"] == 0, "spot count recorded")
	_check(plan["totals"]["estimated_shadow_maps"] == 3, "directional cascades plus omni map estimated")
	_check(plan["environment"]["tonemap"] == "filmic", "environment exported with contract vocabulary")
	_check(plan["limitations"].size() >= 5, "limitations documented")

	_fresh(planner)
	_check(planner.plan()["warnings"].has("no_lights"), "empty rig warns")
	planner.register_light("a", 1, Color(1, 1, 1), 1.0)
	planner.register_light("b", 1, Color(1, 1, 1), 1.0)
	planner.configure({"max_lights": 1})
	_check(planner.plan()["warnings"].has("light_budget_exceeded"), "lowered light budget warns")

	_fresh(planner)
	planner.register_light("spot", 2, Color(0.4, 0.9, 0.7), 2.0, true, 0.05, 0.1, 1, 24.0, 35.0)
	plan = planner.plan()
	_check(plan["lights"][0]["light_type"] == "spot", "spot type exported")
	_check(plan["lights"][0]["range_m"] == 24.0, "spot range exported")
	_check(plan["lights"][0]["spot_angle_degrees"] == 35.0, "spot angle exported")
	var first: Dictionary = planner.plan()
	var second: Dictionary = planner.plan()
	_check(JSON.stringify(first) == JSON.stringify(second), "plan is deterministic")

	var observation: Dictionary = planner.export_observation("m03-smoke-001", "2026-11-13T12:00:00Z", _provenance())
	_check(observation.get("schema_version", "") == "lighting.v1", "observation exports lighting.v1")
	_check(observation["performance"]["measurement_status"] == "UNAVAILABLE", "observation performance is unavailable")
	_check(observation["shadow_budget"]["atlas_size"] == 4096, "observation shadow budget matches planner")
	_check(observation["lights"].size() == 1, "observation carries registered lights")
	_check(not observation["lights"][0].has("shadow_assigned"), "observation omits planner-only fields")
	var bad_sha := _provenance()
	bad_sha["base_sha"] = "A".repeat(40)
	_check(planner.export_observation("m03-smoke-002", "2026-11-13T12:00:00Z", bad_sha).is_empty(), "invalid SHA rejected")
	var measured := _provenance()
	measured["measurement_status"] = "MEASURED"
	_check(planner.export_observation("m03-smoke-003", "2026-11-13T12:00:00Z", measured).is_empty(), "measured provenance requires evidence")
	measured["evidence_uri"] = "evidence://m03-smoke"
	_check(not planner.export_observation("m03-smoke-004", "2026-11-13T12:00:00Z", measured).is_empty(), "measured provenance with evidence accepted")

	planner.clear()
	_check(planner.plan()["totals"]["lights"] == 0, "clear removes lights")
	_check(planner.plan()["environment"]["glow"] == true, "clear restores default environment")
	planner.configure_environment({"glow": false})
	_check(planner.plan()["environment"]["glow"] == false, "environment override applies")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M03_LIGHTRIG_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M03_LIGHTRIG_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
