extends Node
class_name TextureBudgetPlanner

# NEX-M04-TEXTUREBUDGET prototype: deterministic texture-budget planner.
# Planning only: no texture is loaded, decoded, packed or rendered.
# Vocabulary follows the integrated material.v1 contract.

const REPORT_SCHEMA := "texture_budget.report.v1"
const SLOTS: Array[String] = ["albedo", "normal", "orm", "emission", "detail"]
const MAX_DIMENSION := 16384
const MIN_DOWNSCALE_DIMENSION := 64
const TILE_PX := 256
const TIGHT_RATIO := 0.90
const MAX_DECODED_BYTES := 17179869184
const MAX_TEXTURE_COUNT := 1024

var max_decoded_bytes := 268435456
var max_texture_count := 512
var atlas_size := 4096
var last_error := ""
var _last_report: Dictionary = {}


func configure(config := {}) -> bool:
	last_error = ""
	var next_bytes := int(config.get("max_decoded_bytes", max_decoded_bytes))
	var next_count := int(config.get("max_texture_count", max_texture_count))
	var next_atlas := int(config.get("atlas_size", atlas_size))
	if next_bytes < 0 or next_bytes > MAX_DECODED_BYTES:
		last_error = "max_decoded_bytes outside [0,17179869184]"
		return false
	if next_count < 0 or next_count > MAX_TEXTURE_COUNT:
		last_error = "max_texture_count outside [0,1024]"
		return false
	if next_atlas < 256 or next_atlas > 8192:
		last_error = "atlas_size outside [256,8192]"
		return false
	max_decoded_bytes = next_bytes
	max_texture_count = next_count
	atlas_size = next_atlas
	return true


func analyze(materials: Array) -> Dictionary:
	last_error = ""
	if not materials is Array:
		return _invalid("materials must be an array")
	var validation := _validate(materials)
	if not validation.is_empty():
		return _invalid(validation)
	var collected := _collect(materials)
	var unique: Array = collected["unique"]
	var total_bytes := int(collected["total_bytes"])
	var unique_bytes := int(collected["unique_bytes"])
	var duplicates := int(collected["duplicate_refs"])
	var findings: Array = []
	var seen_mismatches: Dictionary = {}
	for sha in collected["mismatches"]:
		if not seen_mismatches.has(sha):
			seen_mismatches[sha] = true
			findings.append(_finding("digest_dimension_mismatch", "high", "same SHA-256 with differing dimensions or mipmaps", String(sha)))
	if unique_bytes > max_decoded_bytes:
		findings.append(_finding("over_decoded_bytes", "high", "decoded bytes exceed the budget"))
	if unique.size() > max_texture_count:
		findings.append(_finding("over_texture_count", "high", "texture count exceeds the budget"))
	if duplicates > 0:
		findings.append(_finding("duplicate_textures", "low", "repeated SHA-256 references can be deduplicated"))
	var tiles_required := 0
	var tiles_available := int(atlas_size / TILE_PX) * int(atlas_size / TILE_PX)
	var detail_count := 0
	for entry in unique:
		tiles_required += ceili(float(entry["width_px"]) / TILE_PX) * ceili(float(entry["height_px"]) / TILE_PX)
		if entry["slot"] == "detail":
			detail_count += 1
		if int(entry["width_px"]) > 4096 or int(entry["height_px"]) > 4096:
			findings.append(_finding("oversized_texture", "medium", "texture exceeds 4096 px", entry["sha256"]))
		if not _is_power_of_two(int(entry["width_px"])) or not _is_power_of_two(int(entry["height_px"])):
			findings.append(_finding("non_power_of_two", "low", "texture dimensions are not powers of two", entry["sha256"]))
		if entry["slot"] in ["normal", "orm"] and bool(entry["srgb"]):
			findings.append(_finding("srgb_on_data_texture", "medium", "normal/ORM data must not be sRGB", entry["sha256"]))
		if not bool(entry["mipmaps"]) and maxi(int(entry["width_px"]), int(entry["height_px"])) > 256:
			findings.append(_finding("missing_mips", "low", "large texture has no mipmaps", entry["sha256"]))
	var pressure_ratio := 0.0
	if tiles_available > 0:
		pressure_ratio = float(tiles_required) / float(tiles_available)
	if pressure_ratio > 1.0:
		findings.append(_finding("atlas_pressure", "medium", "texture tiles exceed the atlas tile budget"))
	if detail_count > 0 and (unique_bytes > max_decoded_bytes or pressure_ratio > 1.0):
		findings.append(_finding("detail_slot_pressure", "low", "detail textures add pressure under budget stress"))
	var downscale := _plan_downscale(unique, max_decoded_bytes)
	var verdict := _verdict(unique_bytes, unique.size())
	var report := {
		"schema_version": REPORT_SCHEMA,
		"verdict": verdict,
		"materials": materials.size(),
		"texture_refs": int(collected["refs"]),
		"unique_textures": unique,
		"decoded_bytes_total": total_bytes,
		"decoded_bytes_dedup": unique_bytes,
		"duplicate_refs": duplicates,
		"duplicate_bytes_saved": total_bytes - unique_bytes,
		"budget": {
			"max_decoded_bytes": max_decoded_bytes,
			"max_texture_count": max_texture_count,
			"atlas_size": atlas_size,
			"tile_px": TILE_PX,
		},
		"atlas": {
			"tiles_required": tiles_required,
			"tiles_available": tiles_available,
			"pressure_ratio": snappedf(pressure_ratio, 0.001),
		},
		"downscale_plan": downscale["steps"],
		"projected_bytes_after_plan": downscale["projected_bytes"],
		"findings": _sorted_findings(findings),
		"recommendations": _recommendations(duplicates, unique.size(), unique_bytes, downscale, pressure_ratio),
		"limitations": _limitations(),
	}
	_last_report = report
	return report


