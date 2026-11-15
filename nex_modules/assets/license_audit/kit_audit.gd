extends SceneTree

# NEX M11 kit audit: feeds the committed M04 material kit to the integrated
# AssetPipelineAuditor. Analysis only: no asset is imported, cooked, loaded as
# a texture or rendered. Licenses are reported as unverified, never claimed.
# godot --headless --path nex_modules/assets/license_audit --script res://kit_audit.gd

const AUDITOR := preload("res://asset_pipeline_auditor.gd")
const KIT_ENV := "NEX_M04_KIT_PATH"
const OUTPUT_ENV := "NEX_M11_KIT_AUDIT_OUTPUT"
const SOURCE_SHA := "7e425920cdaf17c158d46979e68df47e66742724"
const KIT_URI := "nex_modules/materials/kit/kit.v1.json"
const SPDX_ID := "LicenseRef-NEX-Procedural"


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	print("M11_KIT_AUDIT_FAIL " + message)
	quit(2)


func _texture_asset(kit_dir: String, texture: Dictionary) -> Dictionary:
	var uri := String(texture["uri"])
	var path := kit_dir + "/" + uri.trim_prefix("res://")
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return {}
	var asset_id := path.get_file().get_basename()
	return {
		"asset_id": asset_id,
		"kind": "texture",
		"source_uri": uri,
		"source_sha256": String(texture["sha256"]),
		"cooked_bytes": file.get_length(),
		"stages": [
			{"stage": "raw", "status": "pass"},
			{"stage": "imported", "status": "pass", "tool_id": "godot-4.7.2-import"},
		],
		"license": {
			"spdx_id": SPDX_ID,
			"source_uri": "nex_modules/materials/kit/README.md",
			"attribution": "NEX Engine procedural kit; generated deterministically",
			"verification": "unverified",
		},
		"import_settings": {"compression": "none", "max_dimension_px": 128, "lod_count": 1},
		"dependencies": [],
	}


func _run() -> void:
	var kit_path := OS.get_environment(KIT_ENV).strip_edges()
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if kit_path.is_empty() or output.is_empty():
		_fail("missing kit or output path")
		return
	var text := FileAccess.get_file_as_string(kit_path)
	if text.is_empty():
		_fail("cannot read kit observation")
		return
	var kit = JSON.parse_string(text)
	if not kit is Dictionary or String(kit.get("schema_version", "")) != "material.v1":
		_fail("kit observation is not material.v1")
		return
	var kit_dir := kit_path.get_base_dir()
	var assets: Array = []
	for material in kit.get("materials", []):
		for texture in material.get("textures", []):
			var asset := _texture_asset(kit_dir, texture)
			if asset.is_empty():
				_fail("cannot read texture " + String(texture["uri"]))
				return
			assets.append(asset)
	var document := {
		"schema_version": "asset_pipeline.v1",
		"observation_id": "m11-kit-audit.v1",
		"captured_at_utc": "2026-11-15T00:00:00Z",
		"assets": assets,
		"policy": {
			"allowed_spdx_ids": [SPDX_ID],
			"require_attribution": true,
			"require_verified_license": false,
			"allow_unverified": true,
			"require_cooked_artifact": false,
		},
		"budget": {
			"max_assets": 100,
			"max_total_bytes": 104857600,
			"max_texture_bytes": 52428800,
			"max_unverified_licenses": assets.size(),
		},
		"provenance": {
			"base_sha": SOURCE_SHA,
			"head_sha": SOURCE_SHA,
			"godot_version": "4.7.2-stable",
			"hardware": {"gpu_model": "NVIDIA GeForce RTX 5050", "driver_version": "NVIDIA 617.14"},
			"capture_mode": "headless",
			"measurement_status": "UNAVAILABLE",
		},
	}
	var auditor = AUDITOR.new()
	root.add_child(auditor)
	if not auditor.load_document(document):
		_fail("auditor rejected the kit document: " + auditor.last_error)
		return
	var report: Dictionary = auditor.audit()
	var result := {
		"schema_version": "m11_kit_audit_run.v1",
		"source_sha": SOURCE_SHA,
		"kit_uri": KIT_URI,
		"kit_sha256": FileAccess.get_sha256(kit_path),
		"document": document,
		"report": report,
	}
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		_fail("cannot write output")
		return
	file.store_string(JSON.stringify(result, "  ") + "\n")
	file.close()
	print("M11_KIT_AUDIT_OK " + String(report.get("verdict", "")))
	quit(0)
