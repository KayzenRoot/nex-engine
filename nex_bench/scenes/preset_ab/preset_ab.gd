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
const NATIVE_RESOLUTION_ENV := "NEX_PRESET_AB_NATIVE_RESOLUTION"
const DEFAULT_PROXY_COUNT := 200
const PROXY_COUNT_ENV := "NEX_PRESET_AB_PROXY_COUNT"
const SCENE_ENV := "NEX_PRESET_AB_SCENE"
const VISUAL_ENV := "NEX_PRESET_AB_VISUAL"
const VISUAL_OUTPUT_ENV := "NEX_PRESET_AB_VISUAL_OUTPUT"
const VISUAL_WARMUP_FRAMES := 180
const VISUAL_SEQUENCE_ENV := "NEX_PRESET_AB_VISUAL_SEQUENCE"
const VISUAL_SEQUENCE_FRAMES := 5
const VISUAL_SEQUENCE_INTERVAL := 30
const CAMERA_MOTION_ENV := "NEX_PRESET_AB_CAMERA_MOTION"
const CAMERA_MOTION_STEP_DEG := 3.0
const CAMERA_MODE_ENV := "NEX_PRESET_AB_CAMERA_MODE"
const SIGHTLINE_ENV := "NEX_PRESET_AB_SIGHTLINE"
const SIGHTLINE_STAGE_ENV := "NEX_PRESET_AB_SIGHTLINE_STAGE"
const DEPTH_OVERLAY_ENV := "NEX_PRESET_AB_DEPTH_OVERLAY"
const TAA_ENV := "NEX_PRESET_AB_TAA"
const PROFILE_ENV := "NEX_PRESET_AB_PROFILE"
const LOOK_ENV := "NEX_PRESET_AB_LOOK"
const TORCHES_ENV := "NEX_PRESET_AB_TORCHES"
const GI_ENV := "NEX_PRESET_AB_GI"
const FOG_ENV := "NEX_PRESET_AB_FOG"
const LIGHT_BUDGET_ENV := "NEX_PRESET_AB_LIGHT_BUDGET"
const M03_LIGHT_RIG := preload("res://scenes/m03_lighting/light_rig_planner.gd")
const SIGHTLINE_SCRIPT := preload("res://scenes/m02_analysis/sightline_controller.gd")
const DEPTH_SCRIPT := preload("res://scenes/m02_analysis/depth_composition_solver.gd")
const M02_CAMERA_RIG := preload("res://scenes/m02_camera/camera_rig.gd")
const ALLOWED_PROXY_COUNTS := [25, 50, 100, 200]
const OMNI_COUNT := 4
const M01_SCENES := {
	"corridor_static": {
		"path": "res://scenes/base/corridor_static.tscn",
		"scene": "M01 Corridor A/B/A",
		"layout": "M01 corridor_static + deterministic fillers",
		"proxy_count": 100,
		"seed": 4101,
	},
	"arena_combat": {
		"path": "res://scenes/base/arena_combat.tscn",
		"scene": "M01 Arena A/B/A",
		"layout": "M01 arena_combat + deterministic fillers",
		"proxy_count": 100,
		"seed": 4102,
	},
	"dense_city": {
		"path": "res://scenes/base/dense_city.tscn",
		"scene": "M01 City A/B/A",
		"layout": "M01 dense_city + deterministic fillers",
		"proxy_count": 100,
		"seed": 4103,
	},
}

var session: RefCounted
var presets: Dictionary = {}
var preset_id := ""
var environment: Environment
var directional: DirectionalLight3D
var omnis: Array[OmniLight3D] = []
var camera: Camera3D
var applied := {}
var proxy_count := DEFAULT_PROXY_COUNT
var scene_id := ""
var scene_label := "Preset A/B/A"
var scene_layout := "built-in deterministic grid"
var base_mesh_count := 0
var filler_mesh_count := 0
var stage_valid := true
var _sightline_meshes: Dictionary = {}