func _validate(materials: Array) -> String:
	for index in range(materials.size()):
		var material = materials[index]
		if not material is Dictionary:
			return "materials[%d] must be an object" % index
		if not material.has("material_id") or not material["material_id"] is String:
			return "materials[%d] requires material_id" % index
		if not _is_contract_id(String(material["material_id"])):
			return "materials[%d].material_id does not match material.v1" % index
		if not material.has("textures") or not material["textures"] is Array:
			return "materials[%d] requires textures" % index
		for texture_index in range(material["textures"].size()):
			var error := _validate_texture(material["textures"][texture_index], index, texture_index)
			if not error.is_empty():
				return error
	return ""


func _validate_texture(texture, material_index: int, texture_index: int) -> String:
	var prefix := "materials[%d].textures[%d]" % [material_index, texture_index]
	if not texture is Dictionary:
		return prefix + " must be an object"
	if not texture.has("slot") or not SLOTS.has(String(texture["slot"])):
		return prefix + ".slot is invalid"
	if not texture.has("sha256") or not texture["sha256"] is String:
		return prefix + ".sha256 is required"
	if not _is_sha256(String(texture["sha256"])):
		return prefix + ".sha256 must be lowercase 64-hex"
	for key in ["width_px", "height_px"]:
		if not texture.has(key) or not _is_integer(texture[key]):
			return prefix + "." + key + " must be an integer"
		var dimension := int(texture[key])
		if dimension < 1 or dimension > MAX_DIMENSION:
			return prefix + "." + key + " outside [1,16384]"
	for key in ["mipmaps", "srgb"]:
		if not texture.has(key) or not texture[key] is bool:
			return prefix + "." + key + " must be boolean"
	return ""


func _is_integer(value) -> bool:
	return value is int or (value is float and is_finite(value) and value == floor(value))


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


func _is_power_of_two(value: int) -> bool:
	return value > 0 and (value & (value - 1)) == 0


func _bytes(width: int, height: int, mipmaps: bool) -> int:
	var base := width * height * 4
	if mipmaps:
		return int(round(float(base) * 4.0 / 3.0))
	return base


func _collect(materials: Array) -> Dictionary:
	var unique: Dictionary = {}
	var total_bytes := 0
	var refs := 0
	var mismatches: Array[String] = []
	for material in materials:
		for texture in material["textures"]:
			refs += 1
			var sha: String = texture["sha256"]
			var width := int(texture["width_px"])
			var height := int(texture["height_px"])
			var mipmaps := bool(texture["mipmaps"])
			var size := _bytes(width, height, mipmaps)
			total_bytes += size
			if unique.has(sha):
				var existing: Dictionary = unique[sha]
				if int(existing["width_px"]) != width or int(existing["height_px"]) != height or bool(existing["mipmaps"]) != mipmaps:
					mismatches.append(sha)
				existing["refs"] += 1
				continue
			unique[sha] = {
				"sha256": sha,
				"slot": String(texture["slot"]),
				"width_px": width,
				"height_px": height,
				"mipmaps": mipmaps,
				"srgb": bool(texture["srgb"]),
				"bytes": size,
				"refs": 1,
			}
	var entries: Array = []
	var unique_bytes := 0
	for sha in unique.keys():
		entries.append(unique[sha])
		unique_bytes += int(unique[sha]["bytes"])
	entries.sort_custom(func(a, b): return String(a["sha256"]) < String(b["sha256"]))
	return {
		"unique": entries,
		"unique_bytes": unique_bytes,
		"total_bytes": total_bytes,
		"refs": refs,
		"duplicate_refs": refs - entries.size(),
		"mismatches": mismatches,
	}


