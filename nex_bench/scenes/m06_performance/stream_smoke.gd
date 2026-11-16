extends SceneTree

# NEX M06-S05 StreamGuard smoke: async load states, cache, duplicate and
# failure handling. It measures cold/warm load times in this process only.

const STREAM_GUARD := preload("res://scenes/m06_performance/stream_guard.gd")
const OUTPUT_ENV := "NEX_M06_STREAM_OUTPUT"
const PATHS := [
	"res://scenes/base/corridor_static.tscn",
	"res://scenes/base/arena_combat.tscn",
	"res://scenes/base/dense_city.tscn",
]

var checks := 0
var failures: Array[String] = []


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var guard = STREAM_GUARD.new()
	root.add_child(guard)
	_check(guard.configure({"max_cache": 8}), "configure")
	_check(not guard.configure({"max_cache": 0}), "reject zero cache")
	for path in PATHS:
		_check(bool(guard.request(path)["accepted"]), "request " + path)
	_check(bool(guard.request(PATHS[0]).get("duplicate", false)), "duplicate request")
	var frames := 0
	while frames < 300:
		var update: Dictionary = guard.poll()
		if update["state"]["counts"]["loading"] == 0:
			break
		await process_frame
		frames += 1
	_check(frames < 300, "poll timeout")
	var state: Dictionary = guard.get_state()
	_check(int(state["counts"]["ready"]) == 3, "three ready")
	_check(int(state["counts"]["failed"]) == 0, "no failures")
	for path in PATHS:
		_check(guard.get_resource(path) != null, "resource cached " + path)
	var warm: Dictionary = guard.request(PATHS[0])
	_check(bool(warm.get("duplicate", false)) and String(warm["state"]) == "ready", "warm request")
	_check(not bool(guard.request("user://bad.tscn")["accepted"]), "reject non-res path")
	_check(not bool(guard.request("res://../escape.tscn")["accepted"]), "reject traversal")
	var missing: Dictionary = guard.request("res://does_not_exist_m06.tscn")
	_check(bool(missing["accepted"]), "missing accepted for async")
	for _index in range(30):
		guard.poll()
		if int(guard.get_state()["counts"]["failed"]) > 0:
			break
		await process_frame
	_check(int(guard.get_state()["counts"]["failed"]) >= 1, "missing failed")
	var timings: Array = []
	var entries: Dictionary = guard.get_entries()
	for path in PATHS:
		timings.append({"path": path, "elapsed_ms": float(entries[path].get("elapsed_ms", 0.0))})
	var document := {
		"schema_version": "m06_stream_smoke.v1",
		"source_sha": "c763319d04d0bf353c15db8378872bdf8fab1734",
		"checks": checks,
		"failures": failures,
		"verdict": "PASS" if failures.is_empty() else "FAIL",
		"frames_waited": frames,
		"state": guard.get_state(),
		"timings": timings,
		"limitations": [
			"cold/warm load of three small scenes in one process",
			"no scene streaming, prefetch policy or disk-pressure test",
			"audit remains ADMIN_SOLO / NOT_INDEPENDENT",
		],
	}
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if output.is_empty():
		output = ProjectSettings.globalize_path("user://m06_stream_smoke.json")
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		print("M06_STREAM_SMOKE_FAIL cannot write")
		quit(2)
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	if failures.is_empty():
		print("M06_STREAM_SMOKE_PASS %d checks" % checks)
		quit(0)
	else:
		print("M06_STREAM_SMOKE_FAIL " + ", ".join(failures))
		quit(2)
