extends Node3D

# Original NEX ARPG reference demo. All geometry, materials and effects are
# procedural; no Path of Exile assets, names or parity claims are used.

const PLAYER_SPEED := 4.2
const ATTACK_RANGE := 3.0
const ATTACK_COOLDOWN := 0.55
const ARENA_LIMIT := 7.6
const ATTACK_DURATION := 0.35

var player: CharacterBody3D
var player_visual: Node3D
var weapon_pivot: Node3D
var cloak: MeshInstance3D
var left_leg: MeshInstance3D
var right_leg: MeshInstance3D
var left_arm: MeshInstance3D
var right_arm: MeshInstance3D
var camera: Camera3D
var dummy: StaticBody3D
var dummy_label: Label3D
var dummy_material: StandardMaterial3D
var hud: Control
var health := 100.0
var mana := 100.0
var dummy_health := 100.0
var target := Vector3.ZERO
var has_target := false
var walk_phase := 0.0
var attack_timer := 0.0
var attack_cooldown := 0.0
var hit_flash := 0.0
var elapsed := 0.0
var camera_zoom := 1.0
var hud_timer := 0.0
var torch_lights: Array[OmniLight3D] = []
var torch_base_energy: Array[float] = []
var rng := RandomNumberGenerator.new()


func _ready() -> void:
	rng.seed = 1337
	_build_environment()
	_build_arena()
	_build_player()
	_build_dummy()
	_build_camera()
	_build_hud()


func _process(delta: float) -> void:
	elapsed += delta
	_animate_player(delta)
	_update_camera(delta)
	_update_torches()
	if hit_flash > 0.0:
		hit_flash -= delta
		if hit_flash <= 0.0 and dummy_material != null:
			dummy_material.albedo_color = Color(0.28, 0.18, 0.1)
	hud_timer -= delta
	if hud_timer <= 0.0 and hud != null:
		hud_timer = 0.1
		hud.call("refresh", health, mana, dummy_health, "")


func _physics_process(delta: float) -> void:
	if player == null:
		return
	attack_cooldown = maxf(0.0, attack_cooldown - delta)
	var input_dir := Vector3.ZERO
	if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
		input_dir.z -= 1.0
	if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN):
		input_dir.z += 1.0
	if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
		input_dir.x -= 1.0
	if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
		input_dir.x += 1.0
	if input_dir == Vector3.ZERO and has_target:
		var to_target := target - player.global_position
		to_target.y = 0.0
		if to_target.length() > 0.2:
			input_dir = to_target.normalized()
		else:
			has_target = false
	if input_dir.length() > 0.01:
		input_dir = input_dir.normalized()
		player.velocity.x = input_dir.x * PLAYER_SPEED
		player.velocity.z = input_dir.z * PLAYER_SPEED
		player_visual.rotation.y = lerp_angle(player_visual.rotation.y,
			atan2(input_dir.x, input_dir.z), minf(1.0, delta * 12.0))
	else:
		player.velocity.x = move_toward(player.velocity.x, 0.0, PLAYER_SPEED * delta * 8.0)
		player.velocity.z = move_toward(player.velocity.z, 0.0, PLAYER_SPEED * delta * 8.0)
	player.velocity.y -= 20.0 * delta
	player.move_and_slide()
	var flat := Vector3(
		clampf(player.global_position.x, -ARENA_LIMIT, ARENA_LIMIT),
		player.global_position.y,
		clampf(player.global_position.z, -ARENA_LIMIT, ARENA_LIMIT)
	)
	player.global_position = flat


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mouse := event as InputEventMouseButton
		if not mouse.pressed:
			return
		if mouse.button_index == MOUSE_BUTTON_LEFT:
			_set_move_target(mouse.position)
		elif mouse.button_index == MOUSE_BUTTON_RIGHT:
			_attack()
		elif mouse.button_index == MOUSE_BUTTON_WHEEL_UP:
			camera_zoom = clampf(camera_zoom - 0.08, 0.65, 1.45)
		elif mouse.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			camera_zoom = clampf(camera_zoom + 0.08, 0.65, 1.45)
	elif event is InputEventKey:
		var key := event as InputEventKey
		if key.pressed and not key.echo and key.keycode == KEY_SPACE:
			_attack()


