extends SceneTree

# NEX M02-S01 camera math probe: 3D<->screen round trip, aspect extents and a
# deterministic fast-follow replay. No rendering, no screenshot.
# godot --headless --path nex_bench --script res://scenes/m02_camera/camera_math.gd

const RIG := preload("res://scenes/m02_camera/camera_rig.gd")
const OUTPUT_ENV := "NEX_M02_CAMERA_MATH_OUTPUT"
const SOURCE_SHA := "fa1adae7ab67e38c2556d126627006c338e2e8f4"


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	print("M02_CAMERA_MATH_FAIL " + message)
	quit(2)


func _run() -> void:
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if output.is_empty():
		_fail("missing output path")
		return
	var rig = RIG.new()
	root.add_child(rig)
	rig.set_viewport_size(Vector2i(1920, 1080))
	if not rig.configure({
		"projection": "perspective",
		"yaw_deg": 45.0,
		"pitch_deg": -35.264,
		"distance_m": 18.0,
		"vertical_fov_deg": 40.0,
	}):
		_fail("configure: " + rig.last_error)
		return
	rig.set_focus(Vector3.ZERO)
	await process_frame
	var points := [
		Vector3(0.0, 0.0, 0.0),
		Vector3(3.0, 0.0, -2.0),
		Vector3(-4.0, 0.0, 1.5),
		Vector3(0.0, 0.0, 6.0),
	]
	var max_error := 0.0
	for point in points:
		var screen := rig.world_to_screen(point)
		var world := rig.screen_to_world(screen, 0.0)
		max_error = maxf(max_error, (world - point).length())
	var extents := {}
	for aspect in [16.0 / 9.0, 16.0 / 10.0, 21.0 / 9.0, 4.0 / 3.0]:
		extents["%.4f" % aspect] = rig.visible_world_extents(aspect)
	var events: Array = []
	for index in range(30):
		events.append({"target": [float(index % 6) * 1.5, 0.0, float(index % 4) * 1.2]})
	var states: Array = rig.replay(events, 0.0166667, Vector3.ZERO, 1.0)
	var max_displacement := 0.0
	var previous := Vector2.ZERO
	for index in range(states.size()):
		var focus: Array = states[index]["focus_m"]
		var screen := rig.world_to_screen(Vector3(focus[0], focus[1], focus[2]))
		if index > 0:
			max_displacement = maxf(max_displacement, screen.distance_to(previous))
		previous = screen
	var document := {
		"schema_version": "m02_camera_math.v1",
		"source_sha": SOURCE_SHA,
		"viewport_px": [1920, 1080],
		"projection": "perspective",
		"round_trip_max_error_m": snappedf(max_error, 0.000001),
		"aspect_extents": extents,
		"fast_follow_max_screen_step_px": snappedf(max_displacement, 0.001),
		"fast_follow_states": states.size(),
		"verdict": "CAMERA_MATH_CONSISTENT" if max_error < 0.01 and max_displacement < 250.0 else "CAMERA_MATH_REVIEW",
		"limitations": [
			"round trip uses the y=0 plane; vertical points are not covered",
			"fast follow is deterministic and headless, not a perceptual test",
		],
	}
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		_fail("cannot write output")
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	print("M02_CAMERA_MATH_OK error=%.6f step=%.3f" % [max_error, max_displacement])
	quit(0)
