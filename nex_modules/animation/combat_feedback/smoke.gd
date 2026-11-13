extends SceneTree

# Headless deterministic smoke for NEX M10-FEEDBACK FeedbackPlanner.
# godot --headless --path nex_modules/animation/combat_feedback --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _fresh(planner, options := {}) -> void:
	planner.clear()
	planner.configure({
		"max_hit_stop_ms": options.get("max_hit_stop_ms", 80),
		"max_shake_amplitude": options.get("max_shake", 0.8),
		"max_concurrent_channels": options.get("max_concurrent", 5),
		"max_total_channels": options.get("max_total", 8),
	})
	planner.set_attack("slash", [
		{"phase": 0, "duration_ms": 120},
		{"phase": 1, "duration_ms": 80},
		{"phase": 2, "duration_ms": 200},
	])
	planner.register_hit_event("hit-01", options.get("event1_at", 150), "goblin-01", options.get("event1_damage", 40), false, 0)
	planner.register_hit_event("hit-02", options.get("event2_at", 160), "goblin-02", options.get("event2_damage", 120), options.get("event2_critical", true), 0)
	planner.register_channel("hit-stop-01", 0, 150, options.get("hit_stop_duration", 60), 1.0, 10, options.get("hit_stop_event", "hit-01"))
	planner.register_channel("shake-01", 1, 150, 120, options.get("shake_intensity", 0.4), 8, "hit-02")
	planner.register_channel("flash-01", 2, 150, 90, 0.6, 7, "hit-02")
	planner.register_channel("number-01", 4, 150, options.get("number_duration", 600), 1.0, 5, "hit-02", "goblin-02")
	planner.register_channel("recoil-01", 3, 150, 100, 0.5, 6, "hit-01")


func _has(report: Dictionary, code: String) -> bool:
	for finding in report["conflicts"]:
		if finding["code"] == code:
			return true
	return false


