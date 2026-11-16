extends Node2D

# NEX M07 2D reference lab: layered sprites, CanvasModulate, 2D lights,
# LightOccluder2D shadows, normal maps, GPUParticles2D and ParallaxBackground.
# Native captures and measurements only; no engine/renderer core changes.

const SESSION_SCRIPT := "res://gpu_profile/session.gd"
const MODE_ENV := "NEX_M07_MODE"
const VISUAL_ENV := "NEX_M07_VISUAL"
const VISUAL_OUTPUT_ENV := "NEX_M07_VISUAL_OUTPUT"
const AUTORUN_ENV := "NEX_M07_AUTORUN"
const WIDTH_ENV := "NEX_M07_WIDTH"
const HEIGHT_ENV := "NEX_M07_HEIGHT"
const SOURCE_SHA_ENV := "NEX_GPU_PROFILE_SOURCE_SHA"
const WARMUP_FRAMES := 120
const MODES := ["baseline", "lighting", "shadows", "normal", "particles", "parallax",
	"quality_low", "quality_medium", "quality_high"]

var session: RefCounted
var mode := "baseline"
var camera: Camera2D
var parallax: ParallaxBackground
var sprites: Array[Sprite2D] = []
var lights: Array[PointLight2D] = []
var particles: Array[GPUParticles2D] = []
var occluders: Array[LightOccluder2D] = []
var sprite_count := 0
var light_count := 0
var particle_count := 0
var parallax_layers := 0
var shadow_count := 0
var _metrics_reported := false


func _ready() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 240
	if OS.get_environment("NEX_M07_NATIVE_RESOLUTION") == "1":
		get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	var width := int(OS.get_environment(WIDTH_ENV)) if not OS.get_environment(WIDTH_ENV).is_empty() else 1920
	var height := int(OS.get_environment(HEIGHT_ENV)) if not OS.get_environment(HEIGHT_ENV).is_empty() else 1080
	DisplayServer.window_set_size(Vector2i(width, height))
	mode = OS.get_environment(MODE_ENV).strip_edges()
	if mode.is_empty():
		mode = "baseline"
	if not MODES.has(mode):
		push_error("NEX_M07: unknown mode " + mode)
		get_tree().quit(2)
		return
	camera = Camera2D.new()
	camera.name = "M07Camera"
	camera.position = Vector2.ZERO
	camera.anchor_mode = Camera2D.ANCHOR_MODE_DRAG_CENTER
	camera.enabled = true
	add_child(camera)
	_build_background()
	_build_sprites()
	match mode:
		"lighting":
			_build_lighting(false, false)
		"shadows":
			_build_lighting(true, false)
		"normal":
			_build_lighting(false, true)
		"particles":
			_build_particles(6, 64)
		"parallax":
			_build_parallax(3)
		"quality_low":
			_build_lighting(false, false, 1)
		"quality_medium":
			_build_lighting(false, false, 2)
			_build_parallax(2)
		"quality_high":
			_build_lighting(true, true, 4)
			_build_particles(6, 64)
			_build_parallax(3)
	print("NEX_M07_LAB " + JSON.stringify({
		"mode": mode, "sprites": sprite_count, "lights": light_count,
		"particles": particle_count, "parallax_layers": parallax_layers,
		"shadows": shadow_count,
	}))
	if OS.get_environment(VISUAL_ENV) == "1":
		call_deferred("_start_visual_capture")
	elif OS.get_environment(AUTORUN_ENV) == "1":
		call_deferred("_start_capture")


func _build_background() -> void:
	var background_layer := CanvasLayer.new()
	background_layer.name = "M07BackgroundLayer"
	background_layer.layer = -200
	add_child(background_layer)
	var background := ColorRect.new()
	background.name = "M07Background"
	background.color = Color("#0B1220")
	background.position = Vector2.ZERO
	background.size = Vector2(1920, 1080)
	background_layer.add_child(background)
	var horizon := ColorRect.new()
	horizon.name = "M07Horizon"
	horizon.color = Color("#17263A")
	horizon.position = Vector2(0, 540)
	horizon.size = Vector2(1920, 540)
	background_layer.add_child(horizon)


func _radial_texture(size := 64, color := Color.WHITE) -> ImageTexture:
	var image := Image.create(size, size, false, Image.FORMAT_RGBA8)
	var center := (float(size) - 1.0) * 0.5
	for y in range(size):
		for x in range(size):
			var dx := (float(x) - center) / center
			var dy := (float(y) - center) / center
			var distance := sqrt(dx * dx + dy * dy)
			var alpha := clampf(1.0 - distance, 0.0, 1.0)
			image.set_pixel(x, y, Color(color.r, color.g, color.b, alpha))
	return ImageTexture.create_from_image(image)


