extends Node3D

# NEX-M01-S05 Lighting Matrix: standalone measurement stage for native Godot
# lighting/VFX cost. It reuses the integrated GPU profile session (read-only)
# and never fabricates metrics. F11 starts/cancels; Q/W/E select 25/100/200;
# 1..5 select presets. Combined preset is limited to 25 proxies.

const SESSION_SCRIPT := "res://gpu_profile/session.gd"
const PRESETS_PATH := "res://presets/lighting_matrix/presets.v1.json"
const SOURCE_SHA_ENV := "NEX_GPU_PROFILE_SOURCE_SHA"
const STATUS_SECONDS := 0.5

var session: RefCounted
var presets: Array = []
var counts: Array = [25, 100, 200]
var preset_index := 0
var count_index := 0
var status_label: Label
var profile_label: Label
var world_root: Node3D
var camera: Camera3D
var directional: DirectionalLight3D
var sun_rotation := Vector3(-52.0, -38.0, 0.0)
var last_status := "LIGHTING MATRIX | 1..5 presets, Q/W/E counts, F11 profile"
var status_timer := 0.0


func _ready() -> void:
	_load_presets()
	_build_stage()
	_build_ui()
	var script := load(SESSION_SCRIPT) as Script
	if script != null:
		session = script.new() as RefCounted
	_apply_preset()


func _load_presets() -> void:
	var text := FileAccess.get_file_as_string(PRESETS_PATH)
	if text.is_empty():
		push_error("Lighting matrix presets are missing: " + PRESETS_PATH)
		return
	var data: Variant = JSON.parse_string(text)
	if not (data is Dictionary):
		push_error("Lighting matrix presets are not a JSON object")
		return
	var raw: Variant = data.get("presets", [])
	if not (raw is Array) or raw.size() < 1:
		push_error("Lighting matrix presets list is empty")
		return
	presets = raw
	preset_index = clampi(preset_index, 0, presets.size() - 1)


func _build_stage() -> void:
	world_root = Node3D.new()
	world_root.name = "World"
	add_child(world_root)

	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("#0B0F14")
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("#2A3444")
	environment.ambient_light_energy = 0.35
	environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var world_environment := WorldEnvironment.new()
	world_environment.environment = environment
	add_child(world_environment)

	camera = Camera3D.new()
	camera.name = "IsoCamera"
	camera.position = Vector3(14.0, 14.0, 14.0)
	camera.rotation_degrees = Vector3(-35.264, 45.0, 0.0)
	camera.fov = 40.0
	camera.current = true
	add_child(camera)

	directional = DirectionalLight3D.new()
	directional.name = "Sun"
	directional.rotation_degrees = sun_rotation
	directional.light_energy = 1.15
	add_child(directional)

	var ground := MeshInstance3D.new()
	ground.name = "Ground"
	var plane := PlaneMesh.new()
	plane.size = Vector2(40.0, 40.0)
	ground.mesh = plane
	var ground_material := StandardMaterial3D.new()
	ground_material.albedo_color = Color("#1A222E")
	ground.material_override = ground_material
	add_child(ground)


func _build_ui() -> void:
	var layer := CanvasLayer.new()
	layer.name = "HUD"
	add_child(layer)
	var title := Label.new()
	title.position = Vector2(16.0, 12.0)
	title.add_theme_font_size_override("font_size", 18)
	title.text = "NEX ENGINE / LIGHTING MATRIX"
	layer.add_child(title)
	status_label = Label.new()
	status_label.position = Vector2(16.0, 44.0)
	status_label.add_theme_font_size_override("font_size", 14)
	status_label.text = last_status
	layer.add_child(status_label)
	profile_label = Label.new()
	profile_label.position = Vector2(16.0, 660.0)
	profile_label.custom_minimum_size = Vector2(900.0, 48.0)
	profile_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	profile_label.add_theme_font_size_override("font_size", 14)
	profile_label.text = "GPU PROFILER IDLE | F11 start; combined is 25-only"
	layer.add_child(profile_label)


func _apply_preset() -> void:
	if presets.is_empty():
		return
	for child in world_root.get_children():
		world_root.remove_child(child)
		child.queue_free()
	var preset: Dictionary = presets[preset_index]
	var count := _current_count()
	_build_proxies(count)
	var omni_count := int(preset.get("omni_lights", 0))
	var omni_shadows := bool(preset.get("omni_shadows", false))
	for index in range(omni_count):
		var lamp := OmniLight3D.new()
		lamp.name = "Omni_%d" % index
		var angle := TAU * float(index) / float(maxi(omni_count, 1))
		lamp.position = Vector3(cos(angle) * 6.0, 3.0, sin(angle) * 6.0)
		lamp.light_color = Color("#BFD4FF")
		lamp.light_energy = 1.6
		lamp.omni_range = 8.0
		lamp.shadow_enabled = omni_shadows
		world_root.add_child(lamp)
	directional.shadow_enabled = bool(preset.get("directional_shadow", false))
	var particle_count := int(preset.get("particles", 0))
	for index in range(particle_count):
		var particles := GPUParticles3D.new()
		particles.name = "VFX_%d" % index
		particles.amount = 12
		particles.lifetime = 1.2
		particles.position = Vector3(float(index - 1) * 2.5, 1.0, 0.0)
		var process_material := ParticleProcessMaterial.new()
		process_material.direction = Vector3.UP
		process_material.initial_velocity_min = 0.6
		process_material.initial_velocity_max = 1.4
		process_material.gravity = Vector3(0.0, -1.2, 0.0)
		particles.process_material = process_material
		var glow := SphereMesh.new()
		glow.radius = 0.08
		glow.height = 0.16
		var glow_material := StandardMaterial3D.new()
		glow_material.albedo_color = Color("#35D0FF")
		glow_material.emission_enabled = true
		glow_material.emission = Color("#35D0FF")
		glow.material = glow_material
		particles.draw_pass_1 = glow
		world_root.add_child(particles)
	last_status = "PRESET %s | %d proxies | %s" % [
		str(preset.get("id", "?")), count, str(preset.get("label", ""))
	]
	_refresh_status()


