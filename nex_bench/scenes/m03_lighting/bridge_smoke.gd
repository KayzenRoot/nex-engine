extends SceneTree

# NEX M03-S05 LightBridge smoke: two mock consumers, validation, budget,
# preemption, expiry and fallback. No light is created or rendered.
# godot --headless --path nex_bench --script res://scenes/m03_lighting/bridge_smoke.gd

const BRIDGE := preload("res://scenes/m03_lighting/light_bridge.gd")
const OUTPUT_ENV := "NEX_M03_BRIDGE_OUTPUT"
const SOURCE_SHA := "6be39d49d8769ff46a98990c6818c8132e9e5a1d"

var checks := 0
var failures: Array[String] = []


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _request(request_id: String, priority: int, group: String, shadow := "soft", duration := 400) -> Dictionary:
	return {
		"request_id": request_id,
		"effect_id": "fx-" + request_id,
		"position": [0.0, 2.0, 0.0],
		"color": [1.0, 0.5, 0.2, 1.0],
		"radius": 4.0,
		"intensity": 2.0,
		"duration_ms": duration,
		"priority": priority,
		"shadow_policy": shadow,
		"budget_group": group,
	}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if output.is_empty():
		print("M03_LIGHT_BRIDGE_SMOKE_FAIL missing output")
		quit(2)
		return
	var bridge = BRIDGE.new()
	root.add_child(bridge)
	_check(bridge.configure({"max_active": 4, "max_per_group": 3, "timeout_ms": 500}), "configure")
	var first: Dictionary = bridge.submit(_request("spell-impact", 5, "combat", "soft", 400))
	_check(bool(first["accepted"]), "spell accepted")
	_check(not bool(bridge.submit(_request("spell-impact", 5, "combat"))["accepted"]), "duplicate rejected")
	var invalid := _request("bad-radius", 3, "ambient")
	invalid["radius"] = 99.0
	_check(not bool(bridge.submit(invalid)["accepted"]), "invalid radius rejected")
	_check(bool(bridge.submit(_request("torch-flicker", 2, "ambient", "none", 300))["accepted"]), "torch accepted")
	_check(bool(bridge.submit(_request("hit-flash", 4, "combat", "none", 200))["accepted"]), "flash accepted")
	_check(bool(bridge.submit(_request("combat-extra", 3, "combat", "none", 200))["accepted"]), "extra accepted")
	_check(not bool(bridge.submit(_request("group-overflow", 4, "combat", "none", 200))["accepted"]), "group full rejected")
	bridge.configure({"max_active": 2, "max_per_group": 8})
	bridge.clear()
	_check(bool(bridge.submit(_request("low-priority", 1, "ambient"))["accepted"]), "low accepted")
	_check(bool(bridge.submit(_request("high-priority", 9, "combat"))["accepted"]), "high accepted")
	var preempt: Dictionary = bridge.submit(_request("critical", 10, "combat"))
	_check(bool(preempt["accepted"]) and preempt["preempted"] == ["low-priority"], "preemption")
	var expired: Array = bridge.tick(600)
	_check(expired.size() == 2, "expiry")
	var state: Dictionary = bridge.get_state()
	_check(state["active"] == 0, "state empty")
	var document := {
		"schema_version": "m03_light_bridge_smoke.v1",
		"source_sha": SOURCE_SHA,
		"checks": checks,
		"failures": failures,
		"verdict": "PASS" if failures.is_empty() else "FAIL",
		"limitations": [
			"planning only; no light, shadow map or renderer is created",
			"priority is the only relevance signal in this MVP",
			"timeout/fallback is deterministic in milliseconds, not a frame-time measurement",
		],
	}
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		print("M03_LIGHT_BRIDGE_SMOKE_FAIL cannot write")
		quit(2)
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	if failures.is_empty():
		print("M03_LIGHT_BRIDGE_SMOKE_PASS %d checks" % checks)
		quit(0)
	else:
		print("M03_LIGHT_BRIDGE_SMOKE_FAIL " + ", ".join(failures))
		quit(2)
