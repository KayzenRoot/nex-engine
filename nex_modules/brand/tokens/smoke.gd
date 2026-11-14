extends SceneTree

# Headless deterministic smoke for NEX M12-VALIDATOR IdentityValidator.
# godot --headless --path nex_modules/brand/tokens --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _doc() -> Dictionary:
	return {
		"schema_version": "identity.v1",
		"observation_id": "m12-smoke-001",
		"captured_at_utc": "2026-11-14T12:00:00Z",
		"palette": [
			{"token": "nex-primary", "hex": "#1f6feb", "role": "primary"},
			{"token": "nex-background", "hex": "#0b0f14", "role": "background"},
			{"token": "nex-foreground", "hex": "#f0f4f8", "role": "foreground"},
			{"token": "nex-accent", "hex": "#35d0ff", "role": "accent"},
			{"token": "nex-surface", "hex": "#161b22", "role": "surface"},
			{"token": "nex-error", "hex": "#ff5c5c", "role": "error"},
			{"token": "nex-success", "hex": "#3fb950", "role": "success"},
			{"token": "nex-warning", "hex": "#d29922", "role": "warning"},
		],
		"typography": {
			"font_family": "Inter", "display_size_px": 48, "body_size_px": 16,
			"line_height_ratio": 1.5, "weights": [400, 600, 700],
		},
		"logo": {
			"mark_svg_uri": "res://brand/nex_mark.svg", "mark_sha256": "a".repeat(64),
			"mark_view_box": [0, 0, 64, 64],
			"wordmark_svg_uri": "res://brand/nex_wordmark.svg", "wordmark_sha256": "b".repeat(64),
			"wordmark_view_box": [0, 0, 240, 64],
			"monochrome_sha256": "c".repeat(64), "clear_space_ratio": 0.25,
		},
		"spacing": {"base_px": 4, "scale": [4, 8, 12, 16, 24, 32, 48, 64], "max_content_width_px": 1440},
		"accessibility": {
			"min_text_contrast_ratio": 4.5, "min_large_text_contrast_ratio": 3.0,
			"requires_focus_indicator": true, "min_focus_ring_px": 2,
		},
		"provenance": {
			"base_sha": "d".repeat(40), "head_sha": "e".repeat(40),
			"godot_version": "4.7.2-stable",
			"hardware": {"gpu_model": "NVIDIA GeForce RTX 5050", "driver_version": "617.14"},
			"capture_mode": "headless", "measurement_status": "UNAVAILABLE",
		},
	}


func _has(report: Dictionary, code: String) -> bool:
	for finding in report["findings"]:
		if finding["code"] == code:
			return true
	return false


