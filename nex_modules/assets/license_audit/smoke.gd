extends SceneTree

# Headless deterministic smoke for NEX M11-AUDIT AssetPipelineAuditor.
# godot --headless --path nex_modules/assets/license_audit --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _texture() -> Dictionary:
	return {
		"asset_id": "stone-albedo",
		"kind": "texture",
		"source_uri": "res://art/stone_albedo.png",
		"source_sha256": "a".repeat(64),
		"cooked_bytes": 22369621,
		"stages": [
			{"stage": "raw", "status": "pass"},
			{"stage": "imported", "status": "pass"},
			{"stage": "cooked", "status": "pass", "artifact_sha256": "b".repeat(64), "tool_id": "cook-texture"},
			{"stage": "validated", "status": "pass"},
		],
		"license": {
			"spdx_id": "MIT", "source_uri": "https://example.invalid/license",
			"attribution": "NEX fixture", "verification": "verified", "evidence_uri": "evidence://license",
		},
		"import_settings": {"compression": "lossy", "max_dimension_px": 2048, "lod_count": 3},
		"dependencies": [],
	}


func _model() -> Dictionary:
	return {
		"asset_id": "hero-mesh",
		"kind": "model",
		"source_uri": "res://art/hero.glb",
		"source_sha256": "c".repeat(64),
		"cooked_bytes": 1048576,
		"stages": [
			{"stage": "raw", "status": "pass"},
			{"stage": "imported", "status": "pass"},
			{"stage": "cooked", "status": "pass", "artifact_sha256": "d".repeat(64), "tool_id": "cook-mesh"},
		],
		"license": {
			"spdx_id": "CC0-1.0", "source_uri": "https://example.invalid/cc0",
			"attribution": "NEX fixture", "verification": "verified",
		},
		"import_settings": {"compression": "lossless", "lod_count": 4},
		"dependencies": ["stone-albedo"],
	}