func _set_move_target(screen_position: Vector2) -> void:
	if camera == null:
		return
	var from := camera.project_ray_origin(screen_position)
	var direction := camera.project_ray_normal(screen_position)
	var plane := Plane(Vector3.UP, 0.0)
	var hit: Variant = plane.intersects_ray(from, direction)
	if hit == null:
		return
	var point := Vector3(hit.x, 0.0, hit.z)
	point.x = clampf(point.x, -ARENA_LIMIT, ARENA_LIMIT)
	point.z = clampf(point.z, -ARENA_LIMIT, ARENA_LIMIT)
	target = point
	has_target = true
	_spawn_click_marker(point)


func _attack() -> void:
	if player == null or attack_cooldown > 0.0:
		return
	attack_cooldown = ATTACK_COOLDOWN
	attack_timer = ATTACK_DURATION
	var forward := player_visual.global_transform.basis.z.normalized()
	_spawn_burst(player.global_position + Vector3(0, 1.1, 0) + forward * 0.9,
		Color(1.0, 0.55, 0.15), forward, 26, 3.2)
	if dummy == null:
		return
	var to_dummy := dummy.global_position - player.global_position
	to_dummy.y = 0.0
	if to_dummy.length() <= ATTACK_RANGE:
		player_visual.rotation.y = atan2(to_dummy.x, to_dummy.z)
		_damage_dummy(18.0)


func _damage_dummy(amount: float) -> void:
	if dummy == null:
		return
	dummy_health = maxf(0.0, dummy_health - amount)
	hit_flash = 0.18
	if dummy_material != null:
		dummy_material.albedo_color = Color(0.9, 0.25, 0.12)
	_spawn_burst(dummy.global_position + Vector3(0, 1.25, 0),
		Color(1.0, 0.3, 0.12), Vector3.UP, 18, 2.4)
	_update_dummy_label()
	if dummy_health <= 0.0:
		_reset_dummy_after_delay()


func _reset_dummy_after_delay() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_instance_valid(dummy):
		return
	dummy_health = 100.0
	_update_dummy_label()
	if hud != null:
		hud.call("refresh", health, mana, dummy_health, "Training dummy restored")


func _update_dummy_label() -> void:
	if dummy_label != null:
		dummy_label.text = "TRAINING DUMMY\n%d / 100" % int(dummy_health)


func _animate_player(delta: float) -> void:
	if player == null or player_visual == null:
		return
	var speed := Vector2(player.velocity.x, player.velocity.z).length()
	var moving := clampf(speed / PLAYER_SPEED, 0.0, 1.0)
	if moving > 0.05:
		walk_phase += delta * 9.0
	else:
		walk_phase = lerpf(walk_phase, 0.0, minf(1.0, delta * 6.0))
	var swing := sin(walk_phase) * 0.55 * moving
	if left_leg != null:
		left_leg.rotation_degrees.x = swing
	if right_leg != null:
		right_leg.rotation_degrees.x = -swing
	if left_arm != null:
		left_arm.rotation_degrees.x = -swing * 0.7
	if right_arm != null:
		right_arm.rotation_degrees.x = swing * 0.7
	player_visual.position.y = absf(sin(walk_phase)) * 0.03 * moving
	if cloak != null:
		cloak.rotation_degrees.x = -10.0 + sin(walk_phase * 0.5) * 3.0 * moving
	if weapon_pivot == null:
		return
	if attack_timer > 0.0:
		attack_timer = maxf(0.0, attack_timer - delta)
		var progress := 1.0 - attack_timer / ATTACK_DURATION
		weapon_pivot.rotation.z = deg_to_rad(-125.0) * sin(progress * PI)
	else:
		weapon_pivot.rotation.z = lerp_angle(weapon_pivot.rotation.z, 0.0,
			minf(1.0, delta * 10.0))


