extends SceneTree

# NEX M08 scene composition: feeds the committed M02 scene-analysis bundle to
# the integrated CompositionPlanner. Planning only: no layer, viewport, shader,
# scene or renderer is created.
# godot --headless --path nex_modules/render2_5d/composition --script res://scene_composition.gd

const PLANNER := preload("res://composition_planner.gd")
const ANALYSIS_ENV := "NEX_M02_ANALYSIS_DIR"
const OUTPUT_ENV := "NEX_M08_COMPOSITION_OUTPUT"
const SOURCE_SHA := "d218525cbd7cd84b5c69f5e52577a6244f8733b6"
const MANIFEST_URI := "nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-analysis/runs.v1.json"


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	print("M08_SCENE_COMPOSITION_FAIL " + message)
	quit(2)


func _base_plan(depth: Dictionary, scene_sha: String) -> Dictionary:
	var passes: Dictionary = depth.get("passes", {})
	return {
		"plan_schema": "depth_composition.plan.v1",
		"opaque_count": passes.get("opaque", []).size(),
		"alpha_count": passes.get("alpha", []).size(),
		"overlay_count": passes.get("overlay", []).size(),
		"z_fight_risks": depth.get("z_fight_risks", []).size(),
		"alpha_over_critical": depth.get("alpha_over_critical", []).size(),
		"overlay_gameplay_conflicts": depth.get("overlay_gameplay_conflicts", []).size(),
		"plan_sha256": scene_sha,
	}


func _plan_scene(document: Dictionary, scene_sha: String) -> Dictionary:
	var planner = PLANNER.new()
	root.add_child(planner)
	planner.configure({})
	if not planner.set_base_plan(_base_plan(document["depth"], scene_sha)):
		_fail(document["scene_id"] + ": " + planner.last_error)
		return {}
	if not planner.set_policies({
		"depth_policy": 2,
		"conflict_policy": 0,
		"critical_guard": true,
		"hud_layer_id": "hud",
		"overlay_may_cover_gameplay": false,
	}):
		_fail(document["scene_id"] + ": " + planner.last_error)
		return {}
	var layers := [
		["background", 0, 0.4, 0, 1.0, false, false],
		["gameplay", 1, 1.0, 0, 1.0, true, false],
		["foreground", 2, 1.4, 0, 0.4, false, false],
		["hud", 3, 0.0, 0, 1.0, false, false],
	]
	for layer in layers:
		if not planner.register_layer(layer[0], layer[1], layer[2], layer[3], layer[4], layer[5], layer[6]):
			_fail(document["scene_id"] + ": " + planner.last_error)
			return {}
	for actor in document["sightline"]["actors"]:
		var role := -1
		if String(actor["id"]) == "player":
			role = 0
		elif String(actor["id"]) == "threat":
			role = 1
		if role >= 0 and not planner.register_critical_entity(String(actor["id"]), role, true):
			_fail(document["scene_id"] + ": " + planner.last_error)
			return {}
	var report: Dictionary = planner.plan()
	planner.queue_free()
	return report


func _run() -> void:
	var analysis_dir := OS.get_environment(ANALYSIS_ENV).strip_edges()
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if analysis_dir.is_empty() or output.is_empty():
		_fail("missing analysis dir or output path")
		return
	var manifest_path := analysis_dir + "/runs.v1.json"
	var manifest_text := FileAccess.get_file_as_string(manifest_path)
	if manifest_text.is_empty():
		_fail("cannot read analysis manifest")
		return
	var manifest = JSON.parse_string(manifest_text)
	if not manifest is Dictionary or String(manifest.get("schema_version", "")) != "m02_scene_analysis_runs.v1":
		_fail("manifest is not m02_scene_analysis_runs.v1")
		return
	var scenes: Array = []
	for run in manifest.get("runs", []):
		var scene_path := analysis_dir + "/" + String(run["file"])
		var scene_sha := FileAccess.get_sha256(scene_path)
		if scene_sha != String(run["sha256"]):
			_fail("scene hash mismatch: " + String(run["file"]))
			return
		var scene_text := FileAccess.get_file_as_string(scene_path)
		var document = JSON.parse_string(scene_text)
		if not document is Dictionary or String(document.get("schema_version", "")) != "m02_scene_analysis.v1":
			_fail("scene is not m02_scene_analysis.v1: " + String(run["file"]))
			return
		var report := _plan_scene(document, scene_sha)
		if report.is_empty():
			return
		scenes.append({
			"scene_id": String(document["scene_id"]),
			"scene_sha256": scene_sha,
			"report": report,
		})
	var result := {
		"schema_version": "m08_scene_composition_run.v1",
		"source_sha": SOURCE_SHA,
		"analysis_manifest_uri": MANIFEST_URI,
		"analysis_manifest_sha256": FileAccess.get_sha256(manifest_path),
		"scenes": scenes,
		"limitations": [
			"planning only; no layer, viewport, shader, scene or renderer is created",
			"the base 3D plan is the M02 scene-analysis bundle, not a rendered depth buffer",
			"layer roles and parallax values are reference defaults, not art direction",
			"no FPS, frame-time, visual-quality or game-feel claim",
		],
	}
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		_fail("cannot write output")
		return
	file.store_string(JSON.stringify(result, "  ") + "\n")
	file.close()
	print("M08_SCENE_COMPOSITION_OK %d scenes" % scenes.size())
	quit(0)