func _ready() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 240
	if OS.get_environment(NATIVE_RESOLUTION_ENV) == "1":
		get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	var width := int(OS.get_environment(WIDTH_ENV)) if not OS.get_environment(WIDTH_ENV).is_empty() else 1280
	var height := int(OS.get_environment(HEIGHT_ENV)) if not OS.get_environment(HEIGHT_ENV).is_empty() else 720
	DisplayServer.window_set_size(Vector2i(width, height))
	_resolve_scene()
	_load_pack()
	_build_stage()
	if stage_valid:
		_apply_preset()
	if stage_valid:
		_apply_profile()
	if stage_valid:
		_apply_look()
	if stage_valid and OS.get_environment(TAA_ENV) == "1":
		get_viewport().use_taa = true
		print("NEX_PRESET_AB_TAA enabled")
	if stage_valid and OS.get_environment(CAMERA_MODE_ENV) == "rig":
		_use_m02_camera_rig(width, height)
	if OS.get_environment(VISUAL_SEQUENCE_ENV) == "1":
		call_deferred("_start_visual_sequence")
	elif OS.get_environment(VISUAL_ENV) == "1":
		call_deferred("_start_visual_capture")
	elif OS.get_environment(AUTORUN_ENV) == "1":
		call_deferred("_start_capture")


func _resolve_scene() -> void:
	var requested := OS.get_environment(SCENE_ENV).strip_edges()
	if requested.is_empty() or requested == "builtin":
		_read_proxy_count()
		return
	if not M01_SCENES.has(requested):
		_fail_stage("unknown scene: " + requested)
		return
	scene_id = requested
	var spec: Dictionary = M01_SCENES[scene_id]
	scene_label = String(spec["scene"])
	scene_layout = String(spec["layout"])
	proxy_count = int(spec["proxy_count"])
	var override := OS.get_environment(PROXY_COUNT_ENV).strip_edges()
	if not override.is_empty():
		var parsed := int(override)
		if not ALLOWED_PROXY_COUNTS.has(parsed):
			_fail_stage("proxy count must be one of 25/50/100/200: " + override)
			return
		proxy_count = parsed


func _read_proxy_count() -> void:
	var requested := OS.get_environment(PROXY_COUNT_ENV).strip_edges()
	if requested.is_empty():
		return
	var parsed := int(requested)
	if ALLOWED_PROXY_COUNTS.has(parsed):
		proxy_count = parsed
	else:
		_fail_stage("proxy count must be one of 25/50/100/200: " + requested)


func _fail_stage(message: String) -> void:
	stage_valid = false
	push_error("NEX_PRESET_AB: " + message)


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
	if not stage_valid:
		return
	_build_environment()
	if scene_id.is_empty():
		_build_builtin_stage()
	else:
		_build_m01_stage()


func _build_environment() -> void:
	environment = Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("#0B0F14")
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("#2A3444")
	environment.ambient_light_energy = 0.35
	var world_environment := WorldEnvironment.new()
	world_environment.environment = environment
	add_child(world_environment)


func _build_builtin_stage() -> void:
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

	_build_proxies(proxy_count)
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


func _build_m01_stage() -> void:
	var spec: Dictionary = M01_SCENES[scene_id]
	var packed := load(String(spec["path"])) as PackedScene
	if packed == null:
		_fail_stage("cannot load " + String(spec["path"]))
		return
	var root := packed.instantiate()
	if not root is Node3D:
		_fail_stage("base scene is not Node3D")
		root.free()
		return
	add_child(root)
	var meshes := root.find_children("*", "MeshInstance3D", true, false)
	base_mesh_count = meshes.size()
	var target := proxy_count
	if base_mesh_count > target:
		_fail_stage("base scene has more meshes than the target")
		return
	filler_mesh_count = target - base_mesh_count
	_build_fillers(filler_mesh_count, meshes)
	_use_base_rig(root)
	var total := find_children("*", "MeshInstance3D", true, false).size()
	if total != target:
		_fail_stage("mesh count %d does not match proxy_count %d" % [total, target])
	if OS.get_environment(SIGHTLINE_ENV) == "1":
		_build_sightline()
	if OS.get_environment(DEPTH_OVERLAY_ENV) == "1":
		_build_depth_overlay()


