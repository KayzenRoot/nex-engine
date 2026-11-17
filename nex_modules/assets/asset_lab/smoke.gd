extends SceneTree

# NEX M11 asset-tools smoke: manifest, cook plan, license ledger and quality.
# Deterministic fixtures only; no asset is imported, cooked or written.

const ASSET_MANIFEST := preload("res://asset_manifest.gd")
const COOK_PLANNER := preload("res://cook_planner.gd")
const LICENSE_LEDGER := preload("res://license_ledger.gd")
const QUALITY_GATE := preload("res://quality_gate.gd")
const OUTPUT_ENV := "NEX_M11_ASSET_OUTPUT"
const SOURCE_SHA := "13554f3e9ee879c48edb32d780c6fa0611d41b19"

var checks := 0
var failures: Array[String] = []


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _initialize() -> void:
	call_deferred("_run")


func _has_code(findings: Array, code: String) -> bool:
	for finding in findings:
		if str(finding.get("code", "")) == code:
			return true
	return false


func _load(path: String) -> Dictionary:
	var text := FileAccess.get_file_as_string(path)
	if text.is_empty():
		return {}
	var value: Variant = JSON.parse_string(text)
	return value if value is Dictionary else {}


func _run() -> void:
	var assets_doc := _load("res://fixtures/assets.v1.json")
	var cook_doc := _load("res://fixtures/cook_existing.v1.json")
	var license_doc := _load("res://fixtures/licenses.v1.json")
	var assets: Array = assets_doc.get("assets", [])
	var manifest = ASSET_MANIFEST.new()
	var cook = COOK_PLANNER.new()
	var ledger = LICENSE_LEDGER.new()
	var quality = QUALITY_GATE.new()

	_check(manifest.configure({}), "manifest configure")
	_check(not manifest.configure({"max_assets": 0}), "manifest reject zero assets")
	_check(not manifest.configure({"max_texture_px": 1}), "manifest reject small texture")
	var report: Dictionary = manifest.validate_manifest(assets)
	_check(int(report["assets"]) == 8, "manifest asset count")
	_check(int(report["counts"]["error"]) == 2, "manifest error count")
	_check(int(report["counts"]["warn"]) == 2, "manifest warn count")
	_check(int(report["total_bytes"]) == 270592, "manifest total bytes")
	for code in ["missing_license", "invalid_bytes", "missing_mipmaps", "model_without_lods"]:
		_check(_has_code(report["findings"], code), "manifest code " + code)
	_check(manifest.validate_asset(assets[0]).is_empty(), "manifest clean asset")
	var again: Dictionary = manifest.validate_manifest(assets)
	_check(JSON.stringify(report) == JSON.stringify(again), "manifest deterministic")

	_check(cook.configure({"platform": "windows"}), "cook configure")
	_check(not cook.configure({"platform": "android"}), "cook reject platform")
	var plan: Dictionary = cook.plan(assets, cook_doc.get("existing", {}))
	_check(int(plan["counts"]["accepted"]) == 5, "cook accepted")
	_check(int(plan["counts"]["rejected"]) == 1, "cook rejected")
	_check(int(plan["counts"]["noop"]) == 1, "cook noop")
	_check(int(plan["counts"]["conflicts"]) == 1, "cook conflict")
	var applied: Dictionary = cook.apply(plan, {})
	_check(int(applied["counts"]["applied"]) == 5, "cook apply")
	_check(int(applied["counts"]["blocked"]) == 0, "cook apply blocked")
	var blocked: Dictionary = cook.apply(plan, {"res://cooked/windows/non_pot_rock.png": "x"})
	_check(int(blocked["counts"]["blocked"]) == 1, "cook apply conflict")
	var snapshot := cook.snapshot(plan)
	_check(snapshot.length() == 64, "cook snapshot length")
	_check(snapshot == cook.snapshot(plan), "cook snapshot deterministic")

	_check(ledger.configure({"allowed_spdx": license_doc.get("allowed_spdx", [])}), "license configure")
	_check(not ledger.configure({"allowed_spdx": []}), "license reject empty allowlist")
	var audit: Dictionary = ledger.audit(assets)
	_check(int(audit["counts"]["assets"]) == 8, "license asset count")
	_check(int(audit["counts"]["third_party"]) == 2, "license third party")
	_check(int(audit["counts"]["unverified"]) == 1, "license unverified")
	_check(int(audit["counts"]["rejected"]) == 2, "license rejected")
	_check(int(audit["counts"]["attribution"]) == 2, "license attribution")
	_check(audit["verdict"] == "BLOCKED", "license verdict")
	_check(_has_code(audit["findings"], "attribution_missing"), "license attribution finding")

	var quality_report: Dictionary = quality.evaluate(assets)
	_check(int(quality_report["counts"]["error"]) == 0, "quality errors")
	_check(int(quality_report["counts"]["warn"]) == 5, "quality warns")
	_check(int(quality_report["counts"]["info"]) == 2, "quality info")
	_check(quality_report["verdict"] == "REVIEW_REQUIRED", "quality verdict")
	_check(_has_code(quality_report["findings"], "non_power_of_two"), "quality non-pot")
	_check(_has_code(quality_report["findings"], "high_triangle_count"), "quality triangles")

	var document := {
		"schema_version": "m11_asset_smoke.v1",
		"source_sha": SOURCE_SHA,
		"checks": checks,
		"failures": failures,
		"verdict": "PASS" if failures.is_empty() else "FAIL",
		"manifest": report,
		"cook_plan": plan,
		"cook_snapshot": snapshot,
		"license_audit": audit,
		"quality": quality_report,
		"limitations": [
			"fixtures only; no asset is imported, cooked, loaded or rendered",
			"license verification is declared data, not legal review",
			"no FPS, VRAM or quality claim",
			"audit remains ADMIN_SOLO / NOT_INDEPENDENT",
		],
	}
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if output.is_empty():
		output = ProjectSettings.globalize_path("user://m11_asset_smoke.json")
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		print("M11_ASSET_SMOKE_FAIL cannot write")
		quit(2)
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	if failures.is_empty():
		print("M11_ASSET_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("M11_ASSET_SMOKE_FAIL: " + ", ".join(failures))
		quit(2)
