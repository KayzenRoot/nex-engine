extends RefCounted
class_name CookPlanner

# NEX M11 CookPlanner: deterministic cook plan with conflict and NOOP
# detection. It never writes, cooks or overwrites an asset.

const PLATFORMS := ["windows", "linux", "macos"]
const FORMATS := ["png", "ktx2", "webp", "glb", "ogg"]

var platform := "windows"
var allowed_formats: Array = FORMATS.duplicate()
var max_cooked_bytes := 67108864
var last_error := ""


func configure(config := {}) -> bool:
	last_error = ""
	var next_platform := str(config.get("platform", platform))
	if not PLATFORMS.has(next_platform):
		last_error = "platform is invalid"
		return false
	var formats: Variant = config.get("allowed_formats", allowed_formats)
	if not (formats is Array) or formats.is_empty():
		last_error = "allowed_formats must be non-empty"
		return false
	var next_bytes := int(config.get("max_cooked_bytes", max_cooked_bytes))
	if next_bytes < 1:
		last_error = "max_cooked_bytes must be positive"
		return false
	platform = next_platform
	allowed_formats = formats
	max_cooked_bytes = next_bytes
	return true


func plan(assets: Array, existing := {}) -> Dictionary:
	last_error = ""
	var accepted: Array = []
	var rejected: Array = []
	var noop: Array = []
	var conflicts: Array = []
	for asset in assets:
		if not (asset is Dictionary):
			rejected.append({"id": "", "reason": "asset must be an object"})
			continue
		var id := str(asset.get("id", ""))
		var format := str(asset.get("cook_format", "png")).to_lower()
		var bytes := int(asset.get("cooked_bytes", asset.get("bytes", 0)))
		var sha := str(asset.get("sha256", "")).to_lower()
		var reason := ""
		if id.is_empty():
			reason = "id is required"
		elif not allowed_formats.has(format):
			reason = "format not allowed: " + format
		elif bytes < 1 or bytes > max_cooked_bytes:
			reason = "cooked size outside [1,max]"
		elif sha.length() != 64:
			reason = "sha256 is invalid"
		if not reason.is_empty():
			rejected.append({"id": id, "reason": reason})
			continue
		var destination := "res://cooked/%s/%s.%s" % [platform, id, format]
		var entry := {"id": id, "destination": destination, "format": format,
			"cooked_bytes": bytes, "sha256": sha}
		if existing is Dictionary and existing.has(destination):
			if str(existing[destination]) == sha:
				noop.append(entry)
			else:
				conflicts.append({"id": id, "destination": destination, "reason": "hash differs"})
		else:
			accepted.append(entry)
	accepted.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	rejected.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	noop.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	conflicts.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	return {"accepted": accepted, "rejected": rejected, "noop": noop, "conflicts": conflicts,
		"counts": {"accepted": accepted.size(), "rejected": rejected.size(),
			"noop": noop.size(), "conflicts": conflicts.size()}}


func apply(plan_document: Dictionary, existing := {}) -> Dictionary:
	var applied: Array = []
	var blocked: Array = []
	for entry in plan_document.get("accepted", []):
		var destination := str(entry.get("destination", ""))
		if existing is Dictionary and existing.has(destination):
			blocked.append({"id": str(entry.get("id", "")), "reason": "destination exists"})
		else:
			applied.append(entry)
	applied.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	blocked.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	return {"applied": applied, "blocked": blocked, "noop": plan_document.get("noop", []),
		"conflicts": plan_document.get("conflicts", []),
		"counts": {"applied": applied.size(), "blocked": blocked.size(),
			"noop": plan_document.get("noop", []).size(),
			"conflicts": plan_document.get("conflicts", []).size()}}


func snapshot(plan_document: Dictionary) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(JSON.stringify(plan_document, "", true).to_utf8_buffer())
	return context.finish().hex_encode()


func clear() -> void:
	last_error = ""
