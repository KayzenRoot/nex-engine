extends RefCounted
class_name LicenseLedger

# NEX M11 LicenseLedger: deterministic license/attribution audit. It does
# not perform legal verification or clear assets.

const ALLOWED_SPDX := ["Original", "CC0-1.0", "MIT", "Apache-2.0", "CC-BY-4.0"]

var allowed_spdx: Array = ALLOWED_SPDX.duplicate()
var last_error := ""


func configure(config := {}) -> bool:
	last_error = ""
	var allowed: Variant = config.get("allowed_spdx", allowed_spdx)
	if not (allowed is Array) or allowed.is_empty():
		last_error = "allowed_spdx must be non-empty"
		return false
	for item in allowed:
		if not (item is String) or String(item).is_empty():
			last_error = "allowed_spdx entries must be strings"
			return false
	allowed_spdx = allowed
	return true


func audit(assets: Array) -> Dictionary:
	last_error = ""
	var findings: Array = []
	var entries: Array = []
	var third_party := 0
	var unverified := 0
	var rejected := 0
	var attribution := 0
	for asset in assets:
		if not (asset is Dictionary):
			continue
		var id := str(asset.get("id", ""))
		var spdx := str(asset.get("license", ""))
		var source := str(asset.get("source", ""))
		var verification := str(asset.get("license_verification", "unverified"))
		var required := spdx == "CC-BY-4.0" or source != "original"
		var allowed := allowed_spdx.has(spdx)
		if source != "original":
			third_party += 1
		if not allowed:
			rejected += 1
			findings.append({"id": id, "code": "license_rejected", "severity": "error"})
		elif verification != "verified":
			unverified += 1
			findings.append({"id": id, "code": "license_unverified", "severity": "warn"})
		if required:
			attribution += 1
			if str(asset.get("attribution", "")).is_empty():
				findings.append({"id": id, "code": "attribution_missing", "severity": "warn"})
		entries.append({"id": id, "spdx": spdx, "allowed": allowed,
			"verification": verification, "attribution_required": required})
	var verdict := "CLEARED"
	if rejected > 0:
		verdict = "BLOCKED"
	elif unverified > 0 or attribution > 0:
		verdict = "REVIEW_REQUIRED"
	return {"entries": entries, "findings": findings,
		"counts": {"assets": assets.size(), "third_party": third_party,
			"unverified": unverified, "rejected": rejected, "attribution": attribution},
		"verdict": verdict}


func clear() -> void:
	last_error = ""
