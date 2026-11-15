extends Node3D

# NEX M04 PBR atlas gallery: eight reference materials on spheres, a triplanar
# wet plane and a Decal3D test. Native Forward+ capture; no production art.

const MATERIAL_IDS := [
	"stone_wet", "brushed_metal", "oak_wood", "cloth_crimson",
	"skin_pale", "terrain_earth", "foliage_deep", "water_clear",
]
const OUTPUT_ENV := "NEX_M04_GALLERY_OUTPUT"
const STAGE_ENV := "NEX_M04_GALLERY_STAGE"
const WIDTH := 1920
const HEIGHT := 1080

var camera: Camera3D
var environment: Environment
var _triplanar_plane: MeshInstance3D
var _triplanar_material: ShaderMaterial
var _triplanar_standard: StandardMaterial3D
var _decal: Decal


func _ready() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	DisplayServer.window_set_size(Vector2i(WIDTH, HEIGHT))
	get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	_build_environment()
	_build_camera()
	_build_lights()
	_build_floor()
	_build_gallery()
	_build_triplanar()
	_build_decal()
	_apply_stage(OS.get_environment(STAGE_ENV).strip_edges())
	call_deferred("_capture")


func _build_environment() -> void:
	environment = Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("#0C1016")
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("#263244")
	environment.ambient_light_energy = 0.35
	environment.tonemap_mode = Environment.TONE_MAPPER_ACES
	environment.tonemap_exposure = 1.1
	environment.glow_enabled = true
	environment.glow_intensity = 0.5
	environment.sdfgi_enabled = false
	environment.volumetric_fog_enabled = false
	var world_environment := WorldEnvironment.new()
	world_environment.environment = environment
	add_child(world_environment)


func _build_camera() -> void:
	camera = Camera3D.new()
	camera.name = "GalleryCamera"
	camera.position = Vector3(10.0, 7.5, 12.0)
	camera.fov = 38.0
	camera.current = true
	add_child(camera)
	camera.look_at(Vector3(0.0, 1.2, 0.0), Vector3.UP)


func _build_lights() -> void:
	var key := DirectionalLight3D.new()
	key.name = "Key"
	key.rotation_degrees = Vector3(-50.0, -30.0, 0.0)
	key.light_color = Color("#FFE2C4")
	key.light_energy = 1.4
	key.shadow_enabled = true
	add_child(key)
	var fill := OmniLight3D.new()
	fill.name = "Fill"
	fill.position = Vector3(-4.0, 4.0, 6.0)
	fill.light_color = Color("#7FA8FF")
	fill.light_energy = 0.8
	fill.omni_range = 14.0
	add_child(fill)
	var rim := OmniLight3D.new()
	rim.name = "Rim"
	rim.position = Vector3(4.0, 3.0, -6.0)
	rim.light_color = Color("#FF9A5A")
	rim.light_energy = 1.2
	rim.omni_range = 12.0
	add_child(rim)


func _build_floor() -> void:
	var floor := MeshInstance3D.new()
	floor.name = "Floor"
	var plane := PlaneMesh.new()
	plane.size = Vector2(24.0, 16.0)
	floor.mesh = plane
	floor.material_override = load("res://materials/terrain_earth.tres")
	add_child(floor)


func _build_gallery() -> void:
	for index in range(MATERIAL_IDS.size()):
		var material_id: String = MATERIAL_IDS[index]
		var sphere := MeshInstance3D.new()
		sphere.name = "Sphere_" + material_id
		var mesh := SphereMesh.new()
		mesh.radius = 0.8
		mesh.height = 1.6
		sphere.mesh = mesh
		var column := index % 4
		var row := index / 4
		sphere.position = Vector3(-4.5 + float(column) * 3.0, 1.0, float(row) * 3.0)
		var material = load("res://materials/%s.tres" % material_id)
		if material_id == "water_clear":
			material = material.duplicate()
			material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			material.albedo_color = Color(1.0, 1.0, 1.0, 0.7)
		elif material_id == "skin_pale":
			material = material.duplicate()
			material.subsurf_scatter_enabled = true
			material.subsurf_scatter_strength = 0.2
		sphere.material_override = material
		add_child(sphere)


func _build_triplanar() -> void:
	_triplanar_plane = MeshInstance3D.new()
	_triplanar_plane.name = "TriplanarPlane"
	var plane := PlaneMesh.new()
	plane.size = Vector2(8.0, 5.0)
	_triplanar_plane.mesh = plane
	_triplanar_plane.position = Vector3(0.0, 0.06, -2.0)
	var shader := load("res://triplanar_wet.gdshader") as Shader
	_triplanar_material = ShaderMaterial.new()
	_triplanar_material.shader = shader
	_triplanar_material.set_shader_parameter("albedo_tex", load("res://textures/stone_wet_albedo.png"))
	_triplanar_material.set_shader_parameter("orm_tex", load("res://textures/stone_wet_orm.png"))
	_triplanar_material.set_shader_parameter("uv_scale", 0.45)
	_triplanar_material.set_shader_parameter("wetness", 0.65)
	_triplanar_standard = load("res://materials/stone_wet.tres")
	_triplanar_plane.material_override = _triplanar_material
	add_child(_triplanar_plane)


func _build_decal() -> void:
	_decal = Decal.new()
	_decal.name = "DecalTest"
	_decal.size = Vector3(4.0, 2.0, 4.0)
	_decal.position = Vector3(0.0, 0.9, 2.0)
	_decal.texture_albedo = load("res://textures/stone_wet_albedo.png")
	_decal.modulate = Color(1.0, 0.8, 0.6, 0.85)
	add_child(_decal)


func _apply_stage(stage: String) -> void:
	if _triplanar_plane == null or _decal == null:
		return
	_triplanar_plane.visible = stage.begins_with("triplanar")
	_triplanar_plane.material_override = _triplanar_material if stage == "triplanar_on" else _triplanar_standard
	_decal.visible = stage == "decal_on"


func _capture() -> void:
	await get_tree().process_frame
	for index in range(60):
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	if image == null or image.is_empty():
		print("M04_GALLERY_FAIL image")
		get_tree().quit(2)
		return
	image.flip_y()
	var path := OS.get_environment(OUTPUT_ENV).strip_edges()
	if path.is_empty():
		path = "user://m04_gallery.png"
	var error := image.save_png(path)
	if error != OK:
		print("M04_GALLERY_FAIL save_png: " + str(error))
		get_tree().quit(2)
		return
	print("M04_GALLERY_IMAGE %s %dx%d" % [ProjectSettings.globalize_path(path), image.get_width(), image.get_height()])
	get_tree().quit(0)
