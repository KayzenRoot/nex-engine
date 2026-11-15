extends SceneTree

# NEX M05 FX budget dataset: three deterministic encounter archetypes analyzed
# by the integrated FXBudgetPlanner. Data only: no particle, emitter, light,
# decal or renderer is created.
# godot --headless --path nex_modules/vfx/fxbudget --script res://dataset.gd

const OUTPUT_ENV := "NEX_FX_DATASET_OUTPUT"
const SOURCE_SHA := "99437b22e94a6494eaef801872bb8fd0c79c0f1a"

var failures: Array[String] = []


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	print("FX_DATASET_FAIL " + message)
	quit(2)


func _emitter(emitter_id: String, kind: String, amount: int, gpu := false, light_bridge := false) -> Dictionary:
	return {
		"emitter_id": emitter_id, "kind": kind, "amount": amount,
		"lifetime_ms": 500, "gpu": gpu, "light_bridge": light_bridge,
	}


func _authority() -> Dictionary:
	return {"damage_owner": "gameplay", "hit_detection": "gameplay", "cancel_on_death": true}


func _spell(spell_id: String, element: String, phases: Array, max_decals: int) -> Dictionary:
	return {
		"spell_id": spell_id, "element": element, "phases": phases,
		"gameplay_authority": _authority(),
		"decal_policy": {"max_decals": max_decals, "fade_ms": 3000},
	}


func _ember_bolt() -> Dictionary:
	return _spell("ember-bolt", "fire", [
		{"phase": "cast", "duration_ms": 300, "emitters": [_emitter("cast-spark", "particles", 64, true)]},
		{"phase": "travel", "duration_ms": 200, "emitters": [_emitter("travel-trail", "trail", 32)]},
		{"phase": "impact", "duration_ms": 150, "emitters": [
			_emitter("impact-burst", "particles", 128, true),
			_emitter("impact-light", "light", 1, false, true),
		]},
		{"phase": "linger", "duration_ms": 4000, "emitters": [_emitter("linger-decal", "decal", 1)]},
	], 8)


func _frost_nova() -> Dictionary:
	return _spell("frost-nova", "ice", [
		{"phase": "impact", "duration_ms": 1500, "emitters": [_emitter("nova-burst", "particles", 256, true)]},
		{"phase": "linger", "duration_ms": 3000, "emitters": [_emitter("nova-decal", "decal", 2)]},
	], 4)


func _storm_lance() -> Dictionary:
	return _spell("storm-lance", "lightning", [
		{"phase": "cast", "duration_ms": 400, "emitters": [_emitter("charge-arc", "beam", 48, true)]},
		{"phase": "impact", "duration_ms": 200, "emitters": [
			_emitter("lance-burst", "particles", 512, true),
			_emitter("lance-light", "light", 1, false, true),
		]},
		{"phase": "linger", "duration_ms": 2000, "emitters": [_emitter("lance-scorch", "decal", 2)]},
	], 6)


func _meteor_storm() -> Dictionary:
	return _spell("meteor-storm", "fire", [
		{"phase": "cast", "duration_ms": 900, "emitters": [_emitter("meteor-charge", "particles", 400, true)]},
		{"phase": "impact", "duration_ms": 600, "emitters": [
			_emitter("meteor-burst", "particles", 900, true),
			_emitter("meteor-light", "light", 1, false, true),
		]},
		{"phase": "linger", "duration_ms": 5000, "emitters": [_emitter("meteor-scorch", "decal", 3)]},
	], 8)


func _grave_bind() -> Dictionary:
	return _spell("grave-bind", "nature", [
		{"phase": "impact", "duration_ms": 800, "emitters": [
			_emitter("bind-roots", "particles", 300, true),
			_emitter("bind-mark", "decal", 2),
		]},
		{"phase": "linger", "duration_ms": 2500, "emitters": [_emitter("bind-motes", "particles", 100)]},
	], 4)


func _archetypes() -> Array:
	return [
		{
			"archetype_id": "skirmish",
			"label": "three-trash-pack",
			"budget": {"max_emitters": 32, "max_particles": 800, "max_gpu_emitters": 8, "max_decals": 32},
			"spells": [_ember_bolt(), _frost_nova()],
		},
		{
			"archetype_id": "elite",
			"label": "elite-with-adds",
			"budget": {"max_emitters": 16, "max_particles": 1100, "max_gpu_emitters": 8, "max_decals": 16},
			"spells": [_ember_bolt(), _frost_nova(), _storm_lance()],
		},
		{
			"archetype_id": "boss",
			"label": "boss-with-adds",
			"budget": {"max_emitters": 24, "max_particles": 2000, "max_gpu_emitters": 12, "max_decals": 24},
			"spells": [_ember_bolt(), _frost_nova(), _storm_lance(), _meteor_storm(), _grave_bind()],
		},
	]


func _run() -> void:
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if output.is_empty():
		_fail("missing output path")
		return
	var planner = preload("res://fx_budget_planner.gd").new()
	root.add_child(planner)
	var results: Array = []
	for archetype in _archetypes():
		if not planner.configure(archetype["budget"]):
			_fail(archetype["archetype_id"] + ": " + planner.last_error)
			return
		var report: Dictionary = planner.analyze(archetype["spells"])
		if String(report.get("verdict", "")) == "INVALID_INPUT":
			_fail(archetype["archetype_id"] + ": " + String(report.get("error", "invalid input")))
			return
		results.append({
			"archetype_id": archetype["archetype_id"],
			"label": archetype["label"],
			"budget": archetype["budget"],
			"spell_count": archetype["spells"].size(),
			"report": report,
		})
	var document := {
		"schema_version": "fx_budget_dataset.v1",
		"source_sha": SOURCE_SHA,
		"godot_version": "4.7.2-stable",
		"archetypes": results,
		"limitations": [
			"planning only; no particle, emitter, light, decal or renderer is created",
			"budgets are reference values, not measured hardware limits",
			"no FPS, frame-time, overdraw or visual-quality claim",
		],
	}
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		_fail("cannot write output")
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	print("FX_DATASET_OK %d archetypes" % results.size())
	quit(0)
