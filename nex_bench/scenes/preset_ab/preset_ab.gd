extends Node3D

# NEX-M09-PRESET-AB: isolated A/B/A measurement stage.
# Applies a preset_pack.v1 preset at runtime, disables vsync, caps at 240 fps
# and captures through the existing GPU profile session. No engine/renderer
# core changes; the scene lives under nex_bench without touching project.godot.

const SESSION_SCRIPT := "res://gpu_profile/session.gd"
const PACK_PATH := "res://presets/preset_ab/presets.v1.json"
const AUTORUN_ENV := "NEX_PRESET_AB_AUTORUN"
const PRESET_ENV := "NEX_PRESET_AB_PRESET"
const SOURCE_SHA_ENV := "NEX_GPU_PROFILE_SOURCE_SHA"
const WIDTH_ENV := "NEX_PRESET_AB_WIDTH"
const HEIGHT_ENV := "NEX_PRESET_AB_HEIGHT"
const PROXY_COUNT := 200
const OMNI_COUNT := 4

var session: RefCounted
var presets: Dictionary = {}
var preset_id := ""
var environment: Environment
var directional: DirectionalLight3D
var omnis: Array[OmniLight3D] = []
var camera: Camera3D
var applied := {}


func _ready() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 240
	var width := int(OS.get_environment(WIDTH_ENV)) if not OS.get_environment(WIDTH_ENV).is_empty() else 1280
	var height := int(OS.get_environment(HEIGHT_ENV)) if not OS.get_environment(HEIGHT_ENV).is_empty() else 720
	DisplayServer.window_set_size(Vector2i(width, height))
	_load_pack()
	_build_stage()
	_apply_preset()
	if OS.get_environment(AUTORUN_ENV) == "1":
		call_deferred("_start_capture")


func _load_pack() -> void:
	var text := FileAccess.get_file_as_string(PACK_PATH)
	if text.is_empty():
		push_error("Preset pack is missing: " + PACK_PATH)
		return
	var data: Variant = JSON.parse_string(text)
	if not data is Dictionary:
		push_error("Preset pack is not a JSON object")
		return
	var list: Variant = data.get("presets", [])
	if not list is Array:
		push_error("Preset pack presets are not an array")
		return
	for entry in list:
		if entry is Dictionary and entry.has("preset_id"):
			presets[String(entry["preset_id"])] = entry
	preset_id = OS.get_environment(PRESET_ENV).strip_edges()
	if preset_id.is_empty():
		preset_id = "ab-low"


func _build_stage() -> void:
	environment = Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("#0B0F14")
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("#2A3444")
	environment.ambient_light_energy = 0.35
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
	directional.rotation_degrees = Vector3(-52.0, -38.0, 0.0)
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

	_build_proxies(PROXY_COUNT)
	for index in range(OMNI_COUNT):
		var lamp := OmniLight3D.new()
		lamp.name = "Omni_%d" % index
		var angle := TAU * float(index) / float(OMNI_COUNT)
		lamp.position = Vector3(cos(angle) * 6.0, 3.0, sin(angle) * 6.0)
		lamp.light_color = Color("#BFD4FF")
		lamp.light_energy = 1.6
		lamp.omni_range = 8.0
		lamp.shadow_enabled = false
		omnis.append(lamp)
		add_child(lamp)


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
		add_child(item)


