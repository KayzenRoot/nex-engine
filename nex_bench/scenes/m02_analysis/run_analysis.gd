extends SceneTree

# NEX M02 analysis integration: sightline, depth and temporal prototypes over
# real M01 scene geometry and integrated static frames. Headless, no rendering.

const SIGHTLINE := preload("res://scenes/m02_analysis/sightline_controller.gd")
const DEPTH := preload("res://scenes/m02_analysis/depth_composition_solver.gd")
const TEMPORAL := preload("res://scenes/m02_analysis/temporal_guard_analyzer.gd")
const SCENE_ENV := "NEX_M02_ANALYSIS_SCENE"
const OUTPUT_ENV := "NEX_M02_ANALYSIS_OUTPUT"
const TEMPORAL_DIR := "res://gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-temporal"
const SCENES := {
	"corridor_static": "res://scenes/base/corridor_static.tscn",
	"arena_combat": "res://scenes/base/arena_combat.tscn",
	"dense_city": "res://scenes/base/dense_city.tscn",
}
const MAX_OCCLUDERS := 8
const MAX_PRIMITIVES := 16
const GRID := 4


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	print("NEX_M02_ANALYSIS_FAIL " + message)
	quit(2)


func _world_aabb(mesh_instance: MeshInstance3D) -> AABB:
	var local: AABB = mesh_instance.mesh.get_aabb()
	var xform := mesh_instance.global_transform
	var result := AABB(xform * local.position, Vector3.ZERO)
	for index in range(8):
		var corner := local.position + Vector3(
			local.size.x if (index & 1) else 0.0,
			local.size.y if (index & 2) else 0.0,
			local.size.z if (index & 4) else 0.0,
		)
		result = result.expand(xform * corner)
	return result


func _region_frames(scene_id: String) -> Array:
	var frames: Array = []
	for frame_index in range(5):
		var path := "%s/%s_ab-low_frame_%02d.png" % [TEMPORAL_DIR, scene_id, frame_index]
		var image := Image.load_from_file(ProjectSettings.globalize_path(path))
		if image == null:
			_fail("cannot load " + path)
			return []
		var regions := {}
		for ry in range(GRID):
			for rx in range(GRID):
				var px := int((float(rx) + 0.5) * float(image.get_width()) / float(GRID))
				var py := int((float(ry) + 0.5) * float(image.get_height()) / float(GRID))
				var color := image.get_pixel(px, py)
				regions["r%d_%d" % [rx, ry]] = {
					"luminance": (color.r + color.g + color.b) / 3.0,
					"motion": [0.0, 0.0],
					"alpha": 1.0,
					"edge": false,
				}
		frames.append(regions)
	return frames


func _run() -> void:
	var scene_id := OS.get_environment(SCENE_ENV).strip_edges()
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if not SCENES.has(scene_id):
		_fail("unknown scene: " + scene_id)
		return
	if output.is_empty():
		_fail("missing output path")
		return
	var packed := load(SCENES[scene_id]) as PackedScene
	if packed == null:
		_fail("cannot load scene")
		return
	var scene := packed.instantiate()
	root.add_child(scene)
	await process_frame
	var meshes := scene.find_children("*", "MeshInstance3D", true, false)
	var boxes: Array = []
	for mesh in meshes:
		var box := _world_aabb(mesh)
		if box.size.x > 0.1 and box.size.y > 0.1 and box.size.z > 0.1:
			boxes.append(box)
	boxes.sort_custom(func(a, b): return a.get_volume() > b.get_volume())
	var cameras := scene.find_children("*", "Camera3D", true, false)
	if cameras.is_empty():
		_fail("scene has no camera")
		return
	var camera := cameras[0] as Camera3D
	var camera_position := camera.global_position
	var target := Vector3.ZERO

	var sight = SIGHTLINE.new()
	root.add_child(sight)
	if not sight.configure({}):
		_fail("sightline configure: " + sight.last_error)
		return
	sight.set_camera_position(camera_position)
	var occluders: Array = []
	for index in range(min(MAX_OCCLUDERS, boxes.size())):
		var id := "mesh_%02d" % index
		if sight.register_occluder(id, boxes[index], 2 if index % 3 == 0 else 0, false):
			occluders.append(id)
	var focus_box: AABB = boxes[0]
	var focus := focus_box.get_center()
	var forward := (focus - camera_position).normalized()
	if not sight.set_actors([
		{"id": "player", "priority": 0, "position": focus},
		{"id": "threat", "priority": 1, "position": focus + forward * 2.0},
		{"id": "decor", "priority": 2, "position": focus - forward * 2.0},
	]):
		_fail("sightline actors: " + sight.last_error)
		return
	for step in range(10):
		sight.update(0.05)
	var sight_state: Dictionary = sight.get_state()

	var depth = DEPTH.new()
	root.add_child(depth)
	if not depth.configure({}):
		_fail("depth configure: " + depth.last_error)
		return
	var direction := (target - camera_position).normalized()
	if not depth.set_camera(camera_position, direction):
		_fail("depth camera: " + depth.last_error)
		return
	var primitives: Array = []
	for index in range(min(MAX_PRIMITIVES, boxes.size())):
		var box: AABB = boxes[index]
		var radius := maxf(box.size.x, maxf(box.size.y, box.size.z)) * 0.5
		var id := "mesh_%02d" % index
		if depth.register_primitive(id, 0, box.get_center(), maxf(radius, 0.1), index % 5 == 0, false):
			primitives.append(id)
	var plan: Dictionary = depth.plan()

	var temporal = TEMPORAL.new()
	root.add_child(temporal)
	if not temporal.configure({}):
		_fail("temporal configure: " + temporal.last_error)
		return
	var analysis: Dictionary = temporal.analyze(_region_frames(scene_id), {})

	var report := {
		"schema_version": "m02_scene_analysis.v1",
		"scene_id": scene_id,
		"mesh_count": meshes.size(),
		"occluders_used": occluders.size(),
		"primitives_used": primitives.size(),
		"camera_position": [camera_position.x, camera_position.y, camera_position.z],
		"sightline": {
			"summary": sight_state.get("summary", {}),
			"actors": sight_state.get("actors", []),
			"occluders": sight_state.get("occluders", []),
		},
		"depth": {
			"passes": plan.get("passes", {}),
			"z_fight_risks": plan.get("z_fight_risks", []),
			"alpha_over_critical": plan.get("alpha_over_critical", []),
			"overlay_gameplay_conflicts": plan.get("overlay_gameplay_conflicts", []),
			"limitations": plan.get("limitations", []),
		},
		"temporal": {
			"verdict": analysis.get("verdict"),
			"action": analysis.get("action"),
			"metrics": analysis.get("metrics", {}),
			"frames": analysis.get("frames"),
			"regions": analysis.get("regions"),
			"limitations": analysis.get("limitations", []),
		},
		"limitations": [
			"headless analysis over real scene AABBs and static frames; no rendering",
			"meshes are approximated as AABB/sphere primitives",
			"single deterministic actor layout per scene",
			"temporal analysis uses 4x4 luminance regions from static ab-low frames",
		],
	}
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		_fail("cannot write output")
		return
	file.store_string(JSON.stringify(report, "  ") + "\n")
	file.close()
	print("NEX_M02_ANALYSIS_OK " + output)
	quit(0)