func _update_camera(delta: float) -> void:
	if camera == null or player == null:
		return
	var offset := Vector3(6.8, 8.6, 6.8) * camera_zoom
	var desired := player.global_position + offset
	desired.x = clampf(desired.x, -8.2, 8.2)
	desired.z = clampf(desired.z, -8.2, 8.2)
	camera.global_position = camera.global_position.lerp(desired, 1.0 - exp(-4.0 * delta))
	camera.look_at(player.global_position + Vector3(0, 1.0, 0), Vector3.UP)


func _update_torches() -> void:
	for index in range(torch_lights.size()):
		var light := torch_lights[index]
		light.light_energy = torch_base_energy[index] + sin(elapsed * 8.0 + float(index) * 1.7) * 0.3 + sin(elapsed * 17.0 + float(index)) * 0.08


func smoke_state() -> Dictionary:
	return {
		"player": player != null,
		"dummy": dummy != null,
		"hud": hud != null,
		"camera": camera != null,
		"dummy_health": dummy_health,
		"attack_cooldown": attack_cooldown,
		"torches": torch_lights.size(),
	}


func smoke_attack() -> void:
	_damage_dummy(18.0)


func _build_environment() -> void:
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.018, 0.025, 0.04)
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.24, 0.28, 0.4)
	environment.ambient_light_energy = 1.1
	environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var headless := DisplayServer.get_name() == "headless"
	environment.glow_enabled = not headless
	environment.glow_intensity = 1.0
	environment.glow_bloom = 0.25
	environment.fog_enabled = true
	environment.fog_light_color = Color(0.045, 0.06, 0.09)
	environment.fog_density = 0.012
	environment.ssao_enabled = not headless
	environment.ssao_radius = 1.2
	environment.ssao_intensity = 1.5
	var world := WorldEnvironment.new()
	world.environment = environment
	add_child(world)
	var moon := DirectionalLight3D.new()
	moon.rotation_degrees = Vector3(-52, -28, 0)
	moon.light_color = Color(0.55, 0.65, 0.92)
	moon.light_energy = 1.1
	moon.shadow_enabled = true
	add_child(moon)
	var fill := OmniLight3D.new()
	fill.position = Vector3(0, 6.0, 2.0)
	fill.light_color = Color(0.55, 0.42, 0.3)
	fill.light_energy = 1.1
	fill.omni_range = 18.0
	fill.shadow_enabled = false
	add_child(fill)