func _use_base_rig(root: Node) -> void:
	var cameras := root.find_children("*", "Camera3D", true, false)
	if cameras.is_empty():
		_fail_stage("base scene has no Camera3D")
		return
	camera = cameras[0] as Camera3D
	for index in range(cameras.size()):
		(cameras[index] as Camera3D).current = index == 0
	var directionals := root.find_children("*", "DirectionalLight3D", true, false)
	if directionals.is_empty():
		_fail_stage("base scene has no DirectionalLight3D")
		return
	directional = directionals[0] as DirectionalLight3D
	for light in root.find_children("*", "OmniLight3D", true, false):
		omnis.append(light as OmniLight3D)


func _build_fillers(count: int, meshes: Array) -> void:
	if count <= 0:
		return
	var bounds := _mesh_bounds(meshes)
	var side := ceili(sqrt(float(count)))
	var step_x := maxf(bounds.size.x - 1.0, 1.0) / float(side)
	var step_z := maxf(bounds.size.z - 1.0, 1.0) / float(side)
	var start_x := bounds.position.x + 0.5
	var start_z := bounds.position.z + 0.5
	var rng := RandomNumberGenerator.new()
	rng.seed = int(M01_SCENES[scene_id]["seed"])
	var mesh := BoxMesh.new()
	mesh.size = Vector3(0.7, 1.2, 0.7)
	var material := StandardMaterial3D.new()
	material.albedo_color = Color("#7E8CA3")
	material.roughness = 0.65
	for index in range(count):
		var item := MeshInstance3D.new()
		item.name = "M01Filler_%03d" % index
		item.mesh = mesh
		item.material_override = material
		var col := index % side
		var row := index / side
		item.position = Vector3(
			start_x + (float(col) + 0.5) * step_x + rng.randf_range(-0.12, 0.12),
			0.6,
			start_z + (float(row) + 0.5) * step_z + rng.randf_range(-0.12, 0.12)
		)
		add_child(item)


func _mesh_bounds(meshes: Array) -> AABB:
	var bounds := AABB()
	var initialized := false
	for node in meshes:
		var item := node as MeshInstance3D
		if item == null or item.mesh == null:
			continue
		var box: AABB = item.global_transform * item.mesh.get_aabb()
		if not initialized:
			bounds = box
			initialized = true
		else:
			bounds = bounds.merge(box)
	if not initialized:
		return AABB(Vector3(-5.0, 0.0, -5.0), Vector3(10.0, 1.0, 10.0))
	return bounds


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
		"preset_id": preset_id, "proxy_count": proxy_count,
		"scene": scene_label, "layout": scene_layout,
		"base_meshes": base_mesh_count, "filler_meshes": filler_mesh_count,
		"resolution_scale": viewport.scaling_3d_scale,
		"msaa": String(rendering.get("msaa", "off")),
		"shadow_quality": String(rendering.get("shadow_quality", "high")),
		"shadow_atlas_size": atlas,
		"max_shadowed_lights": int(lighting.get("max_shadowed_lights", 4)),
		"glow": environment.glow_enabled,
		"target_fps": Engine.max_fps,
	}
	print("NEX_PRESET_AB_APPLY " + JSON.stringify(applied))


func _apply_profile() -> void:
	var profile := OS.get_environment(PROFILE_ENV).strip_edges()
	if profile.is_empty():
		return
	var viewport := get_viewport()
	match profile:
		"quality":
			viewport.scaling_3d_scale = 1.0
			viewport.msaa_3d = Viewport.MSAA_4X
			environment.glow_enabled = true
			_apply_shadow_quality("high", 4)
		"balanced":
			viewport.scaling_3d_scale = 0.85
			viewport.msaa_3d = Viewport.MSAA_2X
			environment.glow_enabled = true
			_apply_shadow_quality("medium", 2)
		"performance":
			viewport.scaling_3d_scale = 0.7
			viewport.msaa_3d = Viewport.MSAA_DISABLED
			environment.glow_enabled = false
			_apply_shadow_quality("low", 0)
		_:
			_fail_stage("unknown profile: " + profile)
			return
	applied["profile"] = profile
	applied["profile_resolution_scale"] = viewport.scaling_3d_scale
	print("NEX_PRESET_AB_PROFILE " + JSON.stringify({
		"profile": profile,
		"resolution_scale": viewport.scaling_3d_scale,
		"msaa": viewport.msaa_3d,
		"glow": environment.glow_enabled,
	}))


