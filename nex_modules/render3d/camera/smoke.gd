extends SceneTree

# Headless deterministic smoke for the NEX M02-S01 isometric camera rig.
# godot --headless --path nex_modules/render3d/camera --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _run() -> void:
	root.size = Vector2i(1280, 720)
	await process_frame
	var packed := load("res://main.tscn") as PackedScene
	_check(packed != null, "main scene loads")
	if packed == null:
		_finish()
		return
	var rig = packed.instantiate()
	_check(rig != null, "scene instantiates")
	if rig == null:
		_finish()
		return
	root.add_child(rig)
	await process_frame
	rig.set_viewport_size(Vector2i(1280, 720))

	_check(rig.configure({}), "default configuration accepted")
	_check(rig.last_error == "", "no error on default configuration")
	_check(not rig.configure({"far_clip_m": 0.05}), "inverted clip planes rejected")
	_check(not rig.configure({"projection": "fisheye"}), "unknown projection rejected")
	_check(rig.configure({}), "configuration restored")

	rig.set_focus(Vector3(5.0, 0.0, 5.0))
	var state: Dictionary = rig.get_state()
	_check(_approx(state["target_m"], [5.0, 0.0, 5.0]), "focus reflected in state")
	_check(str(state["projection"]) == "isometric_perspective", "perspective projection in state")
	_check(rig.camera.projection == Camera3D.PROJECTION_PERSPECTIVE, "camera uses perspective")
	_check(absf(rig.camera.fov - 40.0) < 0.01, "vertical FOV applied")
	_check(absf(rig.camera.position.distance_to(Vector3(5.0, 0.0, 5.0)) - 18.0) < 0.01, "camera distance matches rig")
	_check(state["viewport"]["unit"] == "px", "viewport unit is px")
	_check(state["stability"].has("snap_to_pixel"), "stability block present")

	var point := Vector3(2.0, 0.0, -1.0)
	var screen: Vector2 = rig.world_to_screen(point)
	var roundtrip: Vector3 = rig.screen_to_world(screen, 0.0)
	_check(roundtrip.distance_to(point) < 0.05, "world-screen-world roundtrip")

	for aspect in [16.0 / 9.0, 4.0 / 3.0, 21.0 / 9.0]:
		var extents: Dictionary = rig.visible_world_extents(aspect)
		var ratio: float = float(extents["half_width_m"]) / float(extents["half_height_m"])
		_check(absf(ratio - aspect) < 0.0001, "aspect %.3f preserved" % aspect)

	_check(rig.visible_margin([Vector3(0, 0, 0), Vector3(3, 0, 3)])["all_inside"], "near actors inside frame")
	_check(not rig.visible_margin([Vector3(100, 0, 0)])["all_inside"], "distant actor outside frame")

	rig.set_zoom(1.0)
	rig.configure({"zoom_min": 0.5, "zoom_max": 2.0})
	rig.zoom_by(100.0)
	_check(absf(rig.zoom - 2.0) < 0.0001, "zoom clamped to maximum")
	rig.zoom_by(0.0001)
	_check(absf(rig.zoom - 0.5) < 0.0001, "zoom clamped to minimum")
	rig.set_zoom(1.0)

	rig.set_focus(Vector3.ZERO)
	rig.update_follow(Vector3(0.5, 0.0, 0.0), 0.0166667)
	_check(rig.focus.length() < 0.0001, "dead zone holds small target motion")
	rig.update_follow(Vector3(20.0, 0.0, 0.0), 0.0166667)
	_check(rig.focus.x > 0.0 and rig.focus.x < 20.0, "dead zone moves focus toward large motion")

	rig.set_focus(Vector3.ZERO)
	var previous_distance := 40.0
	var monotonic := true
	for step in range(180):
		rig.update_follow(Vector3(40.0, 0.0, 0.0), 0.0166667)
		var distance: float = rig.focus.distance_to(Vector3(40.0, 0.0, 0.0))
		if distance > previous_distance + 0.00001:
			monotonic = false
		previous_distance = distance
	_check(monotonic, "fast transition has no overshoot")
	_check(rig.focus.x > 35.0, "fast transition converges")

	rig.set_focus(Vector3(100.0, 0.0, 100.0))
	_check(_approx(rig.get_state()["target_m"], [50.0, 0.0, 50.0]), "focus clamped to bounds")

	_check(rig.configure({"projection": "orthographic", "ortho_size_m": 10.0, "zoom_min": 0.5, "zoom_max": 2.0}), "orthographic configuration accepted")
	rig.set_zoom(1.0)
	var ortho_state: Dictionary = rig.get_state()
	_check(str(ortho_state["projection"]) == "isometric_orthographic", "orthographic projection in state")
	_check(absf(float(ortho_state["ortho_size_m"]) - 10.0) < 0.0001, "orthographic size in state")
	_check(rig.camera.projection == Camera3D.PROJECTION_ORTHOGONAL, "camera uses orthographic projection")

	rig.configure({"projection": "perspective"})
	rig.set_zoom(1.0)
	var events := [
		{"target": Vector3(3, 0, 3)},
		{"target": Vector3(6, 0, 1), "zoom": 1.2},
		{"target": Vector3(-2, 0, 4)},
	]
	var first: Array = rig.replay(events)
	var second: Array = rig.replay(events)
	_check(JSON.stringify(first) == JSON.stringify(second), "deterministic replay")

	_finish()


func _approx(values: Array, expected: Array, tolerance := 0.001) -> bool:
	if values.size() != expected.size():
		return false
	for index in range(values.size()):
		if absf(float(values[index]) - float(expected[index])) > tolerance:
			return false
	return true


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M02_S01_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M02_S01_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
