extends SceneTree

# Headless deterministic smoke for NEX M02-S02 Sightline.
# godot --headless --path nex_modules/render3d/sightline --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0

const CAMERA := Vector3(0.0, 16.0, 16.0)
const PLAYER := Vector3.ZERO
const WALL_NEAR := AABB(Vector3(-2.0, 0.0, 4.0), Vector3(4.0, 8.0, 2.0))
const WALL_FAR := AABB(Vector3(-2.0, 0.0, 8.0), Vector3(4.0, 14.0, 2.0))
const WALL_BEHIND := AABB(Vector3(-2.0, 0.0, -10.0), Vector3(4.0, 8.0, 2.0))
const VEGETATION := AABB(Vector3(-1.0, 0.0, 8.0), Vector3(2.0, 14.0, 2.0))


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _run() -> void:
	var packed := load("res://main.tscn") as PackedScene
	_check(packed != null, "main scene loads")
	if packed == null:
		_finish()
		return
	var rig = packed.instantiate()
	root.add_child(rig)
	await process_frame
	rig.set_camera_position(CAMERA)

	_check(rig.configure({}), "default configuration accepted")
	_check(not rig.configure({"max_reveal_occluders": 0}), "invalid max reveal rejected")
	_check(not rig.configure({"target_alpha": 1.5}), "invalid target alpha rejected")
	_check(not rig.configure({"critical_threat_distance_m": 0.0}), "invalid critical distance rejected")

	_check(rig.segment_intersects_aabb(CAMERA, PLAYER, WALL_NEAR), "segment hits near wall")
	_check(not rig.segment_intersects_aabb(CAMERA, PLAYER, WALL_BEHIND), "segment misses wall behind player")
	_check(rig.segment_intersects_aabb(CAMERA, PLAYER, AABB(Vector3(-20, -20, -20), Vector3(40, 40, 40))), "segment inside large box")

	# Player behind a hard wall: reveal after enter delay, silhouette, gameplay still blocked.
	rig.clear_occluders()
	rig.configure({"enter_delay_s": 0.08, "exit_delay_s": 0.20, "fade_speed": 10.0, "target_alpha": 0.35, "critical_threat_distance_m": 30.0, "max_reveal_occluders": 8})
	rig.set_camera_position(CAMERA)
	_check(rig.register_occluder("wall", WALL_NEAR, 0), "wall registered")
	_check(not rig.register_occluder("wall", WALL_NEAR, 0), "duplicate occluder rejected")
	_check(not rig.register_occluder("bad", AABB(Vector3.ZERO, Vector3.ZERO), 0), "zero-size occluder rejected")
	_check(rig.set_actors([{"id": "player", "priority": 0, "position": PLAYER}]), "player actor set")
	rig.update(0.05)
	var state: Dictionary = rig.get_state()
	_check(not _occluder(state, "wall")["active"], "reveal waits for enter delay")
	_check(not _actor(state, "player")["gameplay_visible"], "gameplay visibility remains blocked")
	_check(not _actor(state, "player")["visual_readable"], "not readable before reveal")
	_check(not state["summary"]["critical_unseen"], "player is not counted as critical")
	rig.update(0.05)
	state = rig.get_state()
	_check(_occluder(state, "wall")["active"], "wall active after enter delay")
	_check(_occluder(state, "wall")["silhouette"], "hard wall uses silhouette")
	_check(absf(float(_occluder(state, "wall")["alpha"]) - 1.0) < 0.001, "hard wall keeps opacity")
	_check(_actor(state, "player")["visual_readable"], "player readable while gameplay blocked")
	_check(not _actor(state, "player")["gameplay_visible"], "gameplay visibility stays separate")

	# Vegetation fades instead of using a silhouette.
	rig.clear_occluders()
	rig.register_occluder("veg", VEGETATION, 2)
	rig.set_actors([{"id": "player", "priority": 0, "position": PLAYER}])
	rig.update(0.2)
	state = rig.get_state()
	_check(_occluder(state, "veg")["active"], "vegetation reveals")
	_check(not _occluder(state, "veg")["silhouette"], "soft occluder has no silhouette")
	_check(float(_occluder(state, "veg")["alpha"]) < 1.0, "soft occluder fades")
	_check(float(_occluder(state, "veg")["alpha"]) >= 0.35, "soft occluder respects target alpha")

	# Decoration behind an occluder is not revealed.
	rig.clear_occluders()
	rig.register_occluder("wall", WALL_NEAR, 0)
	rig.set_actors([{"id": "prop", "priority": 2, "position": PLAYER}])
	rig.update(0.3)
	state = rig.get_state()
	_check(not _occluder(state, "wall")["active"], "decoration does not trigger reveal")
	_check(not _actor(state, "prop")["gameplay_visible"], "decoration visibility blocked")

	# Critical threat: alert immediately, reveal after delay.
	rig.clear_occluders()
	rig.configure({"critical_threat_distance_m": 30.0})
	rig.register_occluder("wall", WALL_NEAR, 0)
	rig.set_actors([{"id": "enemy", "priority": 1, "position": Vector3(1, 0, 1)}])
	rig.update(0.05)
	state = rig.get_state()
	_check(_actor(state, "enemy")["critical"], "near threat is critical")
	_check(_actor(state, "enemy")["danger_alert"], "blocked threat raises alert")
	_check(state["summary"]["critical_unseen"], "critical threat unseen during enter delay")
	rig.update(0.05)
	state = rig.get_state()
	_check(_actor(state, "enemy")["visual_readable"], "critical threat revealed")
	_check(not state["summary"]["critical_unseen"], "critical unseen clears after reveal")

	# Threat beyond critical distance is alerted but not silhouette-revealed.
	rig.clear_occluders()
	rig.configure({"critical_threat_distance_m": 5.0})
	rig.register_occluder("wall", WALL_NEAR, 0)
	rig.set_actors([{"id": "enemy", "priority": 1, "position": Vector3(1, 0, 1)}])
	rig.update(0.3)
	state = rig.get_state()
	_check(not _actor(state, "enemy")["critical"], "distant threat is not critical")
	_check(_actor(state, "enemy")["danger_alert"], "distant blocked threat still alerts")
	_check(not _occluder(state, "wall")["active"], "distant threat does not force reveal")

	# Transparent occluders never block gameplay visibility.
	rig.clear_occluders()
	rig.register_occluder("glass", WALL_NEAR, 4, true)
	rig.set_actors([{"id": "player", "priority": 0, "position": PLAYER}])
	rig.update(0.3)
	state = rig.get_state()
	_check(_actor(state, "player")["gameplay_visible"], "transparent occluder preserves visibility")
	_check(not _occluder(state, "glass")["active"], "transparent occluder is not revealed")

	# Nearest active occluders survive the reveal cap.
	rig.clear_occluders()
	rig.configure({"max_reveal_occluders": 1, "enter_delay_s": 0.0, "exit_delay_s": 0.2})
	rig.register_occluder("near", WALL_NEAR, 0)
	rig.register_occluder("far", WALL_FAR, 0)
	rig.set_actors([{"id": "player", "priority": 0, "position": PLAYER}])
	rig.update(0.2)
	state = rig.get_state()
	var near_entry: Dictionary = _occluder(state, "near")
	var far_entry: Dictionary = _occluder(state, "far")
	_check(bool(near_entry["active"]) != bool(far_entry["active"]), "cap keeps exactly one reveal")
	_check(bool(near_entry["capped"]) or bool(far_entry["capped"]), "one occluder is capped")
	_check(state["summary"]["active_reveals"] == 1, "cap limits active reveals")

	# Hysteresis: short jitter does not flicker once revealed.
	rig.clear_occluders()
	rig.configure({"enter_delay_s": 0.1, "exit_delay_s": 0.3, "fade_speed": 10.0, "max_reveal_occluders": 8})
	rig.register_occluder("wall", WALL_NEAR, 0)
	rig.set_actors([{"id": "player", "priority": 0, "position": PLAYER}])
	rig.update(0.1)
	rig.update(0.1)
	var stable := true
	for index in range(10):
		rig.move_occluder("wall", WALL_BEHIND)
		rig.update(0.02)
		rig.move_occluder("wall", WALL_NEAR)
		rig.update(0.02)
		if not _occluder(rig.get_state(), "wall")["active"]:
			stable = false
	_check(stable, "hysteresis prevents flicker")

	# Moving wall away and waiting exits the reveal cleanly.
	rig.move_occluder("wall", WALL_BEHIND)
	rig.update(0.35)
	state = rig.get_state()
	_check(not _occluder(state, "wall")["active"], "moved wall stops revealing")
	_check(absf(float(_occluder(state, "wall")["reveal_progress"])) < 0.001, "reveal progress returns to zero")
	_check(not _occluder(state, "wall")["silhouette"], "silhouette clears on exit")

	# Camera rotation/zoom changes the blocking set.
	rig.clear_occluders()
	rig.configure({"enter_delay_s": 0.0, "exit_delay_s": 0.1, "fade_speed": 10.0})
	rig.register_occluder("wall", WALL_NEAR, 0)
	rig.set_actors([{"id": "player", "priority": 0, "position": PLAYER}])
	rig.set_camera_position(CAMERA)
	rig.update(0.1)
	_check(_occluder(rig.get_state(), "wall")["active"], "wall blocks from default camera")
	rig.set_camera_position(Vector3(16.0, 16.0, 0.0))
	rig.update(0.2)
	state = rig.get_state()
	_check(not _occluder(state, "wall")["active"], "camera move clears the sightline")
	_check(_actor(state, "player")["gameplay_visible"], "gameplay visibility restored by camera move")
	rig.set_camera_position(CAMERA)

	# A wall behind the player must not leak a silhouette.
	rig.clear_occluders()
	rig.register_occluder("behind", WALL_BEHIND, 0)
	rig.set_actors([{"id": "player", "priority": 0, "position": PLAYER}])
	rig.update(0.3)
	state = rig.get_state()
	_check(not _occluder(state, "behind")["active"], "occluder behind player is ignored")

	# Deterministic replay of the same update sequence.
	var first_state: Dictionary = {}
	rig.clear_occluders()
	rig.register_occluder("wall", WALL_NEAR, 0)
	rig.set_actors([{"id": "player", "priority": 0, "position": PLAYER}])
	rig.set_camera_position(CAMERA)
	for step in range(12):
		rig.update(0.0333333)
	first_state = rig.get_state()
	rig.clear_occluders()
	rig.register_occluder("wall", WALL_NEAR, 0)
	rig.set_actors([{"id": "player", "priority": 0, "position": PLAYER}])
	rig.set_camera_position(CAMERA)
	for step in range(12):
		rig.update(0.0333333)
	_check(JSON.stringify(first_state) == JSON.stringify(rig.get_state()), "deterministic update sequence")

	_finish()


func _occluder(state: Dictionary, id: String) -> Dictionary:
	for entry in state.get("occluders", []):
		if entry["id"] == id:
			return entry
	return {}


func _actor(state: Dictionary, id: String) -> Dictionary:
	for entry in state.get("actors", []):
		if entry["id"] == id:
			return entry
	return {}


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M02_S02_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M02_S02_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