func _build_arena() -> void:
	var stone := _material(Color(0.08, 0.09, 0.12), 0.0, 0.95)
	var dark := _material(Color(0.04, 0.045, 0.06), 0.0, 0.98)
	var tile_materials := [
		_material(Color(0.085, 0.09, 0.11), 0.0, 0.92),
		_material(Color(0.068, 0.074, 0.095), 0.0, 0.94),
		_material(Color(0.095, 0.1, 0.125), 0.0, 0.9),
	]
	_add_mesh(self, _box(Vector3(18, 0.4, 18)), dark, Vector3(0, -0.2, 0))
	_collision_box(Vector3(18, 0.4, 18), Vector3(0, -0.2, 0))
	for x in range(-4, 5):
		for z in range(-4, 5):
			var material: StandardMaterial3D = tile_materials[(x + z + 8) % tile_materials.size()]
			_add_mesh(self, _box(Vector3(1.92, 0.06, 1.92)), material,
				Vector3(x * 2.0, 0.03, z * 2.0))

	_add_mesh(self, _box(Vector3(18, 3.4, 0.8)), stone, Vector3(0, 1.7, -9.0))
	_add_mesh(self, _box(Vector3(18, 3.4, 0.8)), stone, Vector3(0, 1.7, 9.0))
	_add_mesh(self, _box(Vector3(0.8, 3.4, 18)), stone, Vector3(-9.0, 1.7, 0))
	_add_mesh(self, _box(Vector3(0.8, 3.4, 18)), stone, Vector3(9.0, 1.7, 0))
	_collision_box(Vector3(18, 3.4, 0.8), Vector3(0, 1.7, -9.0))
	_collision_box(Vector3(18, 3.4, 0.8), Vector3(0, 1.7, 9.0))
	_collision_box(Vector3(0.8, 3.4, 18), Vector3(-9.0, 1.7, 0))
	_collision_box(Vector3(0.8, 3.4, 18), Vector3(9.0, 1.7, 0))

	for index in range(-4, 5):
		_add_mesh(self, _box(Vector3(0.9, 3.8, 0.9)), dark,
			Vector3(index * 2.0, 1.9, -8.55))
		_add_mesh(self, _box(Vector3(0.9, 3.8, 0.9)), dark,
			Vector3(index * 2.0, 1.9, 8.55))

	for raw_position in [Vector3(-6.5, 0, -6.5), Vector3(6.5, 0, -6.5), Vector3(-6.5, 0, 6.5), Vector3(6.5, 0, 6.5)]:
		var position: Vector3 = raw_position
		_add_mesh(self, _cylinder(0.55, 0.7, 4.2), stone, position + Vector3(0, 2.1, 0))
		_add_mesh(self, _box(Vector3(1.6, 0.35, 1.6)), dark, position + Vector3(0, 4.3, 0))
		_add_mesh(self, _box(Vector3(1.3, 0.3, 1.3)), dark, position + Vector3(0, 0.15, 0))
		_collision_cylinder(0.7, 4.2, position + Vector3(0, 2.1, 0))
		var inward := -position.normalized() * 0.8
		_add_mesh(self, _cylinder(0.08, 0.12, 0.5), dark,
			position + Vector3(0, 3.1, 0) + inward)
		_add_torch(position + Vector3(0, 3.55, 0) + inward, 3.2)

	_add_mesh(self, _box(Vector3(1.0, 5.0, 1.0)), stone, Vector3(-2.2, 2.5, -8.2))
	_add_mesh(self, _box(Vector3(1.0, 5.0, 1.0)), stone, Vector3(2.2, 2.5, -8.2))
	_add_mesh(self, _box(Vector3(5.4, 0.8, 1.0)), dark, Vector3(0, 5.0, -8.2))
	_add_mesh(self, _box(Vector3(4.0, 0.06, 0.06)), _emissive(Color(0.2, 0.9, 1.0), 2.2),
		Vector3(0, 4.55, -7.68))
	_add_mesh(self, _box(Vector3(4.0, 0.06, 0.06)), _emissive(Color(0.2, 0.9, 1.0), 2.2),
		Vector3(0, 4.55, -8.72))
	_add_mesh(self, _cylinder(0.5, 0.35, 0.6), dark, Vector3(0, 0.3, -5.8))
	_add_mesh(self, _cylinder(0.65, 0.4, 0.15), stone, Vector3(0, 0.65, -5.8))
	_add_torch(Vector3(0, 1.0, -5.8), 3.4)

	for raw_position in [Vector3(-5.0, 0, -5.0), Vector3(5.0, 0, -5.0), Vector3(-5.0, 0, 5.0), Vector3(5.0, 0, 5.0)]:
		var ring_position: Vector3 = raw_position
		var ring := TorusMesh.new()
		ring.inner_radius = 0.32
		ring.outer_radius = 0.4
		ring.rings = 32
		ring.ring_segments = 8
		_add_mesh(self, ring, _emissive(Color(0.12, 0.7, 0.9), 0.7),
			ring_position + Vector3(0, 0.08, 0))

	for raw_position in [Vector3(-5.8, 0, 1.6), Vector3(5.8, 0, 1.6)]:
		var brazier: Vector3 = raw_position
		_add_mesh(self, _cylinder(0.5, 0.35, 0.6), dark, brazier + Vector3(0, 0.3, 0))
		_add_mesh(self, _cylinder(0.65, 0.4, 0.15), stone, brazier + Vector3(0, 0.65, 0))
		_add_torch(brazier + Vector3(0, 1.0, 0), 3.0)

