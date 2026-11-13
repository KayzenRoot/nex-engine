extends SceneTree

# Headless deterministic smoke for NEX M07-S01 CanvasPlanner.
# godot --headless --path nex_modules/render2d/canvas --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _eq(values: Array, expected: Array) -> bool:
	if values.size() != expected.size():
		return false
	for index in range(values.size()):
		if str(values[index]) != str(expected[index]):
			return false
	return true


func _fresh(planner) -> void:
	planner.clear()
	planner.configure({})
	planner.register_material("bg", "canvas-texture", 0)
	planner.register_material("glow", "canvas-glow", 1)


func _layer_ids(plan: Dictionary) -> Array:
	var ids: Array = []
	for layer in plan["layers"]:
		ids.append(layer["id"])
	return ids


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
	_check(not planner.configure({"max_layers": 0}), "invalid max layers rejected")
	_check(not planner.configure({"max_draw_calls": 0}), "invalid draw call budget rejected")
	_check(not planner.configure({"max_lights": -1}), "invalid light budget rejected")
	_check(planner.configure({}), "configuration restored")
	_check(planner.register_material("bg", "canvas-texture", 0), "material registered")
	_check(not planner.register_material("bg", "other", 0), "duplicate material rejected")
	_check(not planner.register_material("", "shader", 0), "empty material id rejected")
	_check(not planner.register_material("bad", "", 0), "empty shader rejected")
	_check(not planner.register_material("bad", "shader", 2), "invalid lighting mode rejected")

	_check(planner.register_layer("a", 10, 0, "bg"), "layer registered")
	_check(not planner.register_layer("a", 0, 0, "bg"), "duplicate layer rejected")
	_check(not planner.register_layer("missing", 0, 0, "unknown"), "unknown material rejected")
	_check(not planner.register_layer("badblend", 0, 9, "bg"), "invalid blend rejected")
	_check(not planner.register_layer("badz", 9000, 0, "bg"), "z outside range rejected")
	_check(not planner.register_layer("badscale", 0, 0, "bg", Vector2.ZERO, Vector2.ZERO), "zero scale rejected")
	_check(not planner.register_layer("badpos", 0, 0, "bg", Vector2(INF, 0.0)), "non-finite position rejected")

	_fresh(planner)
	planner.register_layer("z10", 10, 0, "bg")
	planner.register_layer("zminus", -5, 0, "bg")
	planner.register_layer("z0", 0, 0, "bg")
	_check(_layer_ids(planner.plan()) == ["zminus", "z0", "z10"], "layers sorted by z")

	_fresh(planner)
	planner.register_layer("b", 0, 0, "bg")
	planner.register_layer("a", 0, 0, "bg")
	_check(_layer_ids(planner.plan()) == ["a", "b"], "equal z ties by id")

	_fresh(planner)
	planner.register_layer("visible", 0, 0, "bg")
	planner.register_layer("hidden", 1, 0, "bg", Vector2.ZERO, Vector2.ONE, 0.0, false)
	_check(_layer_ids(planner.plan()) == ["visible"], "invisible layer excluded")

	_fresh(planner)
	planner.register_layer("a", 0, 0, "bg")
	planner.register_layer("b", 1, 0, "bg")
	planner.register_layer("c", 2, 0, "bg")
	var plan: Dictionary = planner.plan()
	_check(plan["totals"]["batches"] == 1, "same material/blend batches together")
	_check(plan["totals"]["draw_calls"] == 1, "single batch yields one draw call")
	_check(plan["totals"]["state_changes"] == 0, "single batch has no state change")
	_check(plan["batches"][0]["layer_ids"].size() == 3, "batch keeps all layer ids")

	_fresh(planner)
	planner.register_layer("a", 0, 0, "bg")
	planner.register_layer("b", 1, 0, "glow")
	planner.register_layer("c", 2, 0, "bg")
	plan = planner.plan()
	_check(plan["totals"]["batches"] == 3, "interleaved materials split batches")
	_check(plan["totals"]["state_changes"] == 2, "state changes equal batches minus one")
	_check(plan["totals"]["draw_calls"] == 3, "three batches yield three draw calls")

	_fresh(planner)
	planner.register_layer("a", 0, 0, "bg")
	planner.register_layer("b", 1, 1, "bg")
	_check(planner.plan()["totals"]["batches"] == 2, "different blend modes split batches")

	_fresh(planner)
	planner.register_layer("a", 0, 0, "bg")
	planner.register_particle("hot", 8, true)
	planner.register_particle("cold", 0, false)
	plan = planner.plan()
	_check(plan["totals"]["draw_calls"] == 2, "emitting particle adds a draw call")
	_check(plan["totals"]["emitting_particles"] == 1, "only emitting particles count")
	_check(not planner.register_particle("zero", 0, true), "emitting emitter requires amount")

	_fresh(planner)
	planner.register_layer("a", 0, 0, "glow")
	plan = planner.plan()
	_check(plan["warnings"].has("lighting_without_lights"), "lit layer without lights warns")
	planner.register_light("key", 0, 1.0)
	_check(not planner.plan()["warnings"].has("lighting_without_lights"), "light removes warning")
	_check(planner.plan()["totals"]["lights"] == 1, "light count recorded")
	_check(not planner.register_light("key", 0, 1.0), "duplicate light rejected")
	_check(not planner.register_light("badtype", 2, 1.0), "invalid light type rejected")
	_check(not planner.register_light("badenergy", 0, -1.0), "invalid light energy rejected")

	_fresh(planner)
	planner.configure({"max_lights": 1})
	planner.register_layer("a", 0, 0, "glow")
	planner.register_light("l1", 0, 1.0)
	planner.register_light("l2", 0, 1.0)
	_check(planner.plan()["warnings"].has("light_budget_exceeded"), "light budget warning")

	_fresh(planner)
	planner.configure({"max_draw_calls": 1})
	planner.register_layer("a", 0, 0, "bg")
	planner.register_layer("b", 1, 0, "glow")
	_check(planner.plan()["warnings"].has("draw_call_budget_exceeded"), "draw call budget warning")

	_fresh(planner)
	planner.configure({"max_layers": 2})
	planner.register_layer("a", 0, 0, "bg")
	planner.register_layer("b", 1, 0, "bg")
	_check(not planner.register_layer("c", 2, 0, "bg"), "max layers enforced")

	_fresh(planner)
	planner.register_layer("a", 0, 0, "bg")
	planner.register_layer("b", 1, 0, "bg")
	var first: Dictionary = planner.plan()
	var second: Dictionary = planner.plan()
	_check(JSON.stringify(first) == JSON.stringify(second), "plan is deterministic")
	_check(first["limitations"].size() >= 5, "limitations documented")
	_check(first["layers"][0].has("batch_index"), "layers carry a batch index")

	planner.clear()
	plan = planner.plan()
	_check(plan["totals"]["visible_layers"] == 0, "cleared planner is empty")
	_check(plan["totals"]["draw_calls"] == 0, "cleared planner has no draw calls")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M07_S01_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M07_S01_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