func _look_spec(look: String) -> Dictionary:
	match look:
		"dungeon_torch":
			return {
				"background": Color("#05070A"),
				"ambient": Color("#3A2418"), "ambient_energy": 0.22,
				"exposure": 1.25, "glow_intensity": 0.9, "glow_bloom": 0.14,
				"sdfgi": true, "sdfgi_energy": 0.8,
				"volumetric_fog": true, "depth_fog": false, "fog_density": 0.015,
				"fog_albedo": Color(0.35, 0.28, 0.22), "fog_emission": Color(0.02, 0.01, 0.005),
				"moon_color": Color("#5A6FA8"), "moon_energy": 0.25,
				"torch_color": Color("#FF8A3D"), "torch_energy": 4.0, "torch_range": 9.0,
				"torches": 8, "shadowed": 4,
				"fill_color": Color("#FFB37A"), "fill_energy": 0.9, "fill_range": 14.0,
			}
		"moonlit_exterior":
			return {
				"background": Color("#0A1220"),
				"ambient": Color("#1A2A4A"), "ambient_energy": 0.25,
				"exposure": 1.0, "glow_intensity": 0.6, "glow_bloom": 0.08,
				"sdfgi": true, "sdfgi_energy": 0.6,
				"volumetric_fog": true, "depth_fog": false, "fog_density": 0.008,
				"fog_albedo": Color(0.18, 0.24, 0.35), "fog_emission": Color(0.0, 0.005, 0.01),
				"moon_color": Color("#8FB3FF"), "moon_energy": 0.9,
				"torch_color": Color("#FFB066"), "torch_energy": 1.6, "torch_range": 10.0,
				"torches": 5, "shadowed": 3,
				"fill_color": Color("#7FA8FF"), "fill_energy": 0.5, "fill_range": 16.0,
			}
		"boss_arena":
			return {
				"background": Color("#0B0505"),
				"ambient": Color("#2A0E0E"), "ambient_energy": 0.2,
				"exposure": 1.15, "glow_intensity": 0.9, "glow_bloom": 0.15,
				"sdfgi": true, "sdfgi_energy": 0.7,
				"volumetric_fog": true, "depth_fog": false, "fog_density": 0.02,
				"fog_albedo": Color(0.3, 0.12, 0.08), "fog_emission": Color(0.02, 0.002, 0.0),
				"moon_color": Color("#6A7AA8"), "moon_energy": 0.4,
				"torch_color": Color("#FF5A1F"), "torch_energy": 4.5, "torch_range": 8.0,
				"torches": 10, "shadowed": 4,
				"fill_color": Color("#FF7A4D"), "fill_energy": 0.8, "fill_range": 14.0,
			}
	return {}


func _torch_position(index: int, count: int) -> Vector3:
	var bounds := _mesh_bounds(find_children("*", "MeshInstance3D", true, false))
	var center := bounds.get_center()
	var radius := maxf(2.0, minf(bounds.size.x, bounds.size.z) * 0.35)
	var angle := TAU * float(index) / float(maxi(1, count))
	return Vector3(center.x + cos(angle) * radius, bounds.position.y + 2.5, center.z + sin(angle) * radius)


