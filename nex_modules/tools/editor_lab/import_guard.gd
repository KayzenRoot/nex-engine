extends RefCounted
class_name ImportGuard

# NEX M09 ImportGuard: deterministic import planning with conflict and NOOP
# detection. It never writes files and never overwrites user material.

const ALLOWED_EXTENSIONS := ["png", "jpg", "webp", "tres", "tscn", "json"]
const MAX_FILE_BYTES := 67108864

var allowed_extensions: Array = ALLOWED_EXTENSIONS.duplicate()
var max_file_bytes := MAX_FILE_BYTES
var last_error := ""


func configure(config := {}) -> bool:
	last_error = ""
	var extensions: Variant = config.get("allowed_extensions", allowed_extensions)
	if not (extensions is Array) or extensions.is_empty():
		last_error = "allowed_extensions must be a non-empty array"
		return false
	var next: Array[String] = []
	for extension in extensions:
		if not (extension is String) or String(extension).is_empty():
			last_error = "allowed extension must be a non-empty string"
			return false
		next.append(String(extension).to_lower())
	var next_bytes := int(config.get("max_file_bytes", max_file_bytes))
	if next_bytes < 1 or next_bytes > MAX_FILE_BYTES:
		last_error = "max_file_bytes outside [1,64MB]"
		return false
	allowed_extensions = next
	max_file_bytes = next_bytes
	return true


func _valid_sha(value: String) -> bool:
	if value.length() != 64:
		return false
	for index in range(value.length()):
		if not "0123456789abcdef".contains(value[index]):
			return false
	return true


func plan(files: Array, existing := {}) -> Dictionary:
	last_error = ""
	var accepted: Array = []
	var rejected: Array = []
	var noop: Array = []
	var conflicts: Array = []
	for file in files:
		if not (file is Dictionary):
			rejected.append({"id": "", "reason": "file must be an object"})
			continue
		var id := str(file.get("id", ""))
		var path := str(file.get("path", ""))
		var destination := str(file.get("destination", ""))
		var extension := str(file.get("extension", "")).to_lower()
		var bytes := int(file.get("bytes", 0))
		var sha := str(file.get("sha256", "")).to_lower()
		var reason := ""
		if id.is_empty() or path.is_empty() or destination.is_empty():
			reason = "id/path/destination are required"
		elif not allowed_extensions.has(extension):
			reason = "extension not allowed: " + extension
		elif bytes < 1 or bytes > max_file_bytes:
			reason = "file size outside [1,max]"
		elif not _valid_sha(sha):
			reason = "sha256 must be 64 lowercase hex"
		if not reason.is_empty():
			rejected.append({"id": id, "reason": reason})
			continue
		var entry := {"id": id, "path": path, "destination": destination, "bytes": bytes, "sha256": sha}
		if existing is Dictionary and existing.has(destination):
			if str(existing[destination]) == sha:
				noop.append(entry)
			else:
				conflicts.append({"id": id, "destination": destination, "reason": "destination hash differs"})
		else:
			accepted.append(entry)
	accepted.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	rejected.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	noop.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	conflicts.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	return {
		"accepted": accepted, "rejected": rejected, "noop": noop, "conflicts": conflicts,
		"counts": {"accepted": accepted.size(), "rejected": rejected.size(),
			"noop": noop.size(), "conflicts": conflicts.size()},
	}


func apply(plan_document: Dictionary, existing := {}) -> Dictionary:
	last_error = ""
	var applied: Array = []
	var blocked: Array = []
	for entry in plan_document.get("accepted", []):
		var destination := str(entry.get("destination", ""))
		if existing is Dictionary and existing.has(destination):
			blocked.append({"id": str(entry.get("id", "")), "reason": "destination already exists"})
		else:
			applied.append(entry)
	applied.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	blocked.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	return {"applied": applied, "blocked": blocked,
		"noop": plan_document.get("noop", []), "conflicts": plan_document.get("conflicts", []),
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
