extends SceneTree

# Headless deterministic smoke for NEX M02-S03 DepthWeave.
# godot --headless --path nex_modules/render3d/depth_composition --rendering-method gl_compatibility --script res://smoke.gd

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


func _run() -> void:
	var packed := load("res://main.tscn") as PackedScene
	_check(packed != null, "main scene loads")
	if packed == null:
		_finish()
		return
	var solver = packed.instantiate()
	root.add_child(solver)
	await process_frame
	_check(solver.configure({}), "default configuration accepted")
	_check(solver.set_camera(Vector3.ZERO, Vector3(0, 0, -1)), "default camera accepted")
	_check(not solver.set_camera(Vector3.ZERO, Vector3.ZERO), "degenerate camera rejected")
	_check(not solver.configure({"projection": "fisheye"}), "invalid projection rejected")
	_check(not solver.configure({"depth_epsilon_m": 0.2, "hysteresis_m": 0.1}), "hysteresis below epsilon rejected")
	_check(not solver.configure({"max_primitives": 0}), "invalid max primitives rejected")
	_check(solver.configure({}), "configuration restored")

	# Opaque/decal front-to-back and alpha back-to-front.
	solver.register_primitive("a", 0, Vector3(0, 0, -5), 0.1)
	solver.register_primitive("b", 0, Vector3(0, 0, -6), 0.1)
	solver.register_primitive("c", 0, Vector3(0, 0, -7), 0.1)
	_check(_eq(solver.plan()["passes"]["opaque"], ["a", "b", "c"]), "opaque front-to-back")
	solver.clear_primitives()
	solver.register_primitive("x", 1, Vector3(0, 0, -5), 0.1)
	solver.register_primitive("y", 1, Vector3(0, 0, -6), 0.1)
	solver.register_primitive("z", 1, Vector3(0, 0, -7), 0.1)
	_check(_eq(solver.plan()["passes"]["alpha"], ["z", "y", "x"]), "alpha back-to-front")

	# Overlays last, decals in the opaque pass, ties by id.
	solver.clear_primitives()
	solver.register_primitive("o2", 2, Vector3.ZERO, 0.1)
	solver.register_primitive("o1", 2, Vector3.ZERO, 0.1)
	solver.register_primitive("d", 3, Vector3(0, 0, -4), 0.1)
	solver.register_primitive("p", 0, Vector3(0, 0, -5), 0.1)
	var plan: Dictionary = solver.plan()
	_check(_eq(plan["passes"]["opaque"], ["d", "p"]), "decal stays in opaque pass")
	_check(_eq(plan["passes"]["overlay"], ["o1", "o2"]), "overlays are last and id-sorted")
	solver.clear_primitives()
	solver.register_primitive("b", 0, Vector3(0, 0, -5), 0.1)
	solver.register_primitive("a", 0, Vector3(0, 0, -5), 0.1)
	_check(_eq(solver.plan()["passes"]["opaque"], ["a", "b"]), "equal depths tie by id")

	# Z-fighting risk is detected and resolution is deterministic.
	solver.clear_primitives()
	solver.register_primitive("f1", 0, Vector3(0, 0, -5), 0.5)
	solver.register_primitive("f2", 0, Vector3(0, 0, -5), 0.5)
	plan = solver.plan()
	_check(plan["z_fight_risks"].size() == 1, "z-fighting risk detected")
	_check(_eq(plan["passes"]["opaque"], ["f1", "f2"]), "z-fighting resolution is deterministic")
	var second: Dictionary = solver.plan()
	_check(_eq(second["passes"]["opaque"], ["f1", "f2"]), "z-fighting order remains stable")
	_check(_eq(second["passes"]["opaque"], plan["passes"]["opaque"]), "repeated plan keeps passes")

	# Hysteresis stabilizes small camera-induced depth inversions.
	solver.clear_primitives()
	solver.register_primitive("A", 0, Vector3(0, 0, -5), 0.1)
	solver.register_primitive("B", 0, Vector3(-0.2, 0, -5), 0.1)
	solver.set_camera(Vector3.ZERO, Vector3(0, 0, -1))
	_check(_eq(solver.plan()["passes"]["opaque"], ["A", "B"]), "initial tie order by id")
	solver.set_camera(Vector3.ZERO, Vector3(0.02, 0, -1))
	_check(_eq(solver.plan()["passes"]["opaque"], ["A", "B"]), "small depth inversion is stabilized")
	solver.set_camera(Vector3.ZERO, Vector3(0.2, 0, -1))
	_check(_eq(solver.plan()["passes"]["opaque"], ["B", "A"]), "large depth inversion changes order")

	# Slow camera steps remain stable; a fast step flips.
	solver.clear_primitives()
	solver.register_primitive("A", 0, Vector3(0, 0, -5), 0.1)
	solver.register_primitive("B", 0, Vector3(-0.2, 0, -5), 0.1)
	solver.set_camera(Vector3.ZERO, Vector3(0, 0, -1))
	solver.plan()
	var stable := true
	for x in [0.005, 0.01, 0.015, 0.02]:
		solver.set_camera(Vector3.ZERO, Vector3(x, 0, -1))
		if not _eq(solver.plan()["passes"]["opaque"], ["A", "B"]):
			stable = false
	_check(stable, "slow camera steps remain stable")
	solver.set_camera(Vector3.ZERO, Vector3(0.3, 0, -1))
	_check(_eq(solver.plan()["passes"]["opaque"], ["B", "A"]), "fast camera step flips order")

	# Alpha in front of a gameplay-critical primitive is flagged.
	solver.clear_primitives()
	solver.register_primitive("critical", 0, Vector3(0, 0, -5), 0.1, true, false)
	solver.register_primitive("front", 1, Vector3(0, 0, -4), 0.1)
	_check(solver.plan()["alpha_over_critical"].has("front"), "alpha over critical flagged")
	solver.clear_primitives()
	solver.register_primitive("critical", 0, Vector3(0, 0, -5), 0.1, true, false)
	solver.register_primitive("back", 1, Vector3(0, 0, -6), 0.1)
	_check(not solver.plan()["alpha_over_critical"].has("back"), "alpha behind critical not flagged")

	# Overlay that can hide gameplay is reported.
	solver.clear_primitives()
	solver.register_primitive("critical", 0, Vector3(0, 0, -5), 0.1, true, false)
	solver.register_primitive("hud", 2, Vector3.ZERO, 0.1, false, true)
	_check(solver.plan()["overlay_gameplay_conflicts"].has("hud"), "overlay gameplay conflict flagged")
	solver.clear_primitives()
	solver.register_primitive("critical", 0, Vector3(0, 0, -5), 0.1, true, false)
	solver.register_primitive("hud", 2, Vector3.ZERO, 0.1, false, false)
	_check(solver.plan()["overlay_gameplay_conflicts"].is_empty(), "safe overlay not flagged")

	# Projection is recorded and ordering is consistent.
	solver.clear_primitives()
	solver.register_primitive("a", 0, Vector3(0, 0, -5), 0.1)
	solver.register_primitive("b", 0, Vector3(0, 0, -6), 0.1)
	_check(solver.configure({"projection": "orthographic"}), "orthographic configuration accepted")
	plan = solver.plan()
	_check(plan["projection"] == "orthographic", "projection recorded in plan")
	_check(_eq(plan["passes"]["opaque"], ["a", "b"]), "orthographic ordering consistent")

	# Validation, limits and clearing.
	_check(not solver.register_primitive("a", 0, Vector3.ZERO, 0.1), "duplicate primitive rejected")
	_check(not solver.register_primitive("neg", 0, Vector3.ZERO, -1.0), "negative radius rejected")
	_check(not solver.register_primitive("bad", 9, Vector3.ZERO, 0.1), "invalid kind rejected")
	_check(solver.configure({"max_primitives": 2}), "small limit configuration accepted")
	solver.clear_primitives()
	solver.register_primitive("one", 0, Vector3.ZERO, 0.1)
	solver.register_primitive("two", 0, Vector3.ZERO, 0.1)
	_check(not solver.register_primitive("three", 0, Vector3.ZERO, 0.1), "max primitives enforced")
	solver.clear_primitives()
	plan = solver.plan()
	_check(plan["passes"]["opaque"].is_empty() and plan["depths"].is_empty(), "cleared solver plans empty")
	_check(plan["limitations"].size() >= 5, "limitations documented in plan")
	_check(plan["camera"]["position"].size() == 3, "camera position serialized")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M02_S03_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M02_S03_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