func _plan_downscale(unique: Array, target_bytes: int) -> Dictionary:
	var working: Array = []
	var total := 0
	for entry in unique:
		var copy: Dictionary = entry.duplicate(true)
		working.append(copy)
		total += int(copy["bytes"])
	working.sort_custom(func(a, b):
		if int(a["bytes"]) == int(b["bytes"]):
			return String(a["sha256"]) < String(b["sha256"])
		return int(a["bytes"]) > int(b["bytes"])
	)
	var steps: Array = []
	for entry in working:
		if total <= target_bytes:
			break
		var width := int(entry["width_px"])
		var height := int(entry["height_px"])
		while total > target_bytes and width > MIN_DOWNSCALE_DIMENSION and height > MIN_DOWNSCALE_DIMENSION:
			var next_width := maxi(MIN_DOWNSCALE_DIMENSION, width / 2)
			var next_height := maxi(MIN_DOWNSCALE_DIMENSION, height / 2)
			var next_bytes := _bytes(next_width, next_height, bool(entry["mipmaps"]))
			var saved := int(entry["bytes"]) - next_bytes
			if saved <= 0:
				break
			steps.append({
				"sha256": entry["sha256"],
				"from_px": [width, height],
				"to_px": [next_width, next_height],
				"saved_bytes": saved,
			})
			width = next_width
			height = next_height
			entry["width_px"] = width
			entry["height_px"] = height
			entry["bytes"] = next_bytes
			total -= saved
	return {"steps": steps, "projected_bytes": total}


func _verdict(unique_bytes: int, unique_count: int) -> String:
	if unique_bytes > max_decoded_bytes or unique_count > max_texture_count:
		return "OVER_BUDGET"
	if float(unique_bytes) >= float(max_decoded_bytes) * TIGHT_RATIO:
		return "TIGHT"
	if max_texture_count > 0 and float(unique_count) >= float(max_texture_count) * TIGHT_RATIO:
		return "TIGHT"
	return "FIT"


func _finding(code: String, severity: String, message: String, sha := "") -> Dictionary:
	var finding := {"code": code, "severity": severity, "message": message}
	if not sha.is_empty():
		finding["sha256"] = sha
	return finding


func _sorted_findings(findings: Array) -> Array:
	var order := {"high": 0, "medium": 1, "low": 2, "info": 3}
	findings.sort_custom(func(a, b):
		if order[a["severity"]] == order[b["severity"]]:
			return String(a["code"]) < String(b["code"])
		return order[a["severity"]] < order[b["severity"]]
	)
	return findings


func _recommendations(duplicates: int, unique_count: int, unique_bytes: int, downscale: Dictionary, pressure: float) -> Array:
	var recommendations: Array = []
	if duplicates > 0:
		recommendations.append({
			"action": "deduplicate_textures",
			"quality_cost": "none",
			"duplicate_refs": duplicates,
		})
	if unique_bytes > max_decoded_bytes:
		recommendations.append({
			"action": "downscale_largest",
			"quality_cost": "medium",
			"steps": downscale["steps"].size(),
			"projected_bytes": downscale["projected_bytes"],
		})
	if unique_count > max_texture_count:
		recommendations.append({
			"action": "reduce_texture_count",
			"quality_cost": "medium",
			"excess": unique_count - max_texture_count,
		})
	if pressure > 1.0:
		recommendations.append({
			"action": "increase_atlas_or_split",
			"quality_cost": "low",
		})
	return recommendations


func _limitations() -> Array[String]:
	return [
		"planning only: no texture is loaded, decoded, uploaded or rendered",
		"decoded size is width*height*4 with a 4/3 mipmap factor, not measured VRAM",
		"atlas pressure is tile arithmetic (256 px tiles), not an allocator simulation",
		"downscale steps reduce dimensions by half down to 64 px; no resampling is performed",
		"visual quality and runtime cost are INCONCLUSIVE_NOT_RUN",
		"no scene, engine or project.godot integration",
	]


func _invalid(reason: String) -> Dictionary:
	last_error = reason
	var report := {
		"schema_version": REPORT_SCHEMA,
		"verdict": "INVALID_INPUT",
		"materials": 0,
		"texture_refs": 0,
		"unique_textures": [],
		"decoded_bytes_total": 0,
		"decoded_bytes_dedup": 0,
		"duplicate_refs": 0,
		"duplicate_bytes_saved": 0,
		"budget": {
			"max_decoded_bytes": max_decoded_bytes,
			"max_texture_count": max_texture_count,
			"atlas_size": atlas_size,
			"tile_px": TILE_PX,
		},
		"atlas": {"tiles_required": 0, "tiles_available": 0, "pressure_ratio": 0.0},
		"downscale_plan": [],
		"projected_bytes_after_plan": 0,
		"findings": [],
		"recommendations": [],
		"limitations": _limitations(),
		"reason": reason,
	}
	_last_report = report
	return report


func get_last_report() -> Dictionary:
	return _last_report


func clear() -> void:
	max_decoded_bytes = 268435456
	max_texture_count = 512
	atlas_size = 4096
	last_error = ""
	_last_report = {}
