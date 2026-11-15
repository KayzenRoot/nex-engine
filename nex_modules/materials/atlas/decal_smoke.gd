extends SceneTree

# NEX M04-S05 DecalSurface smoke: two mock consumers, validation, surface and
# decal budgets, preemption and expiry. No Decal3D is created here.

const SURFACE := preload("res://decal_surface.gd")
const OUTPUT_ENV := "NEX_M04_DECAL_OUTPUT"
const SOURCE_SHA := "e09cce2f4332e00a0f51eacb346f5763fe228db9"

var checks := 0
var failures: Array[String] = []


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _request(request_id: String, surface: String, priority := 3, duration := 400) -> Dictionary:
	return {
		"request_id": request_id,
		"effect_id": "fx-" + request_id,
		"surface_tag": surface,
		"position": [0.0, 0.0, 0.0],
		"projection": [2.0, 2.0, 2.0],
		"duration_ms": duration,
		"fade_ms": 200,
		"priority": priority,
		"blend": "mix",
	}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if output.is_empty():
		print("M04_DECAL_SMOKE_FAIL missing output")
		quit(2)
		return
	var surface = SURFACE.new()
	root.add_child(surface)
	_check(surface.configure({"max_decals": 3, "max_per_surface": 2}), "configure")
	_check(bool(surface.submit(_request("hit-mark", "floor"))["accepted"]), "floor mark accepted")
	_check(not bool(surface.submit(_request("hit-mark", "floor"))["accepted"]), "duplicate rejected")
	var invalid := _request("bad-projection", "floor")
	invalid["projection"] = [1.0]
	_check(not bool(surface.submit(invalid)["accepted"]), "invalid projection rejected")
	_check(bool(surface.submit(_request("wall-mark", "wall"))["accepted"]), "wall mark accepted")
	_check(bool(surface.submit(_request("floor-mark-2", "floor"))["accepted"]), "floor second accepted")
	_check(not bool(surface.submit(_request("floor-mark-3", "floor"))["accepted"]), "surface full rejected")
	surface.configure({"max_decals": 2, "max_per_surface": 8})
	surface.clear()
	_check(bool(surface.submit(_request("low", "floor", 1))["accepted"]), "low accepted")
	_check(bool(surface.submit(_request("high", "floor", 8))["accepted"]), "high accepted")
	var preempt: Dictionary = surface.submit(_request("critical", "wall", 10))
	_check(bool(preempt["accepted"]) and preempt["preempted"] == ["low"], "preemption")
	var expired: Array = surface.tick(600)
	_check(expired.size() == 2, "expiry")
	_check(surface.get_state()["active"] == 0, "state empty")
	var document := {
		"schema_version": "m04_decal_smoke.v1",
		"source_sha": SOURCE_SHA,
		"checks": checks,
		"failures": failures,
		"verdict": "PASS" if failures.is_empty() else "FAIL",
		"limitations": [
			"planning only; no Decal3D is created by this smoke",
			"priority is the only relevance signal in this MVP",
			"no overdraw or GPU cost is measured",
		],
	}
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		print("M04_DECAL_SMOKE_FAIL cannot write")
		quit(2)
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	if failures.is_empty():
		print("M04_DECAL_SMOKE_PASS %d checks" % checks)
		quit(0)
	else:
		print("M04_DECAL_SMOKE_FAIL " + ", ".join(failures))
		quit(2)
