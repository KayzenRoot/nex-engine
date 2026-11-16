extends Node3D

# NEX M08 2.5D hybrid lab: orthographic/perspective camera, 3D geometry,
# Sprite3D billboards, depth sorting, shadows and a 2D CanvasLayer overlay.
# Native captures and measurements only; no engine/renderer core changes.

const SESSION_SCRIPT := "res://gpu_profile/session.gd"
const MODE_ENV := "NEX_M08_MODE"
const VISUAL_ENV := "NEX_M08_VISUAL"
const VISUAL_OUTPUT_ENV := "NEX_M08_VISUAL_OUTPUT"
const AUTORUN_ENV := "NEX_M08_AUTORUN"
const WIDTH_ENV := "NEX_M08_WIDTH"
const HEIGHT_ENV := "NEX_M08_HEIGHT"
const SOURCE_SHA_ENV := "NEX_GPU_PROFILE_SOURCE_SHA"
const WARMUP_FRAMES := 120
const MODES := ["baseline", "sprites", "sorted", "shadows", "overlay", "hybrid",
	"perspective", "quality_low", "quality_high"]

var session: RefCounted
var mode := "baseline"
var camera: Camera3D
var sprites: Array[Sprite3D] = []
var boxes: Array[MeshInstance3D] = []
var overlay: CanvasLayer
var sun: DirectionalLight3D
var sprite_count := 0
var box_count := 0
var shadow_count := 0
var overlay_items := 0
var _metrics_reported := false


func _ready() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 240
	if OS.get_environment("NEX_M08_NATIVE_RESOLUTION") == "1":
		get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	var width := int(OS.get_environment(WIDTH_ENV)) if not OS.get_environment(WIDTH_ENV).is_empty() else 1920
	var height := int(OS.get_environment(HEIGHT_ENV)) if not OS.get_environment(HEIGHT_ENV).is_empty() else 1080
	DisplayServer.window_set_size(Vector2i(width, height))
	mode = OS.get_environment(MODE_ENV).strip_edges()
	if mode.is_empty():
		mode = "baseline"
	if not MODES.has(mode):
		push_error("NEX_M08: unknown mode " + mode)
		get_tree().quit(2)
		return
	_build_environment()
	_build_camera()
	_build_geometry()
	match mode:
		"sprites":
			_build_sprites(40, false)
		"sorted":
			_build_sprites(40, true)
		"shadows":
			_build_sprites(40, true)
			_build_shadows()
		"overlay":
			_build_sprites(40, true)
			_build_overlay()
		"hybrid":
			_build_sprites(40, true)
			_build_shadows()
			_build_overlay()
		"perspective":
			camera.projection = Camera3D.PROJECTION_PERSPECTIVE
			camera.fov = 45.0
			_build_sprites(40, true)
		"quality_low":
			_build_sprites(20, true)
		"quality_high":
			_build_sprites(60, true)
			_build_shadows()
			_build_overlay()
	print("NEX_M08_LAB " + JSON.stringify({
		"mode": mode, "sprites": sprite_count, "boxes": box_count,
		"shadows": shadow_count, "overlay_items": overlay_items,
		"projection": "orthogonal" if camera.projection == Camera3D.PROJECTION_ORTHOGONAL else "perspective",
	}))
	if OS.get_environment(VISUAL_ENV) == "1":
		call_deferred("_start_visual_capture")
	elif OS.get_environment(AUTORUN_ENV) == "1":
		call_deferred("_start_capture")


func _build_environment() -> void:
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("#0A101C")
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("#2B3A55")
	environment.ambient_light_energy = 0.45
	var world := WorldEnvironment.new()
	world.environment = environment
	add_child(world)
	sun = DirectionalLight3D.new()
	sun.name = "M08Sun"
	sun.rotation_degrees = Vector3(-52.0, -38.0, 0.0)
	sun.light_energy = 1.3
	sun.shadow_enabled = false
	add_child(sun)


func _build_camera() -> void:
	camera = Camera3D.new()
	camera.name = "M08Camera"
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 14.0
	camera.position = Vector3(12.0, 14.0, 12.0)
	add_child(camera)
	camera.look_at(Vector3.ZERO, Vector3.UP)
	camera.current = true


func _build_geometry() -> void:
	var ground := MeshInstance3D.new()
	ground.name = "M08Ground"
	var plane := PlaneMesh.new()
	plane.size = Vector2(30.0, 30.0)
	ground.mesh = plane
	var ground_material := StandardMaterial3D.new()
	ground_material.albedo_color = Color("#26354F")
	ground_material.roughness = 0.9
	ground.material_override = ground_material
	add_child(ground)
	var box_mesh := BoxMesh.new()
	box_mesh.size = Vector3(0.8, 1.2, 0.8)
	var box_material := StandardMaterial3D.new()
	box_material.albedo_color = Color("#9AA8C0")
	box_material.roughness = 0.65
	for index in range(16):
		var box := MeshInstance3D.new()
		box.name = "M08Box_%02d" % index
		box.mesh = box_mesh
		box.material_override = box_material
		var col := index % 4
		var row := index / 4
		box.position = Vector3(-5.0 + float(col) * 3.2, 0.6, -5.0 + float(row) * 3.2)
		box.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		add_child(box)
		boxes.append(box)
	box_count = boxes.size()


