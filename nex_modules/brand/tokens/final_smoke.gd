extends SceneTree

# NEX M12 final identity smoke: validates the canonical brand identity document
# against IdentityValidator and writes a deterministic report.

const OUTPUT_ENV := "NEX_M12_FINAL_OUTPUT"
const SOURCE_SHA := "c2c13c57b4de7a5114db2e2b79d37a7e026bfa62"

var checks := 0
var failures: Array[String] = []


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var root_path := ProjectSettings.globalize_path("res://") + "../../.."
	var text := FileAccess.get_file_as_string(root_path + "/assets/brand/identity.v1.json")
	if text.is_empty():
		print("NEX_M12_FINAL_IDENTITY_FAIL missing identity")
		quit(2)
		return
	var value: Variant = JSON.parse_string(text)
	if not value is Dictionary:
		print("NEX_M12_FINAL_IDENTITY_FAIL invalid JSON")
		quit(2)
		return
	var packed := load("res://main.tscn") as PackedScene
	_check(packed != null, "main scene loads")
	if packed == null:
		_finish({})
		return
	var validator = packed.instantiate()
	root.add_child(validator)
	await process_frame
	_check(validator.load_document(value), "identity document loads")
	var report: Dictionary = validator.audit()
	_check(report.get("schema_version") == "identity_validation.report.v1", "report schema")
	_check(report.get("verdict") == "READY_FOR_UI", "identity is ready")
	_check(report.get("findings", []).is_empty(), "identity has no findings")
	var summary: Dictionary = report.get("summary", {})
	_check(int(summary.get("high", 0)) == 0, "no high findings")
	_check(int(summary.get("medium", 0)) == 0, "no medium findings")
	_check(int(summary.get("low", 0)) == 0, "no low findings")
	var palette: Array = value.get("palette", [])
	_check(palette.size() == 5, "five palette tokens")
	_check(String(palette[0].get("token", "")) == "graphite", "graphite token")
	var logo: Dictionary = value.get("logo", {})
	_check(String(logo.get("mark_sha256", "")).length() == 64, "mark hash")
	_check(String(logo.get("wordmark_sha256", "")).length() == 64, "wordmark hash")
	var accessibility: Dictionary = value.get("accessibility", {})
	_check(float(accessibility.get("min_text_contrast_ratio", 0.0)) >= 7.0, "text contrast threshold")
	_check(float(accessibility.get("min_large_text_contrast_ratio", 0.0)) >= 3.0, "large contrast threshold")
	_finish(report)


func _finish(report: Dictionary) -> void:
	var document := {
		"schema_version": "m12_final_identity.v1",
		"source_sha": SOURCE_SHA,
		"checks": checks,
		"failures": failures,
		"verdict": "PASS" if failures.is_empty() else "FAIL",
		"report": report,
		"limitations": [
			"headless structural validation only",
			"no editor UI, launcher or installer is modified",
			"distribution and trademark clearance remain Owner decisions",
			"audit remains ADMIN_SOLO / NOT_INDEPENDENT",
		],
	}
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if output.is_empty():
		output = ProjectSettings.globalize_path("res://evidence/m12-final-identity-2026-11-17.json")
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		print("NEX_M12_FINAL_IDENTITY_FAIL cannot write")
		quit(2)
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	if failures.is_empty():
		print("NEX_M12_FINAL_IDENTITY_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M12_FINAL_IDENTITY_FAIL: " + ", ".join(failures))
		quit(2)
