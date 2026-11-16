extends SceneTree

# NEX M05-S01 SpellFX smoke: two mock consumers, idempotency, authority,
# budgets, cancellation and expiry. No particle or light is created here.

const SPELL_FX := preload("res://scenes/m05_vfx/spell_fx.gd")
const OUTPUT_ENV := "NEX_M05_SPELLFX_OUTPUT"
const SOURCE_SHA := "dd840f86023057a4dc8af92148cdf36911175613"

var checks := 0
var failures: Array[String] = []


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _request(event_id: String, vfx_id: String, priority := 3, lifetime := 400) -> Dictionary:
	return {
		"event_id": event_id,
		"vfx_id": vfx_id,
		"position": [0.0, 1.0, 0.0],
		"seed": 42,
		"lifetime_ms": lifetime,
		"quality_tier": "high",
		"priority": priority,
		"gameplay_authority": {"damage_owner": "gameplay", "hit_detection": "gameplay", "cancel_on_death": true},
	}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if output.is_empty():
		print("M05_SPELLFX_SMOKE_FAIL missing output")
		quit(2)
		return
	var bridge = SPELL_FX.new()
	root.add_child(bridge)
	_check(bridge.configure({"max_active": 3, "max_per_vfx": 2}), "configure")
	_check(bool(bridge.submit(_request("cast-fire", "fire-burst"))["accepted"]), "fire accepted")
	var duplicate: Dictionary = bridge.submit(_request("cast-fire", "fire-burst"))
	_check(bool(duplicate["accepted"]) and bool(duplicate["duplicate"]), "duplicate idempotent")
	var invalid := _request("bad-authority", "fire-burst")
	invalid["gameplay_authority"]["damage_owner"] = "visual_only"
	_check(not bool(bridge.submit(invalid)["accepted"]), "visual-only damage rejected")
	_check(bool(bridge.submit(_request("cast-frost", "frost-nova"))["accepted"]), "frost accepted")
	_check(bool(bridge.submit(_request("cast-fire-2", "fire-burst"))["accepted"]), "second fire accepted")
	_check(not bool(bridge.submit(_request("cast-fire-3", "fire-burst"))["accepted"]), "vfx budget rejected")
	_check(not bool(bridge.submit(_request("cast-lightning", "lightning"))["accepted"]), "active budget rejected")
	_check(bridge.cancel("cast-frost"), "cancel accepted")
	_check(not bridge.cancel("missing-event"), "cancel missing rejected")
	var expired: Array = bridge.tick(600)
	_check(expired.size() == 2, "expiry")
	_check(bridge.get_state()["active"] == 0, "state empty")
	var document := {
		"schema_version": "m05_spellfx_smoke.v1",
		"source_sha": SOURCE_SHA,
		"checks": checks,
		"failures": failures,
		"verdict": "PASS" if failures.is_empty() else "FAIL",
		"limitations": [
			"planning only; no particle, light, decal or renderer is created",
			"gameplay authority is validated as data, not implemented",
			"no FPS, frame-time or quality claim",
		],
	}
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		print("M05_SPELLFX_SMOKE_FAIL cannot write")
		quit(2)
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	if failures.is_empty():
		print("M05_SPELLFX_SMOKE_PASS %d checks" % checks)
		quit(0)
	else:
		print("M05_SPELLFX_SMOKE_FAIL " + ", ".join(failures))
		quit(2)