func _run() -> void:
	var packed := load("res://main.tscn") as PackedScene
	_check(packed != null, "main scene loads")
	if packed == null:
		_finish()
		return
	var validator = packed.instantiate()
	root.add_child(validator)
	await process_frame

	_check(validator.load_document(_doc()), "valid document loaded")
	var report: Dictionary = validator.audit()
	_check(report["schema_version"] == "identity_validation.report.v1", "report schema version")
	_check(report["verdict"] == "READY_FOR_UI", "valid identity is ready")
	_check(report["metrics"]["palette_tokens"] == 8, "palette token count")
	_check(report["metrics"]["roles_present"] == 8, "roles present")
	_check(report["metrics"]["text_contrast_ratio"] >= 4.5, "text contrast meets threshold")
	_check(report["metrics"]["spacing_steps"] == 8, "spacing steps")
	_check(report["metrics"]["logo_variants"] == 3, "logo variants")
	_check(report["summary"]["high"] == 0 and report["summary"]["medium"] == 0, "valid identity has no high/medium findings")
	_check(report["limitations"].size() >= 5, "limitations documented")
	_check(JSON.stringify(report) == JSON.stringify(validator.audit()), "audit is deterministic")
	_check(JSON.stringify(validator.get_last_report()) == JSON.stringify(report), "last report retained")

	var duplicate := _doc()
	duplicate["palette"][1]["token"] = "nex-primary"
	validator.load_document(duplicate)
	report = validator.audit()
	_check(_has(report, "duplicate_token"), "duplicate token flagged")
	_check(report["verdict"] == "BLOCKED", "duplicate token blocks UI")

	var missing_role := _doc()
	var filtered: Array = []
	for entry in missing_role["palette"]:
		if entry["role"] != "foreground":
			filtered.append(entry)
	missing_role["palette"] = filtered
	validator.load_document(missing_role)
	_check(_has(validator.audit(), "missing_required_role"), "missing role flagged")

	var low_text := _doc()
	low_text["palette"][2]["hex"] = "#777777"
	validator.load_document(low_text)
	report = validator.audit()
	_check(_has(report, "text_contrast_low"), "low text contrast flagged")
	_check(report["recommendations"].has("increase_contrast"), "contrast recommendation present")

	var low_primary := _doc()
	low_primary["palette"][0]["hex"] = "#111827"
	validator.load_document(low_primary)
	_check(_has(validator.audit(), "large_contrast_low"), "low primary contrast flagged")

	var low_accent := _doc()
	low_accent["palette"][3]["hex"] = "#111111"
	validator.load_document(low_accent)
	report = validator.audit()
	_check(_has(report, "accent_contrast_low"), "low accent contrast flagged")
	_check(report["verdict"] == "READY_FOR_UI", "low-only accent keeps ready verdict")

	var small_display := _doc()
	small_display["typography"]["display_size_px"] = 24
	small_display["typography"]["body_size_px"] = 24
	validator.load_document(small_display)
	_check(_has(validator.audit(), "display_not_larger"), "small display flagged")

	var duplicate_weight := _doc()
	duplicate_weight["typography"]["weights"] = [400, 400]
	validator.load_document(duplicate_weight)
	_check(_has(validator.audit(), "duplicate_weight"), "duplicate weight flagged")

	var odd_weight := _doc()
	odd_weight["typography"]["weights"] = [450]
	validator.load_document(odd_weight)
	report = validator.audit()
	_check(_has(report, "weight_not_multiple"), "non-multiple weight flagged")
	_check(report["verdict"] == "REVIEW_REQUIRED", "medium weight finding requires review")

	var bad_view_box := _doc()
	bad_view_box["logo"]["mark_view_box"] = [0, 0, 0, 64]
	validator.load_document(bad_view_box)
	_check(_has(validator.audit(), "view_box_invalid"), "invalid viewBox flagged")

	var unsorted := _doc()
	unsorted["spacing"]["scale"] = [4, 8, 4]
	validator.load_document(unsorted)
	_check(_has(validator.audit(), "spacing_not_ascending"), "unsorted spacing flagged")

	var below_base := _doc()
	below_base["spacing"]["scale"] = [2, 4, 8]
	validator.load_document(below_base)
	_check(_has(validator.audit(), "spacing_below_base"), "spacing below base flagged")

	var threshold_order := _doc()
	threshold_order["accessibility"]["min_large_text_contrast_ratio"] = 7.0
	validator.load_document(threshold_order)
	_check(_has(validator.audit(), "contrast_threshold_order"), "threshold order flagged")

	var measured := _doc()
	measured["provenance"]["measurement_status"] = "MEASURED"
	validator.load_document(measured)
	report = validator.audit()
	_check(_has(report, "provenance_without_evidence"), "measured provenance without evidence flagged")
	_check(report["verdict"] == "BLOCKED", "provenance finding blocks UI")

	_check(not validator.load_document({"schema_version": "identity.v2", "palette": [], "typography": {}, "logo": {}, "spacing": {}, "accessibility": {}, "provenance": {}}), "wrong schema rejected")
	_check(not validator.load_document({"schema_version": "identity.v1", "palette": [], "typography": {}, "logo": {}, "spacing": {}, "accessibility": {}, "provenance": {}}), "empty palette rejected")

	var bad_hex := _doc()
	bad_hex["palette"][0]["hex"] = "#ABCDEF"
	_check(not validator.load_document(bad_hex), "uppercase hex rejected")

	var bad_focus := _doc()
	bad_focus["accessibility"]["min_focus_ring_px"] = 0
	_check(not validator.load_document(bad_focus), "zero focus ring rejected")

	validator.clear()
	_check(validator.audit()["verdict"] == "INVALID_INPUT", "cleared validator is invalid")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M12_VALIDATOR_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M12_VALIDATOR_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
