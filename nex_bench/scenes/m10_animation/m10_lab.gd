extends Node3D

# NEX M10 animation/feedback lab: AnimationPlayer + AnimationTree blending,
# hit reaction, visual hit-stop, smooth camera and M05 VFX synchronization.
# Native captures and measurements only; no gameplay authority.

const SESSION_SCRIPT := "res://gpu_profile/session.gd"
const MODE_ENV := "NEX_M10_MODE"
const VISUAL_ENV := "NEX_M10_VISUAL"
const VISUAL_OUTPUT_ENV := "NEX_M10_VISUAL_OUTPUT"
const AUTORUN_ENV := "NEX_M10_AUTORUN"
const WIDTH_ENV := "NEX_M10_WIDTH"
const HEIGHT_ENV := "NEX_M10_HEIGHT"
const SOURCE_SHA_ENV := "NEX_GPU_PROFILE_SOURCE_SHA"
const WARMUP_FRAMES := 120
const MODES := ["baseline", "blend", "attack", "hit", "hitstop", "camera",
	"vfx", "quality_low", "quality_high"]
const SPELL_FX := preload("res://scenes/m05_vfx/spell_fx.gd")
const FX_LIBRARY := preload("res://scenes/m05_vfx/fx_library.gd")

var session: RefCounted
var mode := "baseline"
var camera: Camera3D
var anim_player: AnimationPlayer
var anim_tree: AnimationTree
var rig: Skeleton3D
var attachment: BoneAttachment3D
var proxies: Array[Node3D] = []
var proxy_player: AnimationPlayer
var controller: Node
var vfx_spawned := false
var hitstop_done := false
var elapsed := 0.0
var _metrics_reported := false


