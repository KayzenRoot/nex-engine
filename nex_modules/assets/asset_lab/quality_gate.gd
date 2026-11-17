extends RefCounted
class_name AssetQualityGate

# NEX M11 AssetQualityGate: structural texture/model/animation quality checks.
# It does not decode pixels or perform visual review.

const KINDS := ["texture", "model", "animation"]


func _finding(code: String, severity: String, message: String) -> Dictionary:
	return {"code": code, "severity": severity, "message": message}


func _is_power_of_two(value: int) -> bool:
	return value > 0 and (value & (value - 1)) == 0


func check_texture(asset: Dictionary) -> Array:
	var findings: Array = []
	var width := int(asset.get("width", 0))
	var height := int(asset.get("height", 0))
	if not _is_power_of_two(width) or not _is_power_of_two(height):
		findings.append(_finding("non_power_of_two", "warn", "texture dimensions are not power-of-two"))
	if width != height:
		findings.append(_finding("non_square", "info", "texture is not square"))
	if not bool(asset.get("mipmaps", false)):
		findings.append(_finding("missing_mipmaps", "warn", "texture has no mipmaps"))
	if str(asset.get("format", "")) == "png" and not bool(asset.get("compressed", false)):
		findings.append(_finding("uncompressed_texture", "warn", "texture is not compressed"))
	return findings


func check_model(asset: Dictionary) -> Array:
	var findings: Array = []
	if float(asset.get("scale", 0.0)) <= 0.0:
		findings.append(_finding("invalid_scale", "error", "model scale must be positive"))
	if int(asset.get("lods", 0)) < 1:
		findings.append(_finding("model_without_lods", "warn", "model has no LODs"))
	if int(asset.get("triangles", 0)) > 100000:
		findings.append(_finding("high_triangle_count", "warn", "model exceeds 100k triangles"))
	return findings


func check_animation(asset: Dictionary) -> Array:
	var findings: Array = []
	if float(asset.get("duration", 0.0)) <= 0.0:
		findings.append(_finding("invalid_duration", "error", "animation duration must be positive"))
	if int(asset.get("tracks", 0)) < 1:
		findings.append(_finding("missing_tracks", "warn", "animation has no tracks"))
	if not bool(asset.get("loop", false)):
		findings.append(_finding("non_looping", "info", "animation is not looping"))
	return findings


func evaluate(assets: Array) -> Dictionary:
	var findings: Array = []
	var counts := {"error": 0, "warn": 0, "info": 0}
	for asset in assets:
		if not (asset is Dictionary):
			continue
		var kind := str(asset.get("kind", ""))
		var items: Array = []
		if kind == "texture":
			items = check_texture(asset)
		elif kind == "model":
			items = check_model(asset)
		elif kind == "animation":
			items = check_animation(asset)
		for finding in items:
			finding["id"] = str(asset.get("id", ""))
			findings.append(finding)
			var severity := str(finding.get("severity", "info"))
			if counts.has(severity):
				counts[severity] += 1
	findings.sort_custom(func(a, b): return str(a["code"]) < str(b["code"]))
	var verdict := "PASS"
	if counts["error"] > 0:
		verdict = "BLOCKED"
	elif counts["warn"] > 0:
		verdict = "REVIEW_REQUIRED"
	return {"findings": findings, "counts": counts, "verdict": verdict}
