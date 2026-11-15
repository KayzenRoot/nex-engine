extends SceneTree

# NEX M02-S04 TAA sequence analyzer: 4x4 luminance regions from five camera
# motion frames, evaluated by the integrated TemporalGuardAnalyzer.
# godot --headless --path nex_bench --script res://scenes/m02_temporal/analyze_taa.gd

const ANALYZER := preload("res://scenes/m02_analysis/temporal_guard_analyzer.gd")
const DIR_ENV := "NEX_M02_TAA_DIR"
const OUTPUT_ENV := "NEX_M02_TAA_OUTPUT"
const MODE_ENV := "NEX_M02_TAA_MODE"
const SOURCE_SHA := "fa1adae7ab67e38c2556d126627006c338e2e8f4"
const GRID := 4
const FRAMES := 5


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	print("M02_TAA_ANALYSIS_FAIL " + message)
	quit(2)


func _regions(path: String) -> Dictionary:
	var image := Image.load_from_file(ProjectSettings.globalize_path(path))
	if image == null:
		return {}
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
				"edge": true,
			}
	return regions


func _run() -> void:
	var directory := OS.get_environment(DIR_ENV).strip_edges()
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	var mode := OS.get_environment(MODE_ENV).strip_edges()
	if directory.is_empty() or output.is_empty():
		_fail("missing directory or output")
		return
	var frames: Array = []
	for index in range(FRAMES):
		var regions := _regions(directory + "/frame_%02d.png" % index)
		if regions.is_empty():
			_fail("cannot load frame %d" % index)
			return
		frames.append(regions)
	var analyzer = ANALYZER.new()
	root.add_child(analyzer)
	if not analyzer.configure({}):
		_fail("configure: " + analyzer.last_error)
		return
	var report: Dictionary = analyzer.analyze(frames, {"render_scale": 1.0, "prefer_native": true})
	var document := {
		"schema_version": "m02_taa_analysis.v1",
		"source_sha": SOURCE_SHA,
		"mode": mode,
		"frames": FRAMES,
		"regions": GRID * GRID,
		"report": report,
	}
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		_fail("cannot write output")
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	print("M02_TAA_ANALYSIS_OK " + String(report.get("verdict", "")))
	quit(0)
