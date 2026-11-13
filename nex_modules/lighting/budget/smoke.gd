extends SceneTree

# Headless deterministic smoke for NEX M03-LIGHTBUDGET LightBudgetArbiter.
# godot --headless --path nex_modules/lighting/budget --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _scene(omni: int, shadowed: int, directional: bool, particles: int) -> Dictionary:
	return {
		"omni_lights": omni,
		"shadowed_omni_lights": shadowed,
		"directional_shadow": directional,
		"particle_emitters": particles,
	}


func _step_ids(report: Dictionary) -> Array:
	var ids: Array = []
	for step in report["degradation_steps"]:
		ids.append(step["step_id"])
	return ids


func _run() -> void:
	var packed := load("res://main.tscn") as PackedScene
	_check(packed != null, "main scene loads")
	if packed == null:
		_finish()
		return
	var arbiter = packed.instantiate()
	root.add_child(arbiter)
	await process_frame

	_check(arbiter.configure({}), "default configuration accepted")
	_check(not arbiter.configure({"budget_ms": 0.1}), "budget below floor rejected")
	_check(not arbiter.configure({"budget_ms": 2000.0}), "budget above ceiling rejected")
	_check(not arbiter.configure({"model": {"unknown_key": 1.0}}), "unknown model key rejected")
	_check(not arbiter.configure({"model": {"base_gpu_ms": -1.0}}), "negative coefficient rejected")
	_check(arbiter.configure({"budget_ms": 16.67}), "valid budget accepted")
	_check(arbiter.configure({"budget_ms": 8.33, "model": {"per_omni_light_ms": 0.03}}), "valid model override accepted")
	arbiter.reset_model()
	arbiter.clear()

	var baseline: Dictionary = arbiter.estimate(_scene(0, 0, false, 0))
	_check(baseline["verdict"] == "FIT", "baseline fits default budget")
	_check(is_equal_approx(baseline["projected_gpu_ms"], 0.181), "baseline projection matches S05")
	_check(baseline["breakdown"]["omni_lights_ms"] == 0.0, "baseline has no light cost")

	var lights: Dictionary = arbiter.estimate(_scene(4, 0, false, 0))
	_check(is_equal_approx(lights["projected_gpu_ms"], 0.279), "four omni lights project to S05 cost")
	_check(is_equal_approx(lights["breakdown"]["directional_shadow_ms"], 0.0), "lights-only has no shadow cost")

	var shadows: Dictionary = arbiter.estimate(_scene(4, 4, true, 0))
	_check(is_equal_approx(shadows["projected_gpu_ms"], 0.460), "shadow preset projects to S05 cost")
	_check(is_equal_approx(shadows["breakdown"]["omni_shadows_ms"], 0.081), "omni shadow cost")
	_check(is_equal_approx(shadows["breakdown"]["directional_shadow_ms"], 0.100), "directional shadow cost")
	_check(is_equal_approx(shadows["breakdown"]["interaction_ms"], 0.0), "no interaction without particles")

	var vfx: Dictionary = arbiter.estimate(_scene(0, 0, false, 4))
	_check(is_equal_approx(vfx["projected_gpu_ms"], 0.236), "vfx preset projects to S05 cost")

	var combined: Dictionary = arbiter.estimate(_scene(4, 4, true, 4))
	_check(is_equal_approx(combined["projected_gpu_ms"], 1.194), "combined preset projects to S05 cost")
	_check(is_equal_approx(combined["breakdown"]["interaction_ms"], 0.679), "combined preset includes interaction term")
	var parts: float = (
		float(combined["breakdown"]["base_ms"])
		+ float(combined["breakdown"]["omni_lights_ms"])
		+ float(combined["breakdown"]["directional_shadow_ms"])
		+ float(combined["breakdown"]["omni_shadows_ms"])
		+ float(combined["breakdown"]["particles_ms"])
		+ float(combined["breakdown"]["interaction_ms"])
	)
	_check(is_equal_approx(parts, combined["projected_gpu_ms"]), "breakdown sums to projection")
	_check(combined["limitations"].size() >= 5, "limitations documented")
	_check(String(combined["model_source"]).contains("S05"), "model source references S05")
	_check(JSON.stringify(combined) == JSON.stringify(arbiter.estimate(_scene(4, 4, true, 4))), "estimate is deterministic")
	_check(JSON.stringify(arbiter.get_last_report()) == JSON.stringify(combined), "last report retained")

	arbiter.configure({"budget_ms": 1.0})
	var over: Dictionary = arbiter.estimate(_scene(4, 4, true, 4))
	_check(over["verdict"] == "OVER_BUDGET", "combined preset exceeds one millisecond budget")
	_check(over["headroom_ms"] < 0.0, "over-budget headroom is negative")

	arbiter.configure({"budget_ms": 1.25})
	_check(arbiter.estimate(_scene(4, 4, true, 4))["verdict"] == "TIGHT", "small headroom yields tight verdict")

	_check(arbiter.estimate(_scene(-1, 0, false, 0))["verdict"] == "INVALID_INPUT", "negative omni count is invalid")
	_check(arbiter.estimate(_scene(2, 3, false, 0))["verdict"] == "INVALID_INPUT", "more shadowed lights than lights is invalid")
	_check(arbiter.estimate(_scene(0, 0, false, 65))["verdict"] == "INVALID_INPUT", "particle count above limit is invalid")
	var missing: Dictionary = _scene(0, 0, false, 0)
	missing.erase("directional_shadow")
	_check(arbiter.estimate(missing)["verdict"] == "INVALID_INPUT", "missing scene key is invalid")
	var bad_bool: Dictionary = _scene(0, 0, false, 0)
	bad_bool["directional_shadow"] = 1
	_check(arbiter.estimate(bad_bool)["verdict"] == "INVALID_INPUT", "non-boolean directional flag is invalid")
	_check(arbiter.estimate(_scene(-1, 0, false, 0)).has("reason"), "invalid report carries a reason")

	arbiter.configure({"budget_ms": 8.33})
	var fit_plan: Dictionary = arbiter.arbitrate(_scene(4, 4, true, 4))
	_check(fit_plan["verdict"] == "FIT", "arbitrate baseline verdict")
	_check(fit_plan["degradation_steps"].is_empty(), "fit plan has no degradation steps")
	_check(fit_plan["recommended_step"] == "none", "fit plan recommends no step")

	arbiter.configure({"budget_ms": 1.0})
	var plan: Dictionary = arbiter.arbitrate(_scene(4, 4, true, 4))
	_check(plan["verdict"] == "OVER_BUDGET", "over-budget plan detected")
	_check(plan["degradation_steps"].size() >= 4, "degradation ladder generated")
	_check(_step_ids(plan)[0] == "halve_particle_emitters", "lowest quality cost step comes first")
	_check(_step_ids(plan).has("disable_directional_shadow"), "directional shadow step present")
	_check(_step_ids(plan).has("disable_omni_shadows"), "omni shadow step present")
	_check(_step_ids(plan).has("halve_omni_lights"), "halve lights step present")
	_check(_step_ids(plan).has("disable_omni_lights"), "disable lights step present")
	_check(plan["recommended_step"] != "none", "a fitting step is recommended")
	var recommended: Dictionary = plan["recommended_scene"]
	var recommended_cost: Dictionary = arbiter.estimate(recommended)
	_check(recommended_cost["projected_gpu_ms"] <= 1.0, "recommended scene fits the budget")
	_check(plan["degradation_steps"][0]["quality_cost"] == "low", "particle step is low quality cost")
	_check(plan["degradation_steps"][0].has("fits"), "steps carry a fits flag")
	_check(plan["degradation_steps"][0]["projected_gpu_ms"] < plan["projected_gpu_ms"], "first step reduces projection")

	var no_particles: Dictionary = arbiter.arbitrate(_scene(4, 4, true, 0))
	_check(not _step_ids(no_particles).has("halve_particle_emitters"), "particle step skipped without particles")

	var halved: Dictionary = plan["degradation_steps"][3]
	_check(halved["scene"]["omni_lights"] <= 2, "halved step reduces omni lights")
	_check(halved["scene"]["shadowed_omni_lights"] <= halved["scene"]["omni_lights"], "halved step clamps shadowed lights")

	var invalid_plan: Dictionary = arbiter.arbitrate(_scene(-1, 0, false, 0))
	_check(invalid_plan["verdict"] == "INVALID_INPUT", "invalid arbitrate input is rejected")
	_check(invalid_plan["degradation_steps"].is_empty(), "invalid arbitrate has no steps")

	arbiter.configure({"model": {"base_gpu_ms": 0.5}})
	_check(is_equal_approx(arbiter.estimate(_scene(0, 0, false, 0))["projected_gpu_ms"], 0.5), "model override affects projection")
	arbiter.clear()
	_check(arbiter.budget_ms == 8.33, "clear restores budget")
	_check(is_equal_approx(arbiter.estimate(_scene(0, 0, false, 0))["projected_gpu_ms"], 0.181), "clear restores model")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M03_LIGHTBUDGET_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M03_LIGHTBUDGET_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
