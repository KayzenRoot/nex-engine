extends Node
class_name AssetPipelineAuditor

# NEX-M11-AUDIT prototype: deterministic asset-pipeline auditor.
# Analysis only: no asset is imported, cooked, loaded or rendered.
# Vocabulary follows the integrated asset_pipeline.v1 contract.

const REPORT_SCHEMA := "asset_pipeline_audit.report.v1"
const PACK_SCHEMA := "asset_pipeline.v1"
const STAGE_ORDER: Array[String] = ["raw", "imported", "cooked", "validated"]
const STAGE_STATUS: Array[String] = ["pending", "pass", "fail", "skipped"]
const KINDS: Array[String] = ["texture", "model", "audio", "font", "animation", "vfx"]
const VERIFICATIONS: Array[String] = ["verified", "unverified", "rejected"]
const COMPRESSIONS: Array[String] = ["none", "lossless", "lossy"]

var last_error := ""
var _document: Dictionary = {}
var _last_report: Dictionary = {}


func load_document(document: Dictionary) -> bool:
	last_error = ""
	if String(document.get("schema_version", "")) != PACK_SCHEMA:
		last_error = "document schema_version must be " + PACK_SCHEMA
		return false
	if not document.get("assets") is Array or document["assets"].is_empty():
		last_error = "assets must be a non-empty array"
		return false
	if not document.get("policy") is Dictionary:
		last_error = "policy is required"
		return false
	if not document.get("budget") is Dictionary:
		last_error = "budget is required"
		return false
	if not document.get("provenance") is Dictionary:
		last_error = "provenance is required"
		return false
	for asset in document["assets"]:
		var asset_error := _validate_asset(asset)
		if not asset_error.is_empty():
			last_error = asset_error
			return false
	_document = document.duplicate(true)
	return true


func audit() -> Dictionary:
	last_error = ""
	if _document.is_empty():
		return _invalid("no document is loaded")
	var assets: Array = _document["assets"]
	var policy: Dictionary = _document["policy"]
	var budget: Dictionary = _document["budget"]
	var findings: Array = []
	var ids: Array[String] = []
	var total_bytes := 0
	var texture_bytes := 0
	var unverified := 0
	var failed := 0
	var pending := 0
	for asset in assets:
		var asset_id := String(asset["asset_id"])
		if ids.has(asset_id):
			findings.append(_finding("duplicate_asset_id", "high", "duplicate asset id", asset_id))
			continue
		ids.append(asset_id)
		total_bytes += int(asset["cooked_bytes"])
		if asset["kind"] == "texture":
			texture_bytes += int(asset["cooked_bytes"])
		failed += _stage_findings(asset, findings)
		pending += _pending_stages(asset, findings)
		unverified += _license_findings(asset, policy, findings)
		_quality_findings(asset, findings)
	_dependency_findings(assets, ids, findings)
	if assets.size() > int(budget["max_assets"]):
		findings.append(_finding("over_asset_budget", "high", "asset count exceeds max_assets"))
	if total_bytes > int(budget["max_total_bytes"]):
		findings.append(_finding("over_total_bytes", "high", "total bytes exceed max_total_bytes"))
	if texture_bytes > int(budget["max_texture_bytes"]):
		findings.append(_finding("over_texture_bytes", "high", "texture bytes exceed max_texture_bytes"))
	if unverified > int(budget["max_unverified_licenses"]):
		findings.append(_finding("over_unverified_licenses", "high", "unverified licenses exceed max_unverified_licenses"))
	var report := {
		"schema_version": REPORT_SCHEMA,
		"verdict": _verdict(findings),
		"metrics": {
			"assets": assets.size(),
			"total_cooked_bytes": total_bytes,
			"texture_cooked_bytes": texture_bytes,
			"unverified_licenses": unverified,
			"failed_stages": failed,
			"pending_stages": pending,
		},
		"budget": {
			"max_assets": int(budget["max_assets"]),
			"max_total_bytes": int(budget["max_total_bytes"]),
			"max_texture_bytes": int(budget["max_texture_bytes"]),
			"max_unverified_licenses": int(budget["max_unverified_licenses"]),
		},
		"findings": _sorted_findings(findings),
		"summary": _summary(findings),
		"recommendations": _recommendations(findings),
		"limitations": _limitations(),
	}
	_last_report = report
	return report


