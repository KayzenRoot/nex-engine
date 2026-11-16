extends SceneTree

# NEX M06-S09 VRAM Sentinel native smoke: engine video-memory monitor before
# and after loading the 19 M05 VFX reference textures. It is not device VRAM.

const VRAM_SENTINEL := preload("res://scenes/m06_performance/vram_sentinel.gd")
const OUTPUT_ENV := "NEX_M06_VRAM_OUTPUT"
const TEXTURE_DIR := "res://gpu_profile/evidence/windows-rtx5050-2026-11-15-m05-vfx"

var checks := 0
var failures: Array[String] = []
var _textures: Array[ImageTexture] = []


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var sentinel = VRAM_SENTINEL.new()
	_check(sentinel.configure({"budget_bytes": 6000000000, "warn_ratio": 0.8,
		"critical_ratio": 0.92, "hysteresis_ratio": 0.03}), "configure")
	await process_frame
	await process_frame
	var before: Dictionary = sentinel.sample()
	_check(String(before["status"]) in ["MEASURED", "UNAVAILABLE"], "before sample status")
	var files := DirAccess.get_files_at(TEXTURE_DIR)
	var loaded := 0
	for name in files:
		if not String(name).ends_with(".png"):
			continue
		var image := Image.load_from_file(TEXTURE_DIR + "/" + String(name))
		if image == null or image.is_empty():
			continue
		var texture := ImageTexture.create_from_image(image)
		if texture != null:
			_textures.append(texture)
			loaded += 1
	for _index in range(5):
		await process_frame
	var after: Dictionary = sentinel.sample()
	_check(String(after["status"]) in ["MEASURED", "UNAVAILABLE"], "after sample status")
	_check(loaded >= 19, "loaded 19 textures")
	var delta := 0
	if String(before["status"]) == "MEASURED" and String(after["status"]) == "MEASURED":
		delta = int(after["video_bytes"]) - int(before["video_bytes"])
	var evaluation: Dictionary = sentinel.evaluate(after)
	_check(String(evaluation["state"]) in ["OK", "WARN", "CRITICAL", "UNKNOWN"], "evaluation state")
	_check(String(sentinel.evaluate({"status": "UNAVAILABLE"})["state"]) == "UNKNOWN", "unavailable state")
	_check(sentinel.configure({"budget_bytes": 6000000000}), "reconfigure")
	_check(not sentinel.configure({"warn_ratio": 0.95, "critical_ratio": 0.9}), "reject inverted ratios")
	_check(int(sentinel.get_state()["budget_bytes"]) == 6000000000, "budget retained")
	var document := {
		"schema_version": "m06_vram_smoke.v1",
		"source_sha": "c763319d04d0bf353c15db8378872bdf8fab1734",
		"checks": checks,
		"failures": failures,
		"verdict": "PASS" if failures.is_empty() else "FAIL",
		"textures_loaded": loaded,
		"before": before,
		"after": after,
		"delta_bytes": delta,
		"evaluation": evaluation,
		"limitations": [
			"RENDER_VIDEO_MEM_USED is engine-reported allocation, not total device VRAM",
			"textures are 1920x1080 PNGs loaded in one process",
			"no OOM, eviction or recovery test",
			"audit remains ADMIN_SOLO / NOT_INDEPENDENT",
		],
	}
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if output.is_empty():
		output = ProjectSettings.globalize_path("user://m06_vram_smoke.json")
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		print("M06_VRAM_SMOKE_FAIL cannot write")
		quit(2)
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	if failures.is_empty():
		print("M06_VRAM_SMOKE_PASS %d checks textures=%d delta=%d" % [checks, loaded, delta])
		quit(0)
	else:
		print("M06_VRAM_SMOKE_FAIL " + ", ".join(failures))
		quit(2)