func _apply_preset() -> void:
	if not presets.has(preset_id):
		push_error("Preset is not in the pack: " + preset_id)
		return
	var preset: Dictionary = presets[preset_id]
	var settings: Dictionary = preset.get("settings", {})
	var rendering: Dictionary = settings.get("rendering", {})
	var lighting: Dictionary = settings.get("lighting", {})
	var performance: Dictionary = settings.get("performance", {})
	var viewport := get_viewport()
	viewport.scaling_3d_mode = Viewport.SCALING_3D_MODE_BILINEAR
	viewport.scaling_3d_scale = float(rendering.get("resolution_scale", 1.0))
	viewport.msaa_3d = _msaa_mode(String(rendering.get("msaa", "off")))
	environment.tonemap_mode = _tonemap_mode(String(lighting.get("tonemap", "filmic")))
	environment.glow_enabled = bool(lighting.get("glow", false))
	var atlas := int(lighting.get("shadow_atlas_size", 4096))
	RenderingServer.directional_shadow_atlas_set_size(atlas, true)
	RenderingServer.viewport_set_positional_shadow_atlas_size(get_viewport().get_viewport_rid(), atlas, true)
	_apply_shadow_quality(String(rendering.get("shadow_quality", "high")), int(lighting.get("max_shadowed_lights", 4)))
	Engine.max_fps = int(performance.get("target_fps", 240))
	applied = {
		"preset_id": preset_id,
		"resolution_scale": viewport.scaling_3d_scale,
		"msaa": String(rendering.get("msaa", "off")),
		"shadow_quality": String(rendering.get("shadow_quality", "high")),
		"shadow_atlas_size": atlas,
		"max_shadowed_lights": int(lighting.get("max_shadowed_lights", 4)),
		"glow": environment.glow_enabled,
		"target_fps": Engine.max_fps,
	}
	print("NEX_PRESET_AB_APPLY " + JSON.stringify(applied))


func _apply_shadow_quality(quality: String, max_shadowed: int) -> void:
	match quality:
		"off":
			directional.shadow_enabled = false
		"low":
			directional.shadow_enabled = true
			directional.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
			directional.directional_shadow_max_distance = 50.0
		"medium":
			directional.shadow_enabled = true
			directional.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_2_SPLITS
			directional.directional_shadow_max_distance = 100.0
		_:
			directional.shadow_enabled = true
			directional.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
			directional.directional_shadow_max_distance = 200.0 if quality == "high" else 400.0
	for index in range(omnis.size()):
		omnis[index].shadow_enabled = quality != "off" and quality != "low" and index < max_shadowed


func _msaa_mode(value: String) -> int:
	match value:
		"2x":
			return Viewport.MSAA_2X
		"4x":
			return Viewport.MSAA_4X
		"8x":
			return Viewport.MSAA_8X
		_:
			return Viewport.MSAA_DISABLED


func _tonemap_mode(value: String) -> int:
	match value:
		"linear":
			return Environment.TONE_MAPPER_LINEAR
		"reinhard":
			return Environment.TONE_MAPPER_REINHARDT
		"aces":
			return Environment.TONE_MAPPER_ACES
		_:
			return Environment.TONE_MAPPER_FILMIC


func _start_capture() -> void:
	var script := load(SESSION_SCRIPT) as Script
	if script == null:
		print("NEX_PRESET_AB_FAIL session_script")
		get_tree().quit(2)
		return
	session = script.new() as RefCounted
	await get_tree().process_frame
	await get_tree().process_frame
	var context := {
		"source_sha": OS.get_environment(SOURCE_SHA_ENV).strip_edges().to_lower(),
		"scene": "Preset A/B/A",
		"proxy_count": PROXY_COUNT,
		"effect_mode": "lights",
		"renderer": RenderingServer.get_current_rendering_method(),
		"driver": RenderingServer.get_current_rendering_driver_name(),
		"adapter": RenderingServer.get_video_adapter_name(),
	}
	if not session.begin(get_viewport(), context, true):
		print("NEX_PRESET_AB_FAIL begin: " + str(session.last_error))
		get_tree().quit(2)
		return
	print("NEX_PRESET_AB_START preset=%s size=%s vsync=%d max_fps=%d" % [
		preset_id, str(get_viewport().get_visible_rect().size),
		DisplayServer.window_get_vsync_mode(), Engine.max_fps,
	])


func _process(delta: float) -> void:
	if session == null or not session.is_active():
		return
	var update: Dictionary = session.step(delta, get_viewport())
	if not bool(update.get("finished", false)):
		return
	var document: Dictionary = update.get("document", {})
	var path := str(session.save_document(document))
	if path.is_empty():
		print("NEX_PRESET_AB_FAIL export")
		get_tree().quit(3)
		return
	print("NEX_PRESET_AB_CAPTURE " + path)
	get_tree().quit(0)