func _apply_look() -> void:
	var look := OS.get_environment(LOOK_ENV).strip_edges()
	if look.is_empty():
		return
	var spec := _look_spec(look)
	if spec.is_empty():
		_fail_stage("unknown look: " + look)
		return
	var gi_override := OS.get_environment(GI_ENV).strip_edges()
	if gi_override == "off":
		spec["sdfgi"] = false
	elif gi_override == "sdfgi":
		spec["sdfgi"] = true
	var fog_override := OS.get_environment(FOG_ENV).strip_edges()
	if fog_override == "off":
		spec["volumetric_fog"] = false
		spec["depth_fog"] = false
	elif fog_override == "depth":
		spec["volumetric_fog"] = false
		spec["depth_fog"] = true
	elif fog_override == "volumetric":
		spec["volumetric_fog"] = true
		spec["depth_fog"] = false
	var torch_count := int(spec["torches"])
	var torch_override := OS.get_environment(TORCHES_ENV).strip_edges()
	if not torch_override.is_empty():
		torch_count = maxi(1, int(torch_override))
	var budget := OS.get_environment(LIGHT_BUDGET_ENV) == "1"
	var max_shadowed := int(spec["shadowed"])
	if budget:
		max_shadowed = mini(2, max_shadowed)
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = spec["background"]
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = spec["ambient"]
	environment.ambient_light_energy = spec["ambient_energy"]
	environment.tonemap_mode = Environment.TONE_MAPPER_ACES
	environment.tonemap_exposure = spec["exposure"]
	environment.glow_enabled = true
	environment.glow_intensity = spec["glow_intensity"]
	environment.glow_bloom = spec["glow_bloom"]
	environment.sdfgi_enabled = bool(spec["sdfgi"])
	environment.sdfgi_energy = float(spec["sdfgi_energy"])
	environment.volumetric_fog_enabled = bool(spec["volumetric_fog"])
	if bool(spec["volumetric_fog"]):
		environment.volumetric_fog_density = float(spec["fog_density"])
		environment.volumetric_fog_albedo = spec["fog_albedo"]
		environment.volumetric_fog_emission = spec["fog_emission"]
		environment.volumetric_fog_length = 64.0
	else:
		environment.fog_enabled = bool(spec["depth_fog"])
		environment.fog_density = float(spec["fog_density"])
		environment.fog_light_color = spec["fog_albedo"]
		environment.fog_light_energy = 0.4 if bool(spec["depth_fog"]) else 0.0
	directional.light_color = spec["moon_color"]
	directional.light_energy = spec["moon_energy"]
	directional.shadow_enabled = true
	directional.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
	directional.directional_shadow_max_distance = 200.0
	directional.shadow_bias = 0.05
	var planner = M03_LIGHT_RIG.new()
	planner.name = "M03LightRig"
	add_child(planner)
	if not planner.configure({"max_shadowed_lights": max_shadowed, "atlas_size": 4096}):
		_fail_stage("look configure: " + planner.last_error)
		return
	if not planner.configure_environment({
		"ambient_source": 0,
		"ambient_color": spec["ambient"],
		"ambient_energy": spec["ambient_energy"],
		"tonemap": 3,
		"glow": true,
		"fog_density": float(spec["fog_density"]) if bool(spec["volumetric_fog"]) else 0.0,
		"fog_light_energy": 0.4 if bool(spec["depth_fog"]) else 0.0,
		"gi_mode": 1 if bool(spec["sdfgi"]) else 0,
		"gi_energy": float(spec["sdfgi_energy"]),
	}):
		_fail_stage("look environment: " + planner.last_error)
		return
	if not planner.register_light("moon", 0, spec["moon_color"], spec["moon_energy"], true, 0.05, 0.0, 1, 0.0, 0.0, 4):
		_fail_stage("look moon: " + planner.last_error)
		return
	if not planner.register_light("fill", 1, spec["fill_color"], spec["fill_energy"], false, 0.05, 0.0, 1, spec["fill_range"]):
		_fail_stage("look fill: " + planner.last_error)
		return
	for index in range(torch_count):
		if not planner.register_light("torch_%02d" % index, 1, spec["torch_color"], spec["torch_energy"], true, 0.05, 0.0, 1, spec["torch_range"]):
			_fail_stage("look torch: " + planner.last_error)
			return
	var plan: Dictionary = planner.plan()
	var assigned := {}
	for light in plan["lights"]:
		if String(light["light_type"]) == "omni":
			assigned[String(light["light_id"])] = bool(light["shadow_assigned"])
	for index in range(torch_count):
		var torch := OmniLight3D.new()
		torch.name = "M03Torch_%02d" % index
		torch.position = _torch_position(index, torch_count)
		torch.light_color = spec["torch_color"]
		torch.light_energy = spec["torch_energy"]
		torch.omni_range = spec["torch_range"]
		torch.shadow_enabled = bool(assigned.get("torch_%02d" % index, false))
		torch.shadow_bias = 0.05
		add_child(torch)
		omnis.append(torch)
	var fill := OmniLight3D.new()
	fill.name = "M03Fill"
	var scene_bounds := _mesh_bounds(find_children("*", "MeshInstance3D", true, false))
	fill.position = scene_bounds.get_center() + Vector3(0.0, 2.5, 0.0)
	fill.light_color = spec["fill_color"]
	fill.light_energy = spec["fill_energy"]
	fill.omni_range = spec["fill_range"]
	fill.shadow_enabled = false
	add_child(fill)
	omnis.append(fill)
	if camera != null:
		camera.position = Vector3(13.0, 11.0, 13.0)
		camera.look_at(Vector3(0.0, 1.0, 0.0), Vector3.UP)
		camera.fov = 45.0
	print("NEX_PRESET_AB_LOOK " + JSON.stringify({
		"look": look,
		"torches": torch_count,
		"shadowed": plan["totals"]["shadowed_lights"],
		"sdfgi": bool(spec["sdfgi"]),
		"volumetric_fog": bool(spec["volumetric_fog"]),
		"depth_fog": bool(spec["depth_fog"]),
		"budget": budget,
	}))


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