func _sprite_texture() -> ImageTexture:
	var image := Image.create(64, 64, false, Image.FORMAT_RGBA8)
	for y in range(64):
		for x in range(64):
			var edge := 6
			var inside := x >= edge and x < 64 - edge and y >= edge and y < 64 - edge
			var color := Color("#D9E2F2") if inside else Color("#2B3A55")
			image.set_pixel(x, y, color)
	return ImageTexture.create_from_image(image)


func _normal_texture() -> ImageTexture:
	var image := Image.create(64, 64, false, Image.FORMAT_RGBA8)
	for y in range(64):
		for x in range(64):
			var nx := (float(x) / 63.0) * 2.0 - 1.0
			var ny := (float(y) / 63.0) * 2.0 - 1.0
			var nz := sqrt(maxf(0.0, 1.0 - nx * nx - ny * ny))
			image.set_pixel(x, y, Color(nx * 0.5 + 0.5, ny * 0.5 + 0.5, nz * 0.5 + 0.5))
	return ImageTexture.create_from_image(image)


func _build_sprites() -> void:
	var diffuse := _sprite_texture()
	var normal := _normal_texture()
	var canvas_texture := CanvasTexture.new()
	canvas_texture.diffuse_texture = diffuse
	canvas_texture.normal_texture = normal
	var total := 100
	for index in range(total):
		var sprite := Sprite2D.new()
		sprite.name = "M07Sprite_%03d" % index
		sprite.texture = canvas_texture if mode in ["normal", "quality_high"] else diffuse
		var col := index % 12
		var row := index / 12
		sprite.position = Vector2(-900.0 + float(col) * 160.0, -420.0 + float(row) * 90.0)
		sprite.scale = Vector2(0.9, 0.9)
		sprite.modulate = Color(0.75 + 0.25 * float(index % 4) / 3.0,
			0.75 + 0.25 * float(index % 3) / 2.0, 1.0)
		sprite.z_index = 10 + (index % 5)
		add_child(sprite)
		sprites.append(sprite)
	sprite_count = sprites.size()


func _build_lighting(shadows: bool, normals: bool, light_total := 4) -> void:
	var canvas_modulate := CanvasModulate.new()
	canvas_modulate.name = "M07CanvasModulate"
	canvas_modulate.color = Color("#4A5A78")
	add_child(canvas_modulate)
	var light_texture := _radial_texture(256, Color.WHITE)
	var colors := [Color("#FFB26B"), Color("#6BB8FF"), Color("#FF7A9C"), Color("#8CFFB2")]
	for index in range(light_total):
		var light := PointLight2D.new()
		light.name = "M07Light_%02d" % index
		light.texture = light_texture
		light.texture_scale = 3.5
		light.energy = 1.4
		light.color = colors[index % colors.size()]
		light.position = Vector2(-600.0 + float(index) * 400.0, -180.0 + float(index % 2) * 260.0)
		light.shadow_enabled = shadows
		light.range_z_min = -100
		light.range_z_max = 100
		add_child(light)
		lights.append(light)
		light_count += 1
		if shadows:
			shadow_count += 1
	if shadows:
		_build_occluders()


func _build_occluders() -> void:
	var walls := [
		Vector2(-520, -60), Vector2(-420, -60), Vector2(-420, 120), Vector2(-520, 120),
		Vector2(180, -240), Vector2(300, -240), Vector2(300, -80), Vector2(180, -80),
		Vector2(520, 40), Vector2(640, 40), Vector2(640, 220), Vector2(520, 220),
	]
	for index in range(0, walls.size(), 4):
		var polygon := OccluderPolygon2D.new()
		polygon.polygon = PackedVector2Array([walls[index], walls[index + 1], walls[index + 2], walls[index + 3]])
		var occluder := LightOccluder2D.new()
		occluder.name = "M07Occluder_%02d" % (index / 4)
		occluder.occluder = polygon
		occluder.position = Vector2.ZERO
		add_child(occluder)
		occluders.append(occluder)