func _build_player() -> void:
	player = CharacterBody3D.new()
	player.name = "Player"
	player.position = Vector3(0, 0, 3.2)
	var collision := CollisionShape3D.new()
	var shape := CapsuleShape3D.new()
	shape.radius = 0.38
	shape.height = 1.7
	collision.shape = shape
	collision.position.y = 0.85
	player.add_child(collision)
	add_child(player)

	player_visual = Node3D.new()
	player_visual.name = "Visual"
	player_visual.scale = Vector3(1.2, 1.2, 1.2)
	player.add_child(player_visual)
	var cloth := _material(Color(0.07, 0.09, 0.15), 0.0, 0.85)
	var leather := _material(Color(0.16, 0.11, 0.075), 0.0, 0.9)
	var skin := _material(Color(0.62, 0.47, 0.36), 0.0, 0.75)
	var steel := _material(Color(0.38, 0.42, 0.5), 0.85, 0.3)
	var gold := _material(Color(0.68, 0.48, 0.14), 0.9, 0.3)
	var crimson := _material(Color(0.28, 0.035, 0.05), 0.0, 0.8)
	var cyan := _emissive(Color(0.2, 0.9, 1.0), 2.0)

	_add_mesh(player_visual, _capsule(0.34, 1.15), cloth, Vector3(0, 1.02, 0))
	_add_mesh(player_visual, _sphere(0.23), skin, Vector3(0, 1.73, 0))
	_add_mesh(player_visual, _cylinder(0.17, 0.3, 0.38), crimson, Vector3(0, 1.86, -0.02))
	_add_mesh(player_visual, _cylinder(0.05, 0.18, 0.22), crimson, Vector3(0, 2.08, -0.04))
	_add_mesh(player_visual, _sphere(0.17), steel, Vector3(-0.36, 1.5, 0))
	_add_mesh(player_visual, _sphere(0.17), steel, Vector3(0.36, 1.5, 0))
	left_arm = _add_mesh(player_visual, _capsule(0.09, 0.68), leather,
		Vector3(-0.45, 1.16, 0.02), Vector3(0, 0, 10))
	right_arm = _add_mesh(player_visual, _capsule(0.09, 0.68), leather,
		Vector3(0.45, 1.16, 0.02), Vector3(0, 0, -10))
	left_leg = _add_mesh(player_visual, _capsule(0.11, 0.82), leather, Vector3(-0.17, 0.47, 0))
	right_leg = _add_mesh(player_visual, _capsule(0.11, 0.82), leather, Vector3(0.17, 0.47, 0))
	_add_mesh(player_visual, _box(Vector3(0.22, 0.18, 0.34)), leather,
		Vector3(-0.17, 0.09, 0.06))
	_add_mesh(player_visual, _box(Vector3(0.22, 0.18, 0.34)), leather,
		Vector3(0.17, 0.09, 0.06))
	_add_mesh(player_visual, _cylinder(0.35, 0.35, 0.1), gold, Vector3(0, 0.82, 0))

	var cloak_mesh := QuadMesh.new()
	cloak_mesh.size = Vector2(0.9, 1.25)
	var cloak_material := _material(Color(0.22, 0.025, 0.04), 0.0, 0.85)
	cloak_material.cull_mode = BaseMaterial3D.CULL_DISABLED
	cloak = _add_mesh(player_visual, cloak_mesh, cloak_material,
		Vector3(0, 1.0, -0.25), Vector3(-10, 0, 0))

	weapon_pivot = Node3D.new()
	weapon_pivot.name = "WeaponPivot"
	weapon_pivot.position = Vector3(0.5, 1.12, 0.12)
	player_visual.add_child(weapon_pivot)
	_add_mesh(weapon_pivot, _box(Vector3(0.07, 0.95, 0.035)), steel, Vector3(0, 0.52, 0))
	_add_mesh(weapon_pivot, _box(Vector3(0.24, 0.07, 0.07)), gold, Vector3(0, 0.04, 0))
	_add_mesh(weapon_pivot, _box(Vector3(0.035, 0.55, 0.012)), cyan, Vector3(0, 0.56, 0.025))
	var glow := OmniLight3D.new()
	glow.light_color = Color(0.2, 0.8, 1.0)
	glow.light_energy = 0.9
	glow.omni_range = 2.6
	glow.position = Vector3(0, 0.8, 0)
	weapon_pivot.add_child(glow)
	var player_fill := OmniLight3D.new()
	player_fill.position = Vector3(0, 2.6, 0)
	player_fill.light_color = Color(0.6, 0.5, 0.4)
	player_fill.light_energy = 0.7
	player_fill.omni_range = 5.5
	player.add_child(player_fill)