func _validate_asset(asset) -> String:
	if not asset is Dictionary:
		return "asset must be an object"
	if not _is_contract_id(String(asset.get("asset_id", ""))):
		return "asset_id does not match the contract"
	if not KINDS.has(String(asset.get("kind", ""))):
		return "asset kind is invalid"
	if String(asset.get("source_uri", "")).is_empty():
		return "source_uri is required"
	if not _is_sha256(String(asset.get("source_sha256", ""))):
		return "source_sha256 must be lowercase 64-hex"
	if not _is_integer(asset.get("cooked_bytes")) or int(asset["cooked_bytes"]) < 0:
		return "cooked_bytes must be a nonnegative integer"
	var stages = asset.get("stages")
	if not stages is Array or stages.is_empty() or stages.size() > 4:
		return "stages must contain 1..4 entries"
	for stage in stages:
		if not stage is Dictionary:
			return "stage must be an object"
		if not STAGE_ORDER.has(String(stage.get("stage", ""))):
			return "stage name is invalid"
		if not STAGE_STATUS.has(String(stage.get("status", ""))):
			return "stage status is invalid"
		if stage.has("artifact_sha256") and not _is_sha256(String(stage["artifact_sha256"])):
			return "artifact_sha256 must be lowercase 64-hex"
	var license_info = asset.get("license")
	if not license_info is Dictionary:
		return "license is required"
	for key in ["spdx_id", "source_uri"]:
		if String(license_info.get(key, "")).is_empty():
			return "license." + key + " is required"
	if not VERIFICATIONS.has(String(license_info.get("verification", ""))):
		return "license.verification is invalid"
	if not license_info.get("attribution") is String:
		return "license.attribution must be a string"
	var settings = asset.get("import_settings")
	if settings is Dictionary:
		if not COMPRESSIONS.has(String(settings.get("compression", ""))):
			return "import_settings.compression is invalid"
	var dependencies = asset.get("dependencies", [])
	if not dependencies is Array:
		return "dependencies must be an array"
	for dependency in dependencies:
		if not _is_contract_id(String(dependency)):
			return "dependency id does not match the contract"
	return ""


func _stage_findings(asset: Dictionary, findings: Array) -> int:
	var failed := 0
	var seen: Array[String] = []
	for stage in asset["stages"]:
		var name := String(stage["stage"])
		if seen.has(name):
			findings.append(_finding("duplicate_stage", "high", "duplicate stage", String(asset["asset_id"])))
			continue
		seen.append(name)
		if stage["status"] == "fail":
			failed += 1
			findings.append(_finding("stage_failed", "high", "stage failed", String(asset["asset_id"])))
		if stage["status"] == "pass":
			for earlier_index in range(STAGE_ORDER.find(name)):
				if _stage_status(asset, STAGE_ORDER[earlier_index]) != "pass":
					findings.append(_finding("stage_order", "high", "stage passes before an earlier stage", String(asset["asset_id"])))
					break
	return failed


func _pending_stages(asset: Dictionary, findings: Array) -> int:
	var pending := 0
	for stage in asset["stages"]:
		if stage["status"] == "pending":
			pending += 1
			findings.append(_finding("stage_pending", "medium", "stage is pending", String(asset["asset_id"])))
	return pending