func _use_m02_camera_rig(width: int, height: int) -> void:
	if camera == null:
		_fail_stage("M02 camera mode requires a baseline camera")
		return
	var distance := clampf(camera.position.length(), 1.0, 500.0)
	var fov := clampf(camera.fov, 10.0, 100.0)
	var rig = M02_CAMERA_RIG.new()
	rig.name = "M02CameraRig"
	add_child(rig)
	rig.set_viewport_size(Vector2i(width, height))
	if not rig.configure({
		"projection": "perspective",
		"yaw_deg": 45.0,
		"pitch_deg": -35.264,
		"distance_m": distance,
		"vertical_fov_deg": fov,
	}):
		_fail_stage("M02 camera rig configuration failed: " + rig.last_error)
		return
	rig.set_focus(Vector3.ZERO)
	camera.current = false
	camera = rig.camera
	camera.current = true


func _build_sightline() -> void:
	var boxes: Array = []
	for node in find_children("*", "MeshInstance3D", true, false):
		var item := node as MeshInstance3D
		if item == null or item.mesh == null:
			continue
		var box: AABB = item.global_transform * item.mesh.get_aabb()
		if box.size.x > 0.1 and box.size.y > 0.1 and box.size.z > 0.1:
			boxes.append(box)
	boxes.sort_custom(func(a, b): return a.get_volume() > b.get_volume())
	if boxes.is_empty() or camera == null:
		_fail_stage("sightline requires meshes and a camera")
		return
	var controller = SIGHTLINE_SCRIPT.new()
	controller.name = "M02Sightline"
	add_child(controller)
	if not controller.configure({"target_alpha": 0.2}):
		_fail_stage("sightline configure: " + controller.last_error)
		return
	controller.set_camera_position(camera.global_position)
	var scene_bounds := _mesh_bounds(find_children("*", "MeshInstance3D", true, false))
	var center := scene_bounds.get_center()
	var focus := Vector3(center.x, scene_bounds.position.y + 1.0, center.z)
	var forward := (focus - camera.global_position).normalized()
	var wall := MeshInstance3D.new()
	var wall_mesh := BoxMesh.new()
	wall_mesh.size = Vector3(6.0, 4.0, 0.3)
	wall.mesh = wall_mesh
	wall.position = focus - forward * 2.0
	add_child(wall)
	wall.look_at(camera.global_position, Vector3.UP)
	var wall_material := StandardMaterial3D.new()
	wall_material.albedo_color = Color("#4A5568")
	wall_material.roughness = 0.8
	wall_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	wall.material_override = wall_material
	_sightline_meshes["test_wall"] = wall
	controller.register_occluder("test_wall", AABB(wall.position - Vector3(3.0, 2.0, 3.0), Vector3(6.0, 4.0, 6.0)), 2, false)
	if not controller.set_actors([
		{"id": "player", "priority": 0, "position": focus},
		{"id": "threat", "priority": 1, "position": focus + forward * 1.5},
		{"id": "decor", "priority": 2, "position": focus - forward * 1.5},
	]):
		_fail_stage("sightline actors: " + controller.last_error)
		return
	if OS.get_environment(SIGHTLINE_STAGE_ENV) == "revealed":
		for step in range(10):
			controller.update(0.05)
	else:
		controller.update(0.0001)
	var state: Dictionary = controller.get_state()
	for actor in state.get("actors", []):
		var proxy := MeshInstance3D.new()
		var capsule := CapsuleMesh.new()
		capsule.radius = 0.35
		capsule.height = 1.8
		proxy.mesh = capsule
		var position: Array = actor["position"]
		proxy.position = Vector3(position[0], position[1] + 0.9, position[2])
		var material := StandardMaterial3D.new()
		material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		var color := Color("#59C3FF") if String(actor["id"]) == "player" else (Color("#FF5A5A") if String(actor["id"]) == "threat" else Color("#9AA4B2"))
		var readable := bool(actor["gameplay_visible"]) or bool(actor["visual_readable"])
		color.a = 1.0 if readable else 0.35
		material.albedo_color = color
		if bool(actor["visual_readable"]) and bool(actor["needs_reveal"]):
			material.emission_enabled = true
			material.emission = Color("#59C3FF")
			material.emission_energy_multiplier = 1.5
		elif bool(actor["danger_alert"]):
			material.emission_enabled = true
			material.emission = Color("#FF2D2D")
			material.emission_energy_multiplier = 1.2
		proxy.material_override = material
		add_child(proxy)
	for occluder in state.get("occluders", []):
		var id := String(occluder["id"])
		if not _sightline_meshes.has(id):
			continue
		var mesh: MeshInstance3D = _sightline_meshes[id]
		var base_material: StandardMaterial3D = mesh.material_override
		var clone: StandardMaterial3D = base_material.duplicate()
		clone.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		var color: Color = clone.albedo_color
		color.a = float(occluder["alpha"])
		clone.albedo_color = color
		mesh.material_override = clone
		print("NEX_PRESET_AB_SIGHTLINE_WALL alpha=%.2f" % float(occluder["alpha"]))
	print("NEX_PRESET_AB_SIGHTLINE " + JSON.stringify(state.get("summary", {})))