func _build_dummy() -> void:
	dummy = StaticBody3D.new()
	dummy.name = "TrainingDummy"
	dummy.scale = Vector3(1.15, 1.15, 1.15)
	dummy.position = Vector3(0, 0, 0.6)
	add_child(dummy)
	var collision := CollisionShape3D.new()
	var shape := CylinderShape3D.new()
	shape.radius = 0.4
	shape.height = 1.9
	collision.shape = shape
	collision.position.y = 0.95
	dummy.add_child(collision)
	dummy_material = _material(Color(0.28, 0.18, 0.1), 0.0, 0.9)
	var rope := _material(Color(0.45, 0.35, 0.2), 0.0, 0.95)
	_add_mesh(dummy, _cylinder(0.18, 0.2, 1.8), dummy_material, Vector3(0, 0.95, 0))
	_add_mesh(dummy, _box(Vector3(1.5, 0.13, 0.13)), rope, Vector3(0, 1.3, 0))
	_add_mesh(dummy, _sphere(0.27), dummy_material, Vector3(0, 1.98, 0))
	_add_mesh(dummy, _cylinder(0.55, 0.6, 0.16), rope, Vector3(0, 0.08, 0))
	_add_mesh(dummy, _cylinder(0.22, 0.22, 0.06), rope, Vector3(0, 0.92, 0))
	var target_ring := TorusMesh.new()
	target_ring.inner_radius = 0.48
	target_ring.outer_radius = 0.56
	target_ring.rings = 32
	target_ring.ring_segments = 8
	_add_mesh(dummy, target_ring, _emissive(Color(0.9, 0.45, 0.12), 1.0),
		Vector3(0, 0.06, 0))


func _build_camera() -> void:
	camera = Camera3D.new()
	camera.name = "DemoCamera"
	camera.position = Vector3(6.8, 8.6, 6.8)
	camera.fov = 40.0
	camera.current = true
	add_child(camera)
	camera.look_at(Vector3(0, 0.8, 1.2), Vector3.UP)


func _build_hud() -> void:
	var layer := CanvasLayer.new()
	layer.name = "Hud"
	add_child(layer)
	var script := load("res://scenes/arpg_demo/arpg_hud.gd") as Script
	hud = Control.new()
	hud.name = "ArpgHud"
	hud.set_script(script)
	layer.add_child(hud)
	hud.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hud.call("refresh", health, mana, dummy_health, "")


func _add_torch(position: Vector3, energy: float = 2.4) -> void:
	var light := OmniLight3D.new()
	light.position = position
	light.light_color = Color(1.0, 0.48, 0.16)
	light.light_energy = energy
	light.omni_range = 12.0
	light.shadow_enabled = false
	add_child(light)
	torch_lights.append(light)
	torch_base_energy.append(energy)
	var particles := CPUParticles3D.new()
	particles.position = position
	particles.amount = 24
	particles.lifetime = 0.7
	particles.one_shot = false
	particles.explosiveness = 0.0
	particles.randomness = 0.6
	particles.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	particles.emission_sphere_radius = 0.12
	particles.direction = Vector3.UP
	particles.spread = 22.0
	particles.initial_velocity_min = 0.4
	particles.initial_velocity_max = 1.0
	particles.gravity = Vector3(0, 0.9, 0)
	particles.scale_amount_min = 0.4
	particles.scale_amount_max = 0.8
	particles.color = Color(1.0, 0.45, 0.12)
	particles.mesh = _particle_sphere()
	particles.emitting = true
	add_child(particles)