func _ready() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 240
	if OS.get_environment("NEX_M10_NATIVE_RESOLUTION") == "1":
		get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	var width := int(OS.get_environment(WIDTH_ENV)) if not OS.get_environment(WIDTH_ENV).is_empty() else 1920
	var height := int(OS.get_environment(HEIGHT_ENV)) if not OS.get_environment(HEIGHT_ENV).is_empty() else 1080
	DisplayServer.window_set_size(Vector2i(width, height))
	mode = OS.get_environment(MODE_ENV).strip_edges()
	if mode.is_empty():
		mode = "baseline"
	if not MODES.has(mode):
		push_error("NEX_M10: unknown mode " + mode)
		get_tree().quit(2)
		return
	_build_environment()
	_build_camera()
	_build_rig()
	_build_animations()
	_build_tree()
	match mode:
		"blend":
			anim_tree.set("parameters/blend/blend_amount", 0.5)
		"attack", "hitstop", "camera", "vfx":
			anim_tree.set("parameters/blend/blend_amount", 1.0)
		"hit":
			anim_tree.active = false
			anim_player.play("hit")
		"quality_low":
			anim_tree.set("parameters/blend/blend_amount", 0.0)
		"quality_high":
			anim_tree.set("parameters/blend/blend_amount", 1.0)
			_build_proxies(12)
	if mode in ["vfx", "quality_high"]:
		controller = SPELL_FX.new()
		controller.name = "M10SpellFX"
		add_child(controller)
		if not controller.configure({"max_active": 32, "max_per_vfx": 16}):
			push_error("NEX_M10: spellfx configure")
			get_tree().quit(2)
			return
	print("NEX_M10_LAB " + JSON.stringify({
		"mode": mode, "bones": rig.get_bone_count(), "proxies": proxies.size(),
		"blend": float(anim_tree.get("parameters/blend/blend_amount")),
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
	environment.ambient_light_energy = 0.5
	var world := WorldEnvironment.new()
	world.environment = environment
	add_child(world)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52.0, -38.0, 0.0)
	sun.light_energy = 1.3
	add_child(sun)


func _build_camera() -> void:
	camera = Camera3D.new()
	camera.name = "M10Camera"
	camera.position = Vector3(4.0, 3.2, 4.0)
	add_child(camera)
	camera.look_at(Vector3(0.0, 1.2, 0.0), Vector3.UP)
	camera.fov = 45.0
	camera.current = true


func _build_rig() -> void:
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(12.0, 12.0)
	ground.mesh = plane
	var ground_material := StandardMaterial3D.new()
	ground_material.albedo_color = Color("#26354F")
	ground.material_override = ground_material
	add_child(ground)
	rig = Skeleton3D.new()
	rig.name = "Rig"
	add_child(rig)
	rig.add_bone("root")
	rig.add_bone("arm")
	rig.set_bone_parent(1, 0)
	rig.set_bone_pose_position(0, Vector3(0.0, 0.0, 0.0))
	rig.set_bone_pose_position(1, Vector3(0.0, 1.2, 0.0))
	var body := MeshInstance3D.new()
	var body_mesh := BoxMesh.new()
	body_mesh.size = Vector3(0.8, 1.2, 0.5)
	body.mesh = body_mesh
	body.position = Vector3(0.0, 0.6, 0.0)
	var body_material := StandardMaterial3D.new()
	body_material.albedo_color = Color("#9AA8C0")
	body.material_override = body_material
	add_child(body)
	attachment = BoneAttachment3D.new()
	attachment.name = "ArmAttachment"
	attachment.bone_name = "arm"
	rig.add_child(attachment)
	var arm := MeshInstance3D.new()
	var arm_mesh := BoxMesh.new()
	arm_mesh.size = Vector3(0.28, 1.0, 0.28)
	arm.mesh = arm_mesh
	arm.position = Vector3(0.0, 0.5, 0.0)
	var arm_material := StandardMaterial3D.new()
	arm_material.albedo_color = Color("#E2B36B")
	arm.material_override = arm_material
	attachment.add_child(arm)


func _build_animations() -> void:
	anim_player = AnimationPlayer.new()
	anim_player.name = "AnimationPlayer"
	add_child(anim_player)
	var library := AnimationLibrary.new()
	var idle := Animation.new()
	idle.length = 1.0
	idle.loop_mode = Animation.LOOP_LINEAR
	var idle_track := idle.add_track(Animation.TYPE_VALUE)
	idle.track_set_path(idle_track, "Rig/ArmAttachment:rotation")
	idle.track_insert_key(idle_track, 0.0, Vector3(0.0, 0.0, 0.0))
	idle.track_insert_key(idle_track, 0.5, Vector3(0.0, 0.0, 0.18))
	idle.track_insert_key(idle_track, 1.0, Vector3(0.0, 0.0, 0.0))
	library.add_animation("idle", idle)
	var attack := Animation.new()
	attack.length = 0.45
	attack.loop_mode = Animation.LOOP_NONE
	var attack_track := attack.add_track(Animation.TYPE_VALUE)
	attack.track_set_path(attack_track, "Rig/ArmAttachment:rotation")
	attack.track_insert_key(attack_track, 0.0, Vector3(0.0, 0.0, 0.0))
	attack.track_insert_key(attack_track, 0.18, Vector3(0.0, 0.0, -1.2))
	attack.track_insert_key(attack_track, 0.45, Vector3(0.0, 0.0, -0.2))
	library.add_animation("attack", attack)
	var hit := Animation.new()
	hit.length = 0.35
	hit.loop_mode = Animation.LOOP_NONE
	var hit_track := hit.add_track(Animation.TYPE_VALUE)
	hit.track_set_path(hit_track, "Rig:rotation")
	hit.track_insert_key(hit_track, 0.0, Vector3(0.0, 0.0, 0.0))
	hit.track_insert_key(hit_track, 0.08, Vector3(0.0, 0.0, 0.35))
	hit.track_insert_key(hit_track, 0.35, Vector3(0.0, 0.0, 0.0))
	library.add_animation("hit", hit)
	anim_player.add_animation_library("", library)
	anim_player.play("idle")


func _build_tree() -> void:
	var tree := AnimationNodeBlendTree.new()
	var idle_node := AnimationNodeAnimation.new()
	idle_node.animation = "idle"
	tree.add_node("idle", idle_node)
	var attack_node := AnimationNodeAnimation.new()
	attack_node.animation = "attack"
	tree.add_node("attack", attack_node)
	var blend := AnimationNodeBlend2.new()
	tree.add_node("blend", blend, Vector2(0.0, 0.0))
	tree.connect_node("blend", 0, "idle")
	tree.connect_node("blend", 1, "attack")
	tree.connect_node("output", 0, "blend")
	anim_tree = AnimationTree.new()
	anim_tree.name = "AnimationTree"
	anim_tree.tree_root = tree
	add_child(anim_tree)
	anim_tree.anim_player = anim_tree.get_path_to(anim_player)
	anim_tree.active = true


func _build_proxies(total: int) -> void:
	proxy_player = AnimationPlayer.new()
	proxy_player.name = "ProxyAnimationPlayer"
	add_child(proxy_player)
	var proxy_library := AnimationLibrary.new()
	var animation := Animation.new()
	animation.length = 1.0
	animation.loop_mode = Animation.LOOP_LINEAR
	for index in range(total):
		var proxy := MeshInstance3D.new()
		proxy.name = "Proxy_%02d" % index
		var mesh := BoxMesh.new()
		mesh.size = Vector3(0.25, 0.8, 0.25)
		proxy.mesh = mesh
		var material := StandardMaterial3D.new()
		material.albedo_color = Color("#7E8CA3")
		proxy.material_override = material
		proxy.position = Vector3(-2.5 + float(index % 6) * 0.9, 0.4, -1.5 + float(index / 6) * 0.9)
		add_child(proxy)
		proxies.append(proxy)
		var track := animation.add_track(Animation.TYPE_VALUE)
		animation.track_set_path(track, "Proxy_%02d:rotation" % index)
		animation.track_insert_key(track, 0.0, Vector3(0.0, 0.0, 0.0))
		animation.track_insert_key(track, 0.5, Vector3(0.0, 0.0, 0.4))
		animation.track_insert_key(track, 1.0, Vector3(0.0, 0.0, 0.0))
	proxy_library.add_animation("proxy_idle", animation)
	proxy_player.add_animation_library("", proxy_library)
	proxy_player.play("proxy_idle")


func _process(delta: float) -> void:
	elapsed += delta
	if mode == "camera":
		var target := Vector3(4.0 + sin(elapsed * 0.6) * 1.2, 3.2 + cos(elapsed * 0.4) * 0.4, 4.0)
		camera.position = camera.position.lerp(target, 0.08)
		camera.look_at(Vector3(0.0, 1.2, 0.0), Vector3.UP)
	if mode == "hitstop" and not hitstop_done and elapsed > 0.25:
		hitstop_done = true
		anim_player.speed_scale = 0.0
		await get_tree().create_timer(0.08, true, false, true).timeout
		anim_player.speed_scale = 1.0
	if mode in ["vfx", "quality_high"] and not vfx_spawned and elapsed > 0.2:
		_vfx_spawned()
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
		print("NEX_M10_FAIL export")
		get_tree().quit(3)
		return
	print("NEX_M10_CAPTURE " + path)
	get_tree().quit(0)


func _vfx_spawned() -> void:
	vfx_spawned = true
	if controller == null:
		return
	var result: Dictionary = controller.submit({
		"event_id": "m10-impact",
		"vfx_id": "impact-burst",
		"position": [0.0, 1.2, 0.0],
		"seed": 1010,
		"lifetime_ms": 800,
		"quality_tier": "high",
		"priority": 5,
		"gameplay_authority": {"damage_owner": "gameplay", "hit_detection": "gameplay", "cancel_on_death": true},
	})
	if not bool(result.get("accepted", false)):
		return
	var impact := FX_LIBRARY.create_impact()
	impact.position = Vector3(0.0, 1.2, 0.0)
	add_child(impact)


func _start_visual_capture() -> void:
	await get_tree().process_frame
	for _index in range(WARMUP_FRAMES):
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	if image == null or image.is_empty():
		print("NEX_M10_FAIL image")
		get_tree().quit(2)
		return
	image.flip_y()
	var path := OS.get_environment(VISUAL_OUTPUT_ENV).strip_edges()
	if path.is_empty():
		path = ProjectSettings.globalize_path("user://m10_lab_%s.png" % mode)
	var error := image.save_png(path)
	if error != OK:
		print("NEX_M10_FAIL save_png: " + str(error))
		get_tree().quit(2)
		return
	print("NEX_M10_IMAGE %s %dx%d" % [ProjectSettings.globalize_path(path), image.get_width(), image.get_height()])
	get_tree().quit(0)


func _start_capture() -> void:
	var script := load(SESSION_SCRIPT) as Script
	if script == null:
		print("NEX_M10_FAIL session_script")
		get_tree().quit(2)
		return
	session = script.new() as RefCounted
	await get_tree().process_frame
	await get_tree().process_frame
	var context := {
		"source_sha": OS.get_environment(SOURCE_SHA_ENV).strip_edges().to_lower(),
		"scene": "M10 Animation Lab",
		"layout": "M10 animation and feedback lab",
		"proxy_count": 100,
		"effect_mode": "lights",
		"renderer": RenderingServer.get_current_rendering_method(),
		"driver": RenderingServer.get_current_rendering_driver_name(),
		"adapter": RenderingServer.get_video_adapter_name(),
	}
	if not session.begin(get_viewport(), context, true):
		print("NEX_M10_FAIL begin: " + str(session.last_error))
		get_tree().quit(2)
		return
	print("NEX_M10_START mode=%s scene=%s size=%s vsync=%d max_fps=%d" % [
		mode, context["scene"], str(get_viewport().get_visible_rect().size),
		DisplayServer.window_get_vsync_mode(), Engine.max_fps,
	])


func _report_metrics() -> void:
	await RenderingServer.frame_post_draw
	print("NEX_M10_LAB_METRICS " + JSON.stringify({
		"mode": mode,
		"draw_calls": int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),
		"objects": int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)),
		"primitives": int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)),
	}))