func _license_findings(asset: Dictionary, policy: Dictionary, findings: Array) -> int:
	var asset_id := String(asset["asset_id"])
	var license_info: Dictionary = asset["license"]
	var verification := String(license_info["verification"])
	var unverified := 0
	if verification == "rejected":
		findings.append(_finding("license_rejected", "high", "license is rejected", asset_id))
	if verification == "unverified":
		unverified = 1
		findings.append(_finding("license_unverified", "medium", "license is unverified", asset_id))
	if policy.get("require_verified_license") and verification != "verified":
		findings.append(_finding("verified_license_required", "high", "verified license is required", asset_id))
	if not policy.get("allow_unverified", true) and verification == "unverified":
		findings.append(_finding("unverified_license_forbidden", "high", "unverified license is forbidden", asset_id))
	var allowed = policy.get("allowed_spdx_ids", [])
	if allowed is Array and not allowed.is_empty() and not allowed.has(license_info["spdx_id"]):
		findings.append(_finding("spdx_not_allowed", "high", "spdx_id is not allowed", asset_id))
	if policy.get("require_attribution") and String(license_info.get("attribution", "")).is_empty():
		findings.append(_finding("attribution_missing", "high", "attribution is required", asset_id))
	if policy.get("require_cooked_artifact"):
		var cooked := _stage_entry(asset, "cooked")
		if cooked.is_empty() or cooked.get("status") != "pass" or not cooked.has("artifact_sha256"):
			findings.append(_finding("cooked_artifact_missing", "high", "cooked artifact is required", asset_id))
	return unverified


func _quality_findings(asset: Dictionary, findings: Array) -> void:
	var asset_id := String(asset["asset_id"])
	var settings: Dictionary = asset.get("import_settings", {})
	if asset["kind"] == "texture":
		if settings.get("compression") == "none":
			findings.append(_finding("texture_uncompressed", "low", "texture uses no compression", asset_id))
		if int(settings.get("max_dimension_px", 0)) > 4096:
			findings.append(_finding("texture_oversized", "medium", "texture exceeds 4096 px", asset_id))
	if asset["kind"] == "model":
		if int(settings.get("lod_count", 1)) < 2:
			findings.append(_finding("model_without_lods", "low", "model has fewer than two LODs", asset_id))


func _dependency_findings(assets: Array, ids: Array[String], findings: Array) -> void:
	var graph: Dictionary = {}
	for asset in assets:
		var asset_id := String(asset["asset_id"])
		graph[asset_id] = []
		for dependency in asset.get("dependencies", []):
			var dependency_id := String(dependency)
			if dependency_id == asset_id:
				findings.append(_finding("self_dependency", "high", "asset depends on itself", asset_id))
			elif not ids.has(dependency_id):
				findings.append(_finding("dangling_dependency", "high", "dependency does not exist", asset_id))
			else:
				graph[asset_id].append(dependency_id)
	if _has_cycle(graph):
		findings.append(_finding("dependency_cycle", "high", "dependency graph contains a cycle"))


func _has_cycle(graph: Dictionary) -> bool:
	var indegree: Dictionary = {}
	for node in graph.keys():
		indegree[node] = 0
	for node in graph.keys():
		for child in graph[node]:
			indegree[child] = int(indegree.get(child, 0)) + 1
	var queue: Array[String] = []
	for node in indegree.keys():
		if int(indegree[node]) == 0:
			queue.append(node)
	var processed := 0
	while not queue.is_empty():
		var node: String = queue.pop_front()
		processed += 1
		for child in graph.get(node, []):
			indegree[child] = int(indegree[child]) - 1
			if int(indegree[child]) == 0:
				queue.append(child)
	return processed != graph.size()


func _stage_entry(asset: Dictionary, name: String) -> Dictionary:
	for stage in asset["stages"]:
		if stage["stage"] == name:
			return stage
	return {}


func _stage_status(asset: Dictionary, name: String) -> String:
	var stage := _stage_entry(asset, name)
	return String(stage.get("status", "")) if not stage.is_empty() else ""


