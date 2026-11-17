extends RefCounted
class_name PerfLint

# NEX M09 PerfLint: deterministic, event-driven asset/scene linting.
# It reports warnings only; it does not measure performance or modify assets.

const SEVERITIES := ["info", "warn", "error"]
const FORMATS := ["png", "jpg", "webp", "exr", "svg"]

var max_texture_px := 2048
var max_lights := 8
var max_draw_calls := 512
var max_alpha_layers := 24
var max_shadowed_lights := 4
var max_file_bytes := 16777216
var last_error := ""
var _asset_ids: Dictionary = {}


func configure(config := {}) -> bool:
	last_error = ""
	var next_texture := int(config.get("max_texture_px", max_texture_px))
	var next_lights := int(config.get("max_lights", max_lights))
	var next_draws := int(config.get("max_draw_calls", max_draw_calls))
	var next_alpha := int(config.get("max_alpha_layers", max_alpha_layers))
	var next_shadowed := int(config.get("max_shadowed_lights", max_shadowed_lights))
	var next_bytes := int(config.get("max_file_bytes", max_file_bytes))
	if next_texture < 16 or next_texture > 16384:
		last_error = "max_texture_px outside [16,16384]"
		return false
	if next_lights < 0 or next_lights > 256 or next_draws < 0 or next_draws > 100000:
		last_error = "light/draw budget is invalid"
		return false
	if next_alpha < 0 or next_alpha > 4096 or next_shadowed < 0 or next_shadowed > 64:
		last_error = "alpha/shadow budget is invalid"
		return false
	if next_bytes < 1:
		last_error = "max_file_bytes must be positive"
		return false
	max_texture_px = next_texture
	max_lights = next_lights
	max_draw_calls = next_draws
	max_alpha_layers = next_alpha
	max_shadowed_lights = next_shadowed
	max_file_bytes = next_bytes
	return true


func _finding(code: String, severity: String, message: String) -> Dictionary:
	return {"code": code, "severity": severity, "message": message}


func lint_asset(asset: Dictionary) -> Array:
	var findings: Array = []
	var id := str(asset.get("id", ""))
	if id.is_empty():
		findings.append(_finding("missing_id", "error", "asset id is required"))
	elif _asset_ids.has(id):
		findings.append(_finding("duplicate_id", "error", "duplicate asset id: " + id))
	else:
		_asset_ids[id] = true
	var path := str(asset.get("path", ""))
	if path.is_empty():
		findings.append(_finding("missing_path", "error", "asset path is required"))
	var width := int(asset.get("width", 0))
	var height := int(asset.get("height", 0))
	if width > max_texture_px or height > max_texture_px:
		findings.append(_finding("texture_too_large", "warn",
			"%dx%d exceeds %d px" % [width, height, max_texture_px]))
	if width <= 0 or height <= 0:
		findings.append(_finding("invalid_dimensions", "error", "width/height must be positive"))
	var format := str(asset.get("format", ""))
	if not FORMATS.has(format):
		findings.append(_finding("unknown_format", "warn", "unknown texture format: " + format))
	if str(asset.get("license", "")).is_empty():
		findings.append(_finding("missing_license", "error", "asset license is required"))
	if int(asset.get("bytes", 0)) > max_file_bytes:
		findings.append(_finding("oversized_file", "warn",
			"%d bytes exceeds %d" % [int(asset.get("bytes", 0)), max_file_bytes]))
	if bool(asset.get("sync_load", false)):
		findings.append(_finding("sync_load_risk", "warn", "asset is loaded synchronously"))
	findings.sort_custom(func(a, b): return str(a["code"]) < str(b["code"]))
	return findings


func lint_scene(scene: Dictionary) -> Array:
	var findings: Array = []
	var id := str(scene.get("id", ""))
	if id.is_empty():
		findings.append(_finding("missing_scene_id", "error", "scene id is required"))
	if int(scene.get("lights", 0)) > max_lights:
		findings.append(_finding("light_budget_exceeded", "warn",
			"%d lights exceeds %d" % [int(scene.get("lights", 0)), max_lights]))
	if int(scene.get("draw_calls", 0)) > max_draw_calls:
		findings.append(_finding("draw_call_budget_exceeded", "warn",
			"%d draw calls exceeds %d" % [int(scene.get("draw_calls", 0)), max_draw_calls]))
	if int(scene.get("alpha_layers", 0)) > max_alpha_layers:
		findings.append(_finding("alpha_overdraw_risk", "warn",
			"%d alpha layers exceeds %d" % [int(scene.get("alpha_layers", 0)), max_alpha_layers]))
	if int(scene.get("shadowed_lights", 0)) > max_shadowed_lights:
		findings.append(_finding("shadow_budget_exceeded", "warn",
			"%d shadowed lights exceeds %d" % [int(scene.get("shadowed_lights", 0)), max_shadowed_lights]))
	if int(scene.get("sync_loads", 0)) > 0:
		findings.append(_finding("sync_load_risk", "warn", "scene contains synchronous loads"))
	findings.sort_custom(func(a, b): return str(a["code"]) < str(b["code"]))
	return findings


func summarize(findings: Array) -> Dictionary:
	var counts := {"info": 0, "warn": 0, "error": 0}
	var codes: Dictionary = {}
	var highest := "info"
	for finding in findings:
		var severity := str(finding.get("severity", "info"))
		if counts.has(severity):
			counts[severity] += 1
		var code := str(finding.get("code", "unknown"))
		codes[code] = int(codes.get(code, 0)) + 1
		if severity == "error" or (severity == "warn" and highest == "info"):
			highest = severity
	return {"total": findings.size(), "counts": counts, "codes": codes, "highest": highest}


func lint_bundle(assets: Array, scenes: Array) -> Dictionary:
	_asset_ids.clear()
	var findings: Array = []
	for asset in assets:
		findings.append_array(lint_asset(asset))
	for scene in scenes:
		findings.append_array(lint_scene(scene))
	findings.sort_custom(func(a, b): return str(a["code"]) < str(b["code"]))
	return {"findings": findings, "summary": summarize(findings)}


func clear() -> void:
	_asset_ids.clear()
	last_error = ""
