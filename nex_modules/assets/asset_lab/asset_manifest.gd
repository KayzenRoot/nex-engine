extends RefCounted
class_name AssetManifest

# NEX M11 AssetManifest: deterministic metadata validation for textures,
# models, audio, fonts, animation and VFX. It never imports or writes assets.

const KINDS := ["texture", "model", "audio", "font", "animation", "vfx"]
const MAP_SLOTS := ["albedo", "normal", "orm"]

var max_assets := 64
var max_total_bytes := 67108864
var max_texture_px := 4096
var last_error := ""


func configure(config := {}) -> bool:
	last_error = ""
	var next_assets := int(config.get("max_assets", max_assets))
	var next_bytes := int(config.get("max_total_bytes", max_total_bytes))
	var next_px := int(config.get("max_texture_px", max_texture_px))
	if next_assets < 1 or next_assets > 1000:
		last_error = "max_assets outside [1,1000]"
		return false
	if next_bytes < 1:
		last_error = "max_total_bytes must be positive"
		return false
	if next_px < 16 or next_px > 16384:
		last_error = "max_texture_px outside [16,16384]"
		return false
	max_assets = next_assets
	max_total_bytes = next_bytes
	max_texture_px = next_px
	return true


func _valid_id(value: String) -> bool:
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


func _valid_sha(value: String) -> bool:
	if value.length() != 64:
		return false
	for index in range(value.length()):
		if not "0123456789abcdef".contains(value[index]):
			return false
	return true


func _finding(code: String, severity: String, message: String) -> Dictionary:
	return {"code": code, "severity": severity, "message": message}


func validate_asset(asset: Dictionary) -> Array:
	var findings: Array = []
	var id := str(asset.get("id", ""))
	if not _valid_id(id):
		findings.append(_finding("invalid_id", "error", "asset id is invalid"))
	var kind := str(asset.get("kind", ""))
	if not KINDS.has(kind):
		findings.append(_finding("invalid_kind", "error", "unknown asset kind: " + kind))
	if str(asset.get("path", "")).is_empty():
		findings.append(_finding("missing_path", "error", "asset path is required"))
	if not _valid_sha(str(asset.get("sha256", "")).to_lower()):
		findings.append(_finding("invalid_sha256", "error", "sha256 must be 64 lowercase hex"))
	if int(asset.get("bytes", 0)) <= 0:
		findings.append(_finding("invalid_bytes", "error", "bytes must be positive"))
	if str(asset.get("license", "")).is_empty():
		findings.append(_finding("missing_license", "error", "license is required"))
	if str(asset.get("source", "")).is_empty():
		findings.append(_finding("missing_source", "error", "source is required"))
	if kind == "texture":
		var width := int(asset.get("width", 0))
		var height := int(asset.get("height", 0))
		if width <= 0 or height <= 0:
			findings.append(_finding("invalid_dimensions", "error", "texture dimensions must be positive"))
		elif width > max_texture_px or height > max_texture_px:
			findings.append(_finding("texture_too_large", "warn",
				"%dx%d exceeds %d px" % [width, height, max_texture_px]))
		if not bool(asset.get("mipmaps", false)):
			findings.append(_finding("missing_mipmaps", "warn", "texture has no mipmaps"))
		if asset.has("material_id"):
			var maps: Variant = asset.get("maps", [])
			if not (maps is Array) or maps.size() != 3:
				findings.append(_finding("incomplete_pbr_maps", "warn", "PBR material requires albedo/normal/orm"))
			else:
				var slots: Array = []
				for item in maps:
					slots.append(str(item))
				for slot in MAP_SLOTS:
					if not slots.has(slot):
						findings.append(_finding("incomplete_pbr_maps", "warn", "missing PBR slot: " + slot))
	if kind == "model":
		if float(asset.get("scale", 0.0)) <= 0.0:
			findings.append(_finding("invalid_scale", "error", "model scale must be positive"))
		if int(asset.get("lods", 0)) < 1:
			findings.append(_finding("model_without_lods", "warn", "model has no LODs"))
	findings.sort_custom(func(a, b): return str(a["code"]) < str(b["code"]))
	return findings


func validate_manifest(assets: Array) -> Dictionary:
	last_error = ""
	var findings: Array = []
	var ids: Dictionary = {}
	var total_bytes := 0
	var kinds: Dictionary = {}
	for asset in assets:
		if not (asset is Dictionary):
			findings.append(_finding("invalid_asset", "error", "asset must be an object"))
			continue
		var id := str(asset.get("id", ""))
		if ids.has(id):
			findings.append(_finding("duplicate_id", "error", "duplicate asset id: " + id))
		else:
			ids[id] = true
		total_bytes += int(asset.get("bytes", 0))
		var kind := str(asset.get("kind", "unknown"))
		kinds[kind] = int(kinds.get(kind, 0)) + 1
		findings.append_array(validate_asset(asset))
	if assets.size() > max_assets:
		findings.append(_finding("asset_budget_exceeded", "error",
			"%d assets exceeds %d" % [assets.size(), max_assets]))
	if total_bytes > max_total_bytes:
		findings.append(_finding("total_bytes_exceeded", "error",
			"%d bytes exceeds %d" % [total_bytes, max_total_bytes]))
	findings.sort_custom(func(a, b): return str(a["code"]) < str(b["code"]))
	var counts := {"error": 0, "warn": 0}
	for finding in findings:
		var severity := str(finding.get("severity", "warn"))
		if counts.has(severity):
			counts[severity] += 1
	return {"findings": findings, "counts": counts, "assets": assets.size(),
		"total_bytes": total_bytes, "kinds": kinds}


func clear() -> void:
	last_error = ""