func _verdict(findings: Array) -> String:
	for finding in findings:
		if finding["severity"] == "high":
			return "BLOCKED"
	for finding in findings:
		if finding["severity"] == "medium":
			return "REVIEW_REQUIRED"
	return "READY_FOR_INTEGRATION"


func _summary(findings: Array) -> Dictionary:
	var summary := {"high": 0, "medium": 0, "low": 0, "info": 0}
	for finding in findings:
		summary[finding["severity"]] += 1
	return summary


func _finding(code: String, severity: String, message: String, asset_id := "") -> Dictionary:
	var finding := {"code": code, "severity": severity, "message": message}
	if not asset_id.is_empty():
		finding["asset_id"] = asset_id
	return finding


func _sorted_findings(findings: Array) -> Array:
	var order := {"high": 0, "medium": 1, "low": 2, "info": 3}
	findings.sort_custom(func(a, b):
		if order[a["severity"]] == order[b["severity"]]:
			return String(a["code"]) < String(b["code"])
		return order[a["severity"]] < order[b["severity"]]
	)
	return findings


func _recommendations(findings: Array) -> Array:
	var actions: Array[String] = []
	for finding in findings:
		match finding["code"]:
			"license_rejected", "verified_license_required":
				actions.append("replace_or_verify_license")
			"license_unverified", "unverified_license_forbidden":
				actions.append("verify_license")
			"attribution_missing":
				actions.append("add_attribution")
			"spdx_not_allowed":
				actions.append("choose_allowed_license")
			"stage_failed", "stage_order", "stage_pending":
				actions.append("fix_pipeline_stage")
			"cooked_artifact_missing":
				actions.append("cook_asset")
			"dangling_dependency", "self_dependency", "dependency_cycle":
				actions.append("fix_dependencies")
			"over_asset_budget", "over_total_bytes", "over_texture_bytes":
				actions.append("reduce_asset_budget")
			"texture_uncompressed":
				actions.append("enable_texture_compression")
			"texture_oversized":
				actions.append("downscale_texture")
			"model_without_lods":
				actions.append("add_model_lods")
			_:
				pass
	var unique: Array[String] = []
	for action in actions:
		if not unique.has(action):
			unique.append(action)
	unique.sort()
	return unique


func _limitations() -> Array[String]:
	return [
		"analysis only: no asset is imported, cooked, loaded or rendered",
		"license verification is read from the document, not performed",
		"byte budgets use cooked_bytes as declared, not filesystem measurements",
		"dependency cycles are graph arithmetic over declared ids",
		"quality findings are structural heuristics, not visual review",
		"no scene, engine or project.godot integration",
	]


func _invalid(reason: String) -> Dictionary:
	last_error = reason
	var report := {
		"schema_version": REPORT_SCHEMA,
		"verdict": "INVALID_INPUT",
		"metrics": {},
		"budget": {},
		"findings": [],
		"summary": {"high": 0, "medium": 0, "low": 0, "info": 0},
		"recommendations": [],
		"limitations": _limitations(),
		"reason": reason,
	}
	_last_report = report
	return report


func _is_contract_id(value: String) -> bool:
	if value.length() < 2 or value.length() > 64:
		return false
	for index in range(value.length()):
		var character := value[index]
		if index == 0:
			if not "abcdefghijklmnopqrstuvwxyz0123456789".contains(character):
				return false
		elif not "abcdefghijklmnopqrstuvwxyz0123456789._-".contains(character):
			return false
	return true


func _is_sha256(value: String) -> bool:
	if value.length() != 64:
		return false
	for character in value:
		if not "0123456789abcdef".contains(character):
			return false
	return true


func _is_integer(value) -> bool:
	return value is int or (value is float and is_finite(value) and value == floor(value))


func get_last_report() -> Dictionary:
	return _last_report


func clear() -> void:
	_document.clear()
	_last_report = {}
	last_error = ""