func _build_depth_overlay() -> void:
	var boxes: Array = []
	for node in find_children("*", "MeshInstance3D", true, false):
		var item := node as MeshInstance3D
		if item == null or item.mesh == null:
			continue
		var box: AABB = item.global_transform * item.mesh.get_aabb()
		if box.size.x > 0.1 and box.size.y > 0.1 and box.size.z > 0.1:
			boxes.append(box)
	boxes.sort_custom(func(a, b): return a.get_volume() > b.get_volume())
	if boxes.is_empty() or camera == null:
		_fail_stage("depth overlay requires meshes and a camera")
		return
	var focus: Vector3 = boxes[0].get_center()
	var camera_position := camera.global_position
	var forward := (focus - camera_position).normalized()
	var quad := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(10.0, 10.0)
	quad.mesh = plane
	quad.position = camera_position + forward * 2.5
	add_child(quad)
	quad.look_at(focus, Vector3.UP)
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.albedo_color = Color(0.1, 0.4, 0.9, 0.45)
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	quad.material_override = material
	var solver = DEPTH_SCRIPT.new()
	solver.name = "M02Depth"
	add_child(solver)
	if not solver.configure({}):
		_fail_stage("depth configure: " + solver.last_error)
		return
	if not solver.set_camera(camera_position, forward):
		_fail_stage("depth camera: " + solver.last_error)
		return
	solver.register_primitive("overlay", 2, camera_position + forward * 2.5, 1.0, false, false)
	solver.register_primitive("player", 0, focus, 1.0, true, false)
	var plan: Dictionary = solver.plan()
	print("NEX_PRESET_AB_DEPTH " + JSON.stringify({
		"z_fight_risks": plan.get("z_fight_risks", []).size(),
		"alpha_over_critical": plan.get("alpha_over_critical", []).size(),
		"overlay_gameplay_conflicts": plan.get("overlay_gameplay_conflicts", []).size(),
		"passes": plan.get("passes", {}),
	}))