func _billboard_texture() -> GradientTexture2D:
	var texture := GradientTexture2D.new()
	texture.width = 128
	texture.height = 128
	texture.fill = GradientTexture2D.FILL_RADIAL
	texture.fill_from = Vector2(0.5, 0.5)
	texture.fill_to = Vector2(1.0, 1.0)
	var gradient := Gradient.new()
	gradient.colors = [Color(1.0, 0.85, 0.55, 1.0), Color(1.0, 0.45, 0.2, 0.85), Color(1.0, 0.2, 0.1, 0.0)]
	gradient.offsets = [0.0, 0.55, 1.0]
	texture.gradient = gradient
	return texture


func _build_sprites(total: int, sorted: bool) -> void:
	var texture := _billboard_texture()
	for index in range(total):
		var sprite := Sprite3D.new()
		sprite.name = "M08Sprite_%03d" % index
		sprite.texture = texture
		sprite.pixel_size = 0.006
		sprite.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		sprite.alpha_cut = SpriteBase3D.ALPHA_CUT_DISABLED
		sprite.transparent = true
		sprite.shaded = false
		var col := index % 10
		var row := index / 10
		var depth := -6.0 + float(row) * 2.2
		sprite.position = Vector3(-7.0 + float(col) * 1.6, 1.2, depth)
		if sorted:
			sprite.render_priority = int((depth + 10.0) * 10.0)
		add_child(sprite)
		sprites.append(sprite)
	sprite_count = sprites.size()


func _build_shadows() -> void:
	if sun == null:
		return
	sun.shadow_enabled = true
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
	sun.directional_shadow_max_distance = 60.0
	for sprite in sprites:
		sprite.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		sprite.transparent = false
		sprite.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	for box in boxes:
		box.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	shadow_count = sprites.size() + boxes.size()


func _build_overlay() -> void:
	overlay = CanvasLayer.new()
	overlay.name = "M08Overlay"
	overlay.layer = 10
	add_child(overlay)
	var top := ColorRect.new()
	top.color = Color(0.02, 0.04, 0.08, 0.72)
	top.position = Vector2(0, 0)
	top.size = Vector2(1920, 90)
	overlay.add_child(top)
	overlay_items += 1
	var bottom := ColorRect.new()
	bottom.color = Color(0.02, 0.04, 0.08, 0.72)
	bottom.position = Vector2(0, 990)
	bottom.size = Vector2(1920, 90)
	overlay.add_child(bottom)
	overlay_items += 1
	for index in range(4):
		var marker := ColorRect.new()
		marker.color = Color(1.0, 0.72, 0.25, 0.9)
		marker.position = Vector2(40 + index * 120, 32)
		marker.size = Vector2(72, 26)
		overlay.add_child(marker)
		overlay_items += 1


func _start_visual_capture() -> void:
	await get_tree().process_frame
	for _index in range(WARMUP_FRAMES):
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	if image == null or image.is_empty():
		print("NEX_M08_FAIL image")
		get_tree().quit(2)
		return
	image.flip_y()
	var path := OS.get_environment(VISUAL_OUTPUT_ENV).strip_edges()
	if path.is_empty():
		path = ProjectSettings.globalize_path("user://m08_lab_%s.png" % mode)
	var error := image.save_png(path)
	if error != OK:
		print("NEX_M08_FAIL save_png: " + str(error))
		get_tree().quit(2)
		return
	print("NEX_M08_IMAGE %s %dx%d" % [ProjectSettings.globalize_path(path), image.get_width(), image.get_height()])
	get_tree().quit(0)


func _start_capture() -> void:
	var script := load(SESSION_SCRIPT) as Script
	if script == null:
		print("NEX_M08_FAIL session_script")
		get_tree().quit(2)
		return
	session = script.new() as RefCounted
	await get_tree().process_frame
	await get_tree().process_frame
	var context := {
		"source_sha": OS.get_environment(SOURCE_SHA_ENV).strip_edges().to_lower(),
		"scene": "M08 Hybrid 2.5D Lab",
		"layout": "M08 hybrid 2.5D lab",
		"proxy_count": 100,
		"effect_mode": "lights",
		"renderer": RenderingServer.get_current_rendering_method(),
		"driver": RenderingServer.get_current_rendering_driver_name(),
		"adapter": RenderingServer.get_video_adapter_name(),
	}
	if not session.begin(get_viewport(), context, true):
		print("NEX_M08_FAIL begin: " + str(session.last_error))
		get_tree().quit(2)
		return
	print("NEX_M08_START mode=%s scene=%s size=%s vsync=%d max_fps=%d" % [
		mode, context["scene"], str(get_viewport().get_visible_rect().size),
		DisplayServer.window_get_vsync_mode(), Engine.max_fps,
	])


func _process(delta: float) -> void:
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
		print("NEX_M08_FAIL export")
		get_tree().quit(3)
		return
	print("NEX_M08_CAPTURE " + path)
	get_tree().quit(0)


func _report_metrics() -> void:
	await RenderingServer.frame_post_draw
	print("NEX_M08_LAB_METRICS " + JSON.stringify({
		"mode": mode,
		"draw_calls": int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),
		"objects": int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)),
		"primitives": int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)),
	}))