func _build_proxies(count: int) -> void:
	var side := ceili(sqrt(float(count)))
	var mesh := BoxMesh.new()
	mesh.size = Vector3(0.7, 1.2, 0.7)
	var material := StandardMaterial3D.new()
	material.albedo_color = Color("#7E8CA3")
	material.roughness = 0.65
	for index in range(count):
		var item := MeshInstance3D.new()
		item.name = "Proxy_%03d" % index
		item.mesh = mesh
		item.material_override = material
		var col := index % side
		var row := index / side
		item.position = Vector3(
			(float(col) - float(side - 1) * 0.5) * 1.5,
			0.6,
			(float(row) - float(side - 1) * 0.5) * 1.5
		)
		world_root.add_child(item)


func _current_count() -> int:
	var preset: Dictionary = presets[preset_index] if not presets.is_empty() else {}
	var cap := int(preset.get("max_proxy_count", 0))
	var count := int(counts[clampi(count_index, 0, counts.size() - 1)])
	if cap > 0:
		count = mini(count, cap)
	return count


func _unhandled_key_input(event: InputEvent) -> void:
	if not (event is InputEventKey):
		return
	var key_event := event as InputEventKey
	if not key_event.pressed or key_event.echo:
		return
	match key_event.keycode:
		KEY_1, KEY_2, KEY_3, KEY_4, KEY_5:
			_cancel_for_workload_change()
			preset_index = int(key_event.keycode - KEY_1)
			_apply_preset()
		KEY_Q:
			_cancel_for_workload_change()
			count_index = 0
			_apply_preset()
		KEY_W:
			_cancel_for_workload_change()
			count_index = 1
			_apply_preset()
		KEY_E:
			_cancel_for_workload_change()
			count_index = 2
			_apply_preset()
		KEY_F11:
			_toggle_profile()
		_:
			return
	get_viewport().set_input_as_handled()


func _cancel_for_workload_change() -> void:
	if session != null and session.is_active():
		session.cancel("workload changed; run not exported")
		last_status = "CANCELLED | workload changed; no export"
		_refresh_status()


func _toggle_profile() -> void:
	if session == null:
		last_status = "GPU profiler unavailable: session module failed to load"
		_refresh_status()
		return
	if session.is_active():
		session.cancel("manual cancellation")
		last_status = "CANCELLED | no partial report exported"
		_refresh_status()
		return
	var preset: Dictionary = presets[preset_index]
	var source_sha := OS.get_environment(SOURCE_SHA_ENV).strip_edges().to_lower()
	var context := {
		"source_sha": source_sha,
		"scene": "Lighting Matrix",
		"proxy_count": _current_count(),
		"effect_mode": str(preset.get("effect_mode", "")),
		"renderer": RenderingServer.get_current_rendering_method(),
		"driver": RenderingServer.get_current_rendering_driver_name(),
		"adapter": RenderingServer.get_video_adapter_name(),
	}
	if not session.begin(get_viewport(), context, true):
		last_status = "GPU profile blocked: " + str(session.last_error)
		_refresh_status()
		return
	last_status = "GPU PROFILER WARMUP | 2 s then 30 s; F11 cancels"
	_refresh_status()


func _process(delta: float) -> void:
	if session == null or not session.is_active():
		status_timer += delta
		if status_timer >= STATUS_SECONDS:
			status_timer = 0.0
			_refresh_status()
		return
	var update: Dictionary = session.step(delta, get_viewport())
	_refresh_status()
	if bool(update.get("finished", false)):
		var document: Dictionary = update.get("document", {})
		var path := str(session.save_document(document))
		if path.is_empty():
			last_status = "GPU PROFILER %s | export failed" % str(document.get("run_status", "INVALID"))
		else:
			last_status = "GPU PROFILER %s | %s" % [str(document.get("run_status", "INVALID")), path.get_file()]
		_refresh_status()


func _refresh_status() -> void:
	if status_label != null:
		status_label.text = last_status
	if profile_label == null:
		return
	if session == null:
		profile_label.text = "GPU PROFILER UNAVAILABLE"
		return
	if session.is_active():
		var progress: Dictionary = session.progress()
		profile_label.text = "GPU PROFILER %s | %.2fs | %d proxies" % [
			str(progress.get("state", "?")), float(progress.get("elapsed_seconds", 0.0)), _current_count()
		]
	else:
		profile_label.text = "GPU PROFILER IDLE | last: %s" % last_status