func _apply_camera_motion(frame_index: int) -> void:
	if OS.get_environment(CAMERA_MOTION_ENV) != "1" or camera == null:
		return
	var flat := Vector2(camera.position.x, camera.position.z)
	if flat.length() < 0.001:
		return
	var angle := atan2(flat.y, flat.x) + deg_to_rad(CAMERA_MOTION_STEP_DEG * frame_index)
	camera.position = Vector3(flat.length() * cos(angle), camera.position.y, flat.length() * sin(angle))
	camera.look_at(Vector3.ZERO, Vector3.UP)


func _start_visual_sequence() -> void:
	if not stage_valid:
		print("NEX_PRESET_AB_FAIL stage")
		get_tree().quit(2)
		return
	await get_tree().process_frame
	for index in range(VISUAL_WARMUP_FRAMES):
		await get_tree().process_frame
	var requested_dir := OS.get_environment(VISUAL_OUTPUT_ENV).strip_edges()
	if requested_dir.is_empty():
		var tag := scene_id if not scene_id.is_empty() else "builtin"
		requested_dir = "user://gpu_profiles/temporal_%s_%s_%d" % [tag, preset_id, Time.get_ticks_usec()]
	var output_dir := ProjectSettings.globalize_path(requested_dir)
	DirAccess.make_dir_recursive_absolute(output_dir)
	for frame_index in range(VISUAL_SEQUENCE_FRAMES):
		_apply_camera_motion(frame_index)
		await RenderingServer.frame_post_draw
		var image := get_viewport().get_texture().get_image()
		if image == null or image.is_empty():
			print("NEX_PRESET_AB_FAIL image")
			get_tree().quit(2)
			return
		image.flip_y()
		var path := output_dir.path_join("frame_%02d.png" % frame_index)
		var error := image.save_png(path)
		if error != OK:
			print("NEX_PRESET_AB_FAIL save_png: " + str(error))
			get_tree().quit(2)
			return
		print("NEX_PRESET_AB_SEQUENCE_FRAME %s %d %dx%d" % [
			path, frame_index, image.get_width(), image.get_height(),
		])
		if frame_index < VISUAL_SEQUENCE_FRAMES - 1:
			for interval_index in range(VISUAL_SEQUENCE_INTERVAL):
				await get_tree().process_frame
	print("NEX_PRESET_AB_SEQUENCE_DONE")
	get_tree().quit(0)


func _start_visual_capture() -> void:
	if not stage_valid:
		print("NEX_PRESET_AB_FAIL stage")
		get_tree().quit(2)
		return
	await get_tree().process_frame
	for index in range(VISUAL_WARMUP_FRAMES):
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	if image == null or image.is_empty():
		print("NEX_PRESET_AB_FAIL image")
		get_tree().quit(2)
		return
	image.flip_y()
	var path := OS.get_environment(VISUAL_OUTPUT_ENV).strip_edges()
	if path.is_empty():
		var tag := scene_id if not scene_id.is_empty() else "builtin"
		path = "user://gpu_profiles/visual_%s_%s_%d.png" % [tag, preset_id, Time.get_ticks_usec()]
	var output_dir := ProjectSettings.globalize_path("user://gpu_profiles")
	DirAccess.make_dir_recursive_absolute(output_dir)
	var error := image.save_png(path)
	if error != OK:
		print("NEX_PRESET_AB_FAIL save_png: " + str(error))
		get_tree().quit(2)
		return
	print("NEX_PRESET_AB_IMAGE %s %dx%d" % [
		ProjectSettings.globalize_path(path), image.get_width(), image.get_height(),
	])
	get_tree().quit(0)


func _start_capture() -> void:
	if not stage_valid:
		print("NEX_PRESET_AB_FAIL stage")
		get_tree().quit(2)
		return
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
		"scene": scene_label,
		"layout": scene_layout,
		"proxy_count": proxy_count,
		"effect_mode": "lights",
		"renderer": RenderingServer.get_current_rendering_method(),
		"driver": RenderingServer.get_current_rendering_driver_name(),
		"adapter": RenderingServer.get_video_adapter_name(),
	}
	if not session.begin(get_viewport(), context, true):
		print("NEX_PRESET_AB_FAIL begin: " + str(session.last_error))
		get_tree().quit(2)
		return
	print("NEX_PRESET_AB_START preset=%s scene=%s size=%s vsync=%d max_fps=%d" % [
		preset_id, scene_label, str(get_viewport().get_visible_rect().size),
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