func _build_particles(emitters: int, amount: int) -> void:
	var texture := _radial_texture(48, Color("#FFC46B"))
	for index in range(emitters):
		var emitter := GPUParticles2D.new()
		emitter.name = "M07Particles_%02d" % index
		emitter.amount = amount
		emitter.lifetime = 2.2
		emitter.one_shot = false
		emitter.explosiveness = 0.15
		emitter.texture = texture
		emitter.position = Vector2(-700.0 + float(index) * 280.0, 240.0 + float(index % 2) * 80.0)
		emitter.z_index = 30
		var process := ParticleProcessMaterial.new()
		process.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
		process.emission_sphere_radius = 18.0
		process.direction = Vector3(0.0, -1.0, 0.0)
		process.spread = 35.0
		process.initial_velocity_min = 20.0
		process.initial_velocity_max = 60.0
		process.gravity = Vector3(0.0, 12.0, 0.0)
		process.scale_min = 0.4
		process.scale_max = 1.0
		process.color = Color("#FFC46B")
		emitter.process_material = process
		emitter.emitting = true
		add_child(emitter)
		particles.append(emitter)
		particle_count += amount


func _build_parallax(layers: int) -> void:
	parallax = ParallaxBackground.new()
	parallax.name = "M07Parallax"
	parallax.layer = -100
	add_child(parallax)
	var colors := [Color("#1B2E4A"), Color("#274363"), Color("#35577D")]
	for index in range(layers):
		var layer := ParallaxLayer.new()
		layer.name = "M07ParallaxLayer_%02d" % index
		layer.motion_scale = Vector2(0.15 + 0.2 * float(index), 1.0)
		layer.motion_mirroring = Vector2(1920.0, 0.0)
		var band := ColorRect.new()
		band.color = Color(colors[index % colors.size()], 0.65)
		band.position = Vector2(0, 120 + index * 220)
		band.size = Vector2(1920, 140)
		layer.add_child(band)
		parallax.add_child(layer)
		parallax_layers += 1


func _start_visual_capture() -> void:
	await get_tree().process_frame
	for _index in range(WARMUP_FRAMES):
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	if image == null or image.is_empty():
		print("NEX_M07_FAIL image")
		get_tree().quit(2)
		return
	image.flip_y()
	var path := OS.get_environment(VISUAL_OUTPUT_ENV).strip_edges()
	if path.is_empty():
		path = ProjectSettings.globalize_path("user://m07_lab_%s.png" % mode)
	var error := image.save_png(path)
	if error != OK:
		print("NEX_M07_FAIL save_png: " + str(error))
		get_tree().quit(2)
		return
	print("NEX_M07_IMAGE %s %dx%d" % [ProjectSettings.globalize_path(path), image.get_width(), image.get_height()])
	get_tree().quit(0)


func _start_capture() -> void:
	var script := load(SESSION_SCRIPT) as Script
	if script == null:
		print("NEX_M07_FAIL session_script")
		get_tree().quit(2)
		return
	session = script.new() as RefCounted
	await get_tree().process_frame
	await get_tree().process_frame
	var context := {
		"source_sha": OS.get_environment(SOURCE_SHA_ENV).strip_edges().to_lower(),
		"scene": "M07 2D Lab",
		"layout": "M07 layered 2D lab",
		"proxy_count": sprite_count,
		"effect_mode": "lights",
		"renderer": RenderingServer.get_current_rendering_method(),
		"driver": RenderingServer.get_current_rendering_driver_name(),
		"adapter": RenderingServer.get_video_adapter_name(),
	}
	if not session.begin(get_viewport(), context, true):
		print("NEX_M07_FAIL begin: " + str(session.last_error))
		get_tree().quit(2)
		return
	print("NEX_M07_START mode=%s scene=%s size=%s vsync=%d max_fps=%d" % [
		mode, context["scene"], str(get_viewport().get_visible_rect().size),
		DisplayServer.window_get_vsync_mode(), Engine.max_fps,
	])


func _process(delta: float) -> void:
	if parallax != null and mode in ["parallax", "quality_medium", "quality_high"]:
		parallax.scroll_base_offset.x += delta * 20.0
	if not _metrics_reported:
		_metrics_reported = true
		_report_metrics()
	if session == null or not session.is_active():
		return
	var update: Dictionary = session.step(delta, get_viewport())
	if not bool(update.get("finished", false)):
		return
	var document: Dictionary = update.get("document", {})
	var path := str(session.save_document(document))
	if path.is_empty():
		print("NEX_M07_FAIL export")
		get_tree().quit(3)
		return
	print("NEX_M07_CAPTURE " + path)
	get_tree().quit(0)


func _report_metrics() -> void:
	await RenderingServer.frame_post_draw
	print("NEX_M07_LAB_METRICS " + JSON.stringify({
		"mode": mode,
		"draw_calls": int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),
		"objects": int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)),
		"primitives": int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)),
	}))
