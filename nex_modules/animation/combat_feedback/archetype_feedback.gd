extends SceneTree

# NEX M10 archetype feedback: feeds the committed M05 FX budget dataset to the
# integrated FeedbackPlanner. Planning only: no animation, camera, shader,
# scene or renderer is created.
# godot --headless --path nex_modules/animation/combat_feedback --script res://archetype_feedback.gd

const PLANNER := preload("res://feedback_planner.gd")
const DATASET_ENV := "NEX_M05_DATASET_PATH"
const OUTPUT_ENV := "NEX_M10_FEEDBACK_OUTPUT"
const SOURCE_SHA := "91e6c15794662b3502244c2d03879b8dbb9980dd"
const DATASET_URI := "nex_modules/vfx/fxbudget/evidence/fx-budget-dataset-2026-11-15.json"
const ELEMENT_IDS := {"fire": 0, "ice": 1, "lightning": 2, "arcane": 3, "nature": 4, "physical": 5}
const PHASE_IDS := {"cast": 0, "travel": 1, "impact": 1, "linger": 2}


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	print("M10_ARCHETYPE_FEEDBACK_FAIL " + message)
	quit(2)


func _phase_durations(spell: Dictionary) -> Dictionary:
	var durations := {0: 0, 1: 0, 2: 0}
	for phase in spell["phases"]:
		var mapped: int = PHASE_IDS[String(phase["phase"])]
		durations[mapped] += int(phase["duration_ms"])
	return durations


func _impact_damage(spell: Dictionary) -> int:
	var amount := 0
	for phase in spell["phases"]:
		if String(phase["phase"]) != "impact":
			continue
		for emitter in phase["emitters"]:
			if String(emitter["kind"]) in ["particles", "trail", "beam"]:
				amount += int(emitter["amount"])
	return maxi(1, amount / 4)


func _channel(planner, spell_id: String, suffix: String, channel: int, start_ms: int,
		duration_ms: int, intensity: float, priority: int, event_id: String) -> bool:
	return planner.register_channel(suffix + "-" + spell_id, channel, start_ms, duration_ms,
		intensity, priority, event_id, "target-01")


func _plan_spell(spell: Dictionary) -> Dictionary:
	var spell_id := String(spell["spell_id"])
	var planner = PLANNER.new()
	root.add_child(planner)
	planner.configure({})
	var durations := _phase_durations(spell)
	var phases: Array = []
	for key in [0, 1, 2]:
		if int(durations[key]) > 0:
			phases.append({"phase": key, "duration_ms": int(durations[key])})
	if not planner.set_attack(spell_id, phases):
		_fail(spell_id + ": " + planner.last_error)
		return {}
	var damage := _impact_damage(spell)
	var at_ms := int(durations[0]) + int(durations[1])
	var event_id := "hit-" + spell_id
	if not planner.register_hit_event(event_id, at_ms, "target-01", damage, damage >= 128,
			ELEMENT_IDS[String(spell["element"])]):
		_fail(spell_id + ": " + planner.last_error)
		return {}
	var hit_stop := clampi(damage / 20, 20, 80)
	var shake := minf(0.8, 0.2 + float(damage) / 2000.0)
	var registered := [
		_channel(planner, spell_id, "hitstop", 0, at_ms, hit_stop, 0.5, 5, event_id),
		_channel(planner, spell_id, "shake", 1, at_ms, 200, shake, 4, event_id),
		_channel(planner, spell_id, "flash", 2, at_ms, 120, 0.6, 3, event_id),
		_channel(planner, spell_id, "recoil", 3, at_ms, 150, 0.4, 2, event_id),
		_channel(planner, spell_id, "damage", 4, at_ms, 400, 0.3, 1, event_id),
	]
	for ok in registered:
		if not ok:
			_fail(spell_id + ": " + planner.last_error)
			return {}
	var report: Dictionary = planner.plan()
	planner.queue_free()
	return {
		"spell_id": spell_id,
		"element": String(spell["element"]),
		"damage": damage,
		"critical": damage >= 128,
		"report": report,
	}


func _summary(plans: Array) -> Dictionary:
	var verdicts: Array = []
	var total_channels := 0
	var peak := 0
	var hit_stop := 0
	var shake := 0.0
	var summary := {"high": 0, "medium": 0, "low": 0, "info": 0}
	for plan in plans:
		var report: Dictionary = plan["report"]
		verdicts.append(String(report["verdict"]))
		total_channels += int(report["metrics"]["total_channels"])
		peak = maxi(peak, int(report["metrics"]["peak_concurrency"]))
		hit_stop += int(report["metrics"]["total_hit_stop_ms"])
		shake = maxf(shake, float(report["metrics"]["max_shake_intensity"]))
		for key in summary:
			summary[key] += int(report["summary"][key])
	return {
		"spells": plans.size(),
		"verdicts": verdicts,
		"total_channels": total_channels,
		"max_peak_concurrency": peak,
		"total_hit_stop_ms": hit_stop,
		"max_shake_intensity": snappedf(shake, 0.001),
		"conflicts": summary,
	}


func _run() -> void:
	var dataset_path := OS.get_environment(DATASET_ENV).strip_edges()
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if dataset_path.is_empty() or output.is_empty():
		_fail("missing dataset or output path")
		return
	var text := FileAccess.get_file_as_string(dataset_path)
	if text.is_empty():
		_fail("cannot read dataset")
		return
	var dataset = JSON.parse_string(text)
	if not dataset is Dictionary or String(dataset.get("schema_version", "")) != "fx_budget_dataset.v1":
		_fail("dataset is not fx_budget_dataset.v1")
		return
	var archetypes: Array = []
	for archetype in dataset.get("archetypes", []):
		var plans: Array = []
		for spell in archetype["spells"]:
			var plan := _plan_spell(spell)
			if plan.is_empty():
				return
			plans.append(plan)
		archetypes.append({
			"archetype_id": String(archetype["archetype_id"]),
			"label": String(archetype["label"]),
			"spells": plans,
			"summary": _summary(plans),
		})
	var document := {
		"schema_version": "m10_archetype_feedback_run.v1",
		"source_sha": SOURCE_SHA,
		"dataset_uri": DATASET_URI,
		"dataset_sha256": FileAccess.get_sha256(dataset_path),
		"archetypes": archetypes,
		"limitations": [
			"planning only; no animation, camera, shader, scene or renderer is created",
			"damage is derived from impact particle amounts as reference data, not gameplay balance",
			"each spell is planned independently; archetype totals are aggregates, not a simultaneous rotation",
			"no FPS, frame-time, game-feel or visual-quality claim",
		],
	}
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		_fail("cannot write output")
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	print("M10_ARCHETYPE_FEEDBACK_OK %d archetypes" % archetypes.size())
	quit(0)