func _doc() -> Dictionary:
	return {
		"schema_version": "asset_pipeline.v1",
		"observation_id": "m11-smoke-001",
		"captured_at_utc": "2026-11-14T12:00:00Z",
		"assets": [_texture(), _model()],
		"policy": {
			"allowed_spdx_ids": ["MIT", "CC0-1.0", "Apache-2.0"],
			"require_attribution": true,
			"require_verified_license": true,
			"allow_unverified": false,
			"require_cooked_artifact": true,
		},
		"budget": {
			"max_assets": 100, "max_total_bytes": 104857600,
			"max_texture_bytes": 52428800, "max_unverified_licenses": 0,
		},
		"provenance": {
			"base_sha": "e".repeat(40), "head_sha": "f".repeat(40),
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
	var auditor = packed.instantiate()
	root.add_child(auditor)
	await process_frame

	_check(auditor.load_document(_doc()), "valid document loaded")
	var report: Dictionary = auditor.audit()
	_check(report["schema_version"] == "asset_pipeline_audit.report.v1", "report schema version")
	_check(report["verdict"] == "READY_FOR_INTEGRATION", "clean document is ready")
	_check(report["metrics"]["assets"] == 2, "asset count")
	_check(report["metrics"]["total_cooked_bytes"] == 23418197, "total cooked bytes")
	_check(report["metrics"]["texture_cooked_bytes"] == 22369621, "texture cooked bytes")
	_check(report["metrics"]["unverified_licenses"] == 0, "no unverified licenses")
	_check(report["summary"]["high"] == 0 and report["summary"]["medium"] == 0, "clean document has no high/medium findings")
	_check(report["limitations"].size() >= 5, "limitations documented")
	_check(JSON.stringify(report) == JSON.stringify(auditor.audit()), "audit is deterministic")
	_check(JSON.stringify(auditor.get_last_report()) == JSON.stringify(report), "last report retained")

	var duplicate := _doc()
	duplicate["assets"][1]["asset_id"] = "stone-albedo"
	auditor.load_document(duplicate)
	report = auditor.audit()
	_check(_has(report, "duplicate_asset_id"), "duplicate asset flagged")
	_check(report["verdict"] == "BLOCKED", "duplicate blocks integration")

	var stage_order := _doc()
	stage_order["assets"][1]["stages"] = [{"stage": "raw", "status": "pending"}, {"stage": "imported", "status": "pass"}]
	auditor.load_document(stage_order)
	_check(_has(auditor.audit(), "stage_order"), "stage order violation flagged")

	var stage_fail := _doc()
	stage_fail["assets"][0]["stages"][1]["status"] = "fail"
	auditor.load_document(stage_fail)
	report = auditor.audit()
	_check(_has(report, "stage_failed"), "failed stage flagged")
	_check(report["verdict"] == "BLOCKED", "failed stage blocks integration")

	var pending := _doc()
	pending["assets"][0]["stages"][3]["status"] = "pending"
	auditor.load_document(pending)
	report = auditor.audit()
	_check(_has(report, "stage_pending"), "pending stage flagged")
	_check(report["verdict"] == "REVIEW_REQUIRED", "pending stage requires review")

	var no_artifact := _doc()
	no_artifact["assets"][1]["stages"][2].erase("artifact_sha256")
	auditor.load_document(no_artifact)
	_check(_has(auditor.audit(), "cooked_artifact_missing"), "missing cooked artifact flagged")

	var rejected := _doc()
	rejected["assets"][0]["license"]["verification"] = "rejected"
	auditor.load_document(rejected)
	report = auditor.audit()
	_check(_has(report, "license_rejected"), "rejected license flagged")
	_check(report["recommendations"].has("replace_or_verify_license"), "license recommendation present")

	var unverified := _doc()
	unverified["assets"][0]["license"]["verification"] = "unverified"
	unverified["policy"]["require_verified_license"] = false
	unverified["policy"]["allow_unverified"] = true
	unverified["budget"]["max_unverified_licenses"] = 1
	auditor.load_document(unverified)
	report = auditor.audit()
	_check(_has(report, "license_unverified"), "unverified license flagged")
	_check(report["verdict"] == "REVIEW_REQUIRED", "unverified license requires review")

	var verified_required := _doc()
	verified_required["assets"][0]["license"]["verification"] = "unverified"
	auditor.load_document(verified_required)
	_check(_has(auditor.audit(), "verified_license_required"), "verified license requirement flagged")

	var bad_spdx := _doc()
	bad_spdx["assets"][0]["license"]["spdx_id"] = "GPL-3.0-only"
	auditor.load_document(bad_spdx)
	_check(_has(auditor.audit(), "spdx_not_allowed"), "disallowed SPDX flagged")

	var no_attribution := _doc()
	no_attribution["assets"][0]["license"]["attribution"] = ""
	auditor.load_document(no_attribution)
	_check(_has(auditor.audit(), "attribution_missing"), "missing attribution flagged")

	var dangling := _doc()
	dangling["assets"][1]["dependencies"] = ["missing-asset"]
	auditor.load_document(dangling)
	_check(_has(auditor.audit(), "dangling_dependency"), "dangling dependency flagged")

	var self_dependency := _doc()
	self_dependency["assets"][1]["dependencies"] = ["hero-mesh"]
	auditor.load_document(self_dependency)
	_check(_has(auditor.audit(), "self_dependency"), "self dependency flagged")

	var cycle := _doc()
	cycle["assets"][0]["dependencies"] = ["hero-mesh"]
	auditor.load_document(cycle)
	_check(_has(auditor.audit(), "dependency_cycle"), "dependency cycle flagged")

	var asset_budget := _doc()
	asset_budget["budget"]["max_assets"] = 1
	auditor.load_document(asset_budget)
	_check(_has(auditor.audit(), "over_asset_budget"), "asset budget flagged")

	var total_budget := _doc()
	total_budget["budget"]["max_total_bytes"] = 1024
	auditor.load_document(total_budget)
	_check(_has(auditor.audit(), "over_total_bytes"), "total byte budget flagged")

	var texture_budget := _doc()
	texture_budget["budget"]["max_texture_bytes"] = 1024
	auditor.load_document(texture_budget)
	_check(_has(auditor.audit(), "over_texture_bytes"), "texture byte budget flagged")

	var license_budget := _doc()
	license_budget["assets"][0]["license"]["verification"] = "unverified"
	license_budget["policy"]["require_verified_license"] = false
	license_budget["policy"]["allow_unverified"] = true
	auditor.load_document(license_budget)
	_check(_has(auditor.audit(), "over_unverified_licenses"), "unverified license budget flagged")

	var uncompressed := _doc()
	uncompressed["assets"][0]["import_settings"]["compression"] = "none"
	auditor.load_document(uncompressed)
	report = auditor.audit()
	_check(_has(report, "texture_uncompressed"), "uncompressed texture flagged")
	_check(report["verdict"] == "READY_FOR_INTEGRATION", "low-only finding keeps ready verdict")

	var oversized := _doc()
	oversized["assets"][0]["import_settings"]["max_dimension_px"] = 8192
	auditor.load_document(oversized)
	report = auditor.audit()
	_check(_has(report, "texture_oversized"), "oversized texture flagged")
	_check(report["verdict"] == "REVIEW_REQUIRED", "medium finding requires review")

	var no_lods := _doc()
	no_lods["assets"][1]["import_settings"]["lod_count"] = 1
	auditor.load_document(no_lods)
	_check(_has(auditor.audit(), "model_without_lods"), "model without LODs flagged")

	_check(not auditor.load_document({"schema_version": "asset_pipeline.v2", "assets": [], "policy": {}, "budget": {}, "provenance": {}}), "wrong schema rejected")
	_check(not auditor.load_document({"schema_version": "asset_pipeline.v1", "assets": [], "policy": {}, "budget": {}, "provenance": {}}), "empty assets rejected")

	var bad_asset := _doc()
	bad_asset["assets"][0]["asset_id"] = "Stone Albedo"
	_check(not auditor.load_document(bad_asset), "invalid asset id rejected")

	auditor.clear()
	_check(auditor.audit()["verdict"] == "INVALID_INPUT", "cleared auditor is invalid")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M11_AUDIT_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M11_AUDIT_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