func _spawn_burst(position: Vector3, color: Color, direction: Vector3, amount: int, speed: float) -> void:
	var particles := CPUParticles3D.new()
	particles.position = position
	particles.amount = amount
	particles.lifetime = 0.45
	particles.one_shot = true
	particles.explosiveness = 0.95
	particles.direction = direction
	particles.spread = 55.0
	particles.initial_velocity_min = speed * 0.6
	particles.initial_velocity_max = speed
	particles.gravity = Vector3(0, -2.0, 0)
	particles.scale_amount_min = 0.3
	particles.scale_amount_max = 0.6
	particles.color = color
	particles.mesh = _particle_sphere()
	particles.emitting = true
	add_child(particles)
	get_tree().create_timer(0.7).timeout.connect(particles.queue_free)


func _spawn_click_marker(position: Vector3) -> void:
	var marker := MeshInstance3D.new()
	var torus := TorusMesh.new()
	torus.inner_radius = 0.22
	torus.outer_radius = 0.3
	torus.rings = 32
	torus.ring_segments = 8
	marker.mesh = torus
	var material := _emissive(Color(0.2, 0.9, 1.0), 2.0)
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	marker.material_override = material
	marker.position = position + Vector3(0, 0.08, 0)
	add_child(marker)
	var tween := create_tween()
	tween.tween_property(marker, "scale", Vector3(1.8, 1.8, 1.8), 0.35)
	tween.parallel().tween_property(marker, "transparency", 1.0, 0.35)
	tween.tween_callback(marker.queue_free)


func _particle_sphere() -> SphereMesh:
	var sphere := SphereMesh.new()
	sphere.radius = 0.06
	sphere.height = 0.12
	sphere.radial_segments = 8
	sphere.rings = 4
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.vertex_color_use_as_albedo = true
	material.albedo_color = Color.WHITE
	sphere.material = material
	return sphere


func _material(color: Color, metallic: float = 0.0, roughness: float = 0.8,
		emission: Color = Color.BLACK, energy: float = 0.0) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.metallic = metallic
	material.roughness = roughness
	if energy > 0.0:
		material.emission_enabled = true
		material.emission = emission
		material.emission_energy_multiplier = energy
	return material


func _emissive(color: Color, energy: float) -> StandardMaterial3D:
	return _material(color, 0.0, 0.35, color, energy)


func _add_mesh(parent: Node3D, mesh: Mesh, material: Material, position: Vector3,
		rotation_degrees: Vector3 = Vector3.ZERO) -> MeshInstance3D:
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.material_override = material
	instance.position = position
	instance.rotation_degrees = rotation_degrees
	parent.add_child(instance)
	return instance


func _box(size: Vector3) -> BoxMesh:
	var mesh := BoxMesh.new()
	mesh.size = size
	return mesh


func _capsule(radius: float, height: float) -> CapsuleMesh:
	var mesh := CapsuleMesh.new()
	mesh.radius = radius
	mesh.height = height
	return mesh


func _sphere(radius: float) -> SphereMesh:
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = radius * 2.0
	return mesh


func _cylinder(top_radius: float, bottom_radius: float, height: float) -> CylinderMesh:
	var mesh := CylinderMesh.new()
	mesh.top_radius = top_radius
	mesh.bottom_radius = bottom_radius
	mesh.height = height
	return mesh


func _collision_box(size: Vector3, position: Vector3) -> void:
	var body := StaticBody3D.new()
	body.position = position
	var collision := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = size
	collision.shape = shape
	body.add_child(collision)
	add_child(body)


func _collision_cylinder(radius: float, height: float, position: Vector3) -> void:
	var body := StaticBody3D.new()
	body.position = position
	var collision := CollisionShape3D.new()
	var shape := CylinderShape3D.new()
	shape.radius = radius
	shape.height = height
	collision.shape = shape
	body.add_child(collision)
	add_child(body)