func _provenance() -> Dictionary:
	return {
		"base_sha": "d".repeat(40),
		"head_sha": "e".repeat(40),
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
	_check(not planner.configure({"max_hit_stop_ms": 501}), "hit-stop budget above limit rejected")
	_check(not planner.configure({"max_shake_amplitude": 2.5}), "shake budget above limit rejected")
	_check(not planner.configure({"max_concurrent_channels": 0}), "zero concurrency budget rejected")
	_check(not planner.configure({"max_total_channels": 33}), "total channel budget above limit rejected")
	_check(planner.configure({"max_hit_stop_ms": 80, "max_shake_amplitude": 0.8, "max_concurrent_channels": 5, "max_total_channels": 8}), "valid configuration accepted")

	_check(planner.set_attack("slash", [{"phase": 0, "duration_ms": 120}, {"phase": 1, "duration_ms": 80}, {"phase": 2, "duration_ms": 200}]), "attack accepted")
	_check(not planner.set_attack("Slash", [{"phase": 1, "duration_ms": 100}]), "invalid attack id rejected")
	_check(not planner.set_attack("slash", [{"phase": 0, "duration_ms": 100}]), "attack without active phase rejected")
	_check(not planner.set_attack("slash", [{"phase": 0, "duration_ms": 100}, {"phase": 0, "duration_ms": 100}, {"phase": 1, "duration_ms": 100}]), "duplicate phase rejected")
	_check(not planner.set_attack("slash", [{"phase": 1, "duration_ms": 10000}, {"phase": 2, "duration_ms": 100}]), "long attack rejected")
	_check(planner.set_attack("slash", [{"phase": 0, "duration_ms": 120}, {"phase": 1, "duration_ms": 80}, {"phase": 2, "duration_ms": 200}]), "attack restored")

	_check(planner.register_hit_event("hit-01", 150, "goblin-01", 40, false, 0), "hit event registered")
	_check(not planner.register_hit_event("hit-01", 150, "goblin-01", 40, false, 0), "duplicate event rejected")
	_check(not planner.register_hit_event("bad time", 150, "goblin-01", 40, false, 0), "invalid event id rejected")
	_check(not planner.register_hit_event("hit-bad", 10001, "goblin-01", 40, false, 0), "event time above limit rejected")
	_check(not planner.register_hit_event("hit-bad", 150, "Goblin", 40, false, 0), "invalid target rejected")
	_check(not planner.register_hit_event("hit-bad", 150, "goblin-01", -1, false, 0), "negative damage rejected")
	_check(not planner.register_hit_event("hit-bad", 150, "goblin-01", 40, false, 6), "invalid element rejected")

	_check(planner.register_channel("hit-stop-01", 0, 150, 60, 1.0, 10, "hit-01"), "hit-stop channel registered")
	_check(not planner.register_channel("hit-stop-01", 0, 150, 60, 1.0, 10, "hit-01"), "duplicate channel rejected")
	_check(not planner.register_channel("bad channel", 0, 150, 60, 1.0, 10, "hit-01"), "invalid channel id rejected")
	_check(not planner.register_channel("bad-type", 5, 150, 60, 1.0, 10, "hit-01"), "invalid channel type rejected")
	_check(not planner.register_channel("bad-start", 0, 10001, 60, 1.0, 10, "hit-01"), "channel start above limit rejected")
	_check(not planner.register_channel("bad-duration", 0, 150, 5001, 1.0, 10, "hit-01"), "channel duration above limit rejected")
	_check(not planner.register_channel("bad-intensity", 0, 150, 60, 1.5, 10, "hit-01"), "channel intensity above one rejected")
	_check(not planner.register_channel("bad-priority", 0, 150, 60, 1.0, 11, "hit-01"), "channel priority above limit rejected")

	_fresh(planner)
	var plan: Dictionary = planner.plan()
	_check(plan["verdict"] == "SAFE_CONFIG_HEURISTIC", "safe fixture verdict")
	_check(plan["schema_version"] == "feedback.plan.v1", "plan schema version")
	_check(plan["attack"]["total_duration_ms"] == 400, "attack duration")
	_check(plan["attack"]["phases"].size() == 3, "attack phases exported")
	_check(plan["timeline"].size() == 5, "timeline carries all channels")
	_check(plan["timeline"][0]["start_ms"] == 150, "timeline sorted by start")
	_check(plan["metrics"]["total_channels"] == 5, "total channels metric")
	_check(plan["metrics"]["peak_concurrency"] == 5, "peak concurrency metric")
	_check(plan["metrics"]["total_hit_stop_ms"] == 60, "hit-stop total metric")
	_check(is_equal_approx(plan["metrics"]["max_shake_intensity"], 0.4), "shake metric")
	_check(plan["metrics"]["damage_numbers"] == 1, "damage number metric")
	_check(plan["summary"]["high"] == 0, "safe fixture has no high conflicts")
	_check(plan["limitations"].size() >= 5, "limitations documented")
	_check(JSON.stringify(plan) == JSON.stringify(planner.plan()), "plan is deterministic")
	_check(JSON.stringify(planner.get_last_plan()) == JSON.stringify(plan), "last plan retained")

	_fresh(planner, {"event1_at": 500})
	_check(_has(planner.plan(), "event_outside_attack"), "event outside attack flagged")

	_fresh(planner, {"event2_damage": 0, "event2_critical": true})
	_check(_has(planner.plan(), "critical_without_damage"), "critical without damage flagged")

	_fresh(planner, {"number_duration": 5000})
	_check(_has(planner.plan(), "channel_outside_window"), "channel outside window flagged")

	_fresh(planner, {"hit_stop_event": "missing"})
	_check(_has(planner.plan(), "dangling_event"), "dangling event reference flagged")

	_fresh(planner, {"event2_damage": 0, "event2_critical": false})
	_check(_has(planner.plan(), "damage_number_without_damage"), "damage number without damage flagged")

	_fresh(planner, {"hit_stop_duration": 120})
	_check(_has(planner.plan(), "hit_stop_over_budget"), "hit-stop over budget flagged")

	_fresh(planner, {"shake_intensity": 1.0})
	_check(_has(planner.plan(), "shake_over_budget"), "shake over budget flagged")

	_fresh(planner, {"max_total": 2})
	_check(_has(planner.plan(), "total_channels_over_budget"), "total channels over budget flagged")

	_fresh(planner, {"max_concurrent": 2})
	_check(_has(planner.plan(), "concurrency_over_budget"), "concurrency over budget flagged")

	_fresh(planner)
	planner.clear()
	_check(planner.plan()["verdict"] == "INVALID_INPUT", "empty planner is invalid")

	_fresh(planner)
	planner.clear()
	planner.set_attack("slash", [{"phase": 1, "duration_ms": 100}])
	_check(planner.plan()["verdict"] == "INVALID_INPUT", "missing channels is invalid")

	_fresh(planner)
	var observation: Dictionary = planner.export_observation("m10-smoke-001", "2026-11-13T12:00:00Z", _provenance())
	_check(observation.get("schema_version", "") == "feedback.v1", "observation exports feedback.v1")
	_check(observation["performance"]["measurement_status"] == "UNAVAILABLE", "observation performance is unavailable")
	_check(observation["feedback_channels"].size() == 5, "observation carries all channels")
	_check(observation["attack"]["phases"][0]["phase"] == "anticipation", "observation phase vocabulary")
	_check(not observation["feedback_channels"][0].has("end_ms"), "observation omits planner-only fields")
	_check(observation["budget"]["max_hit_stop_ms"] == 80, "observation budget exported")

	_fresh(planner, {"hit_stop_duration": 120})
	_check(planner.export_observation("m10-smoke-002", "2026-11-13T12:00:00Z", _provenance()).is_empty(), "conflicting plan is not exported")

	_fresh(planner)
	var bad_sha := _provenance()
	bad_sha["base_sha"] = "D".repeat(40)
	_check(planner.export_observation("m10-smoke-003", "2026-11-13T12:00:00Z", bad_sha).is_empty(), "invalid SHA rejected")
	var measured := _provenance()
	measured["measurement_status"] = "MEASURED"
	_check(planner.export_observation("m10-smoke-004", "2026-11-13T12:00:00Z", measured).is_empty(), "measured provenance requires evidence")
	measured["evidence_uri"] = "evidence://m10-smoke"
	_check(not planner.export_observation("m10-smoke-005", "2026-11-13T12:00:00Z", measured).is_empty(), "measured provenance with evidence accepted")

	planner.clear()
	_check(planner.max_hit_stop_ms == 80 and planner.max_total_channels == 8, "clear restores defaults")
	_check(planner.plan()["verdict"] == "INVALID_INPUT", "cleared planner is invalid")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M10_FEEDBACK_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M10_FEEDBACK_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
