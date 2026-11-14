extends Node
class_name IdentityValidator

# NEX-M12-VALIDATOR prototype: deterministic visual-identity validator.
# Analysis only: no logo, theme, SVG or UI asset is generated or approved.
# Vocabulary follows the integrated identity.v1 contract.

const REPORT_SCHEMA := "identity_validation.report.v1"
const IDENTITY_SCHEMA := "identity.v1"
const ROLES: Array[String] = ["primary", "secondary", "accent", "background", "surface", "foreground", "error", "success", "warning"]

var last_error := ""
var _document: Dictionary = {}
var _last_report: Dictionary = {}


func load_document(document: Dictionary) -> bool:
	last_error = ""
	if String(document.get("schema_version", "")) != IDENTITY_SCHEMA:
		last_error = "document schema_version must be " + IDENTITY_SCHEMA
		return false
	if not document.get("palette") is Array or document["palette"].is_empty():
		last_error = "palette must be a non-empty array"
		return false
	for entry in document["palette"]:
		var palette_error := _validate_palette_entry(entry)
		if not palette_error.is_empty():
			last_error = palette_error
			return false
	var typography = document.get("typography")
	if not typography is Dictionary or _validate_typography(typography) != "":
		last_error = "typography is invalid"
		return false
	var logo = document.get("logo")
	if not logo is Dictionary or _validate_logo(logo) != "":
		last_error = "logo is invalid"
		return false
	var spacing = document.get("spacing")
	if not spacing is Dictionary or _validate_spacing(spacing) != "":
		last_error = "spacing is invalid"
		return false
	var accessibility = document.get("accessibility")
	if not accessibility is Dictionary or _validate_accessibility(accessibility) != "":
		last_error = "accessibility is invalid"
		return false
	if not document.get("provenance") is Dictionary:
		last_error = "provenance is required"
		return false
	_document = document.duplicate(true)
	return true


func audit() -> Dictionary:
	last_error = ""
	if _document.is_empty():
		return _invalid("no document is loaded")
	var palette: Array = _document["palette"]
	var roles := _roles(palette)
	var typography: Dictionary = _document["typography"]
	var logo: Dictionary = _document["logo"]
	var spacing: Dictionary = _document["spacing"]
	var accessibility: Dictionary = _document["accessibility"]
	var findings: Array = []
	var tokens: Array[String] = []
	for entry in palette:
		var token := String(entry["token"])
		if tokens.has(token):
			findings.append(_finding("duplicate_token", "high", "duplicate palette token", token))
		tokens.append(token)
	for role in ["primary", "background", "foreground"]:
		if not roles.has(role):
			findings.append(_finding("missing_required_role", "high", "required palette role is missing", role))
	var text_threshold := float(accessibility["min_text_contrast_ratio"])
	var large_threshold := float(accessibility["min_large_text_contrast_ratio"])
	var text_contrast := 0.0
	if roles.has("foreground") and roles.has("background"):
		text_contrast = _contrast(roles["foreground"], roles["background"])
		if text_contrast < text_threshold:
			findings.append(_finding("text_contrast_low", "high", "foreground/background contrast is below the text threshold"))
	for role in ["primary", "error"]:
		if roles.has(role) and roles.has("background"):
			var ratio := _contrast(roles[role], roles["background"])
			if ratio < large_threshold:
				findings.append(_finding("large_contrast_low", "high", role + " contrast is below the large-text threshold", role))
	for role in ["success", "warning"]:
		if roles.has(role) and roles.has("background"):
			var ratio := _contrast(roles[role], roles["background"])
			if ratio < large_threshold:
				findings.append(_finding("large_contrast_low", "high", role + " contrast is below the large-text threshold", role))
	if roles.has("accent") and roles.has("background"):
		if _contrast(roles["accent"], roles["background"]) < 3.0:
			findings.append(_finding("accent_contrast_low", "low", "accent contrast is below 3:1", "accent"))
	if int(typography["display_size_px"]) <= int(typography["body_size_px"]):
		findings.append(_finding("display_not_larger", "high", "display size must exceed body size"))
	var weights: Array = typography["weights"]
	var seen_weights: Array[int] = []
	for weight in weights:
		if seen_weights.has(int(weight)):
			findings.append(_finding("duplicate_weight", "high", "duplicate font weight", str(weight)))
		seen_weights.append(int(weight))
		if int(weight) % 100 != 0:
			findings.append(_finding("weight_not_multiple", "medium", "font weight is not a multiple of 100", str(weight)))
	for key in ["mark_view_box", "wordmark_view_box"]:
		var box: Array = logo[key]
		if float(box[2]) <= 0.0 or float(box[3]) <= 0.0:
			findings.append(_finding("view_box_invalid", "high", "logo viewBox width/height must be positive", key))
	var scale: Array = spacing["scale"]
	var base := int(spacing["base_px"])
	for index in range(scale.size()):
		if float(scale[index]) < base:
			findings.append(_finding("spacing_below_base", "high", "spacing value is below base_px", str(scale[index])))
		if index > 0 and float(scale[index]) <= float(scale[index - 1]):
			findings.append(_finding("spacing_not_ascending", "high", "spacing scale is not strictly ascending"))
	if large_threshold > text_threshold:
		findings.append(_finding("contrast_threshold_order", "high", "large-text threshold exceeds text threshold"))
	if int(accessibility["min_focus_ring_px"]) < 1:
		findings.append(_finding("focus_ring_too_small", "high", "focus ring must be at least 1 px"))
	var provenance: Dictionary = _document["provenance"]
	if provenance.get("measurement_status") == "MEASURED" and not provenance.has("evidence_uri"):
		findings.append(_finding("provenance_without_evidence", "high", "MEASURED provenance requires evidence_uri"))
	var report := {
		"schema_version": REPORT_SCHEMA,
		"verdict": _verdict(findings),
		"metrics": {
			"palette_tokens": palette.size(),
			"roles_present": roles.size(),
			"text_contrast_ratio": snappedf(text_contrast, 0.01),
			"large_text_threshold": large_threshold,
			"spacing_steps": scale.size(),
			"logo_variants": 3,
		},
		"findings": _sorted_findings(findings),
		"summary": _summary(findings),
		"recommendations": _recommendations(findings),
		"limitations": _limitations(),
	}
	_last_report = report
	return report


func _validate_palette_entry(entry) -> String:
	if not entry is Dictionary:
		return "palette entry must be an object"
	if not _is_contract_id(String(entry.get("token", ""))):
		return "palette token does not match the contract"
	if not _is_hex(String(entry.get("hex", ""))):
		return "palette hex must be lowercase #rrggbb"
	if not ROLES.has(String(entry.get("role", ""))):
		return "palette role is invalid"
	return ""


func _validate_typography(typography: Dictionary) -> String:
	if String(typography.get("font_family", "")).is_empty():
		return "font_family is required"
	if not _is_integer(typography.get("display_size_px")) or int(typography["display_size_px"]) < 24 or int(typography["display_size_px"]) > 200:
		return "display_size_px outside [24,200]"
	if not _is_integer(typography.get("body_size_px")) or int(typography["body_size_px"]) < 10 or int(typography["body_size_px"]) > 48:
		return "body_size_px outside [10,48]"
	if not _is_number(typography.get("line_height_ratio")) or float(typography["line_height_ratio"]) < 1.0 or float(typography["line_height_ratio"]) > 2.5:
		return "line_height_ratio outside [1,2.5]"
	var weights = typography.get("weights")
	if not weights is Array or weights.is_empty() or weights.size() > 8:
		return "weights must contain 1..8 entries"
	for weight in weights:
		if not _is_integer(weight) or int(weight) < 100 or int(weight) > 900:
			return "font weight outside [100,900]"
	return ""


func _validate_logo(logo: Dictionary) -> String:
	for key in ["mark_svg_uri", "wordmark_svg_uri"]:
		if String(logo.get(key, "")).is_empty():
			return key + " is required"
	for key in ["mark_sha256", "wordmark_sha256", "monochrome_sha256"]:
		if not _is_sha256(String(logo.get(key, ""))):
			return key + " must be lowercase 64-hex"
	for key in ["mark_view_box", "wordmark_view_box"]:
		var box = logo.get(key)
		if not box is Array or box.size() != 4:
			return key + " must contain 4 numbers"
		for value in box:
			if not _is_number(value):
				return key + " must contain finite numbers"
	if not _is_number(logo.get("clear_space_ratio")) or float(logo["clear_space_ratio"]) < 0.0 or float(logo["clear_space_ratio"]) > 1.0:
		return "clear_space_ratio outside [0,1]"
	return ""


func _validate_spacing(spacing: Dictionary) -> String:
	if not _is_integer(spacing.get("base_px")) or int(spacing["base_px"]) < 2 or int(spacing["base_px"]) > 32:
		return "base_px outside [2,32]"
	var scale = spacing.get("scale")
	if not scale is Array or scale.size() < 3 or scale.size() > 12:
		return "scale must contain 3..12 entries"
	for value in scale:
		if not _is_number(value) or float(value) < 1.0 or float(value) > 512.0:
			return "scale value outside [1,512]"
	if not _is_integer(spacing.get("max_content_width_px")) or int(spacing["max_content_width_px"]) < 320 or int(spacing["max_content_width_px"]) > 7680:
		return "max_content_width_px outside [320,7680]"
	return ""


func _validate_accessibility(accessibility: Dictionary) -> String:
	for key in ["min_text_contrast_ratio", "min_large_text_contrast_ratio"]:
		if not _is_number(accessibility.get(key)) or float(accessibility[key]) < 3.0 or float(accessibility[key]) > 21.0:
			return key + " outside [3,21]"
	if not accessibility.get("requires_focus_indicator") is bool:
		return "requires_focus_indicator must be boolean"
	if not _is_integer(accessibility.get("min_focus_ring_px")) or int(accessibility["min_focus_ring_px"]) < 1 or int(accessibility["min_focus_ring_px"]) > 16:
		return "min_focus_ring_px outside [1,16]"
	return ""


func _roles(palette: Array) -> Dictionary:
	var roles: Dictionary = {}
	for entry in palette:
		roles[String(entry["role"])] = String(entry["hex"])
	return roles


func _luminance(hex_color: String) -> float:
	var channels: Array[float] = []
	for index in [1, 3, 5]:
		var channel := float(hex_color.substr(index, 2).hex_to_int()) / 255.0
		channels.append(channel / 12.92 if channel <= 0.04045 else pow((channel + 0.055) / 1.055, 2.4))
	return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


func _contrast(first: String, second: String) -> float:
	var high := maxf(_luminance(first), _luminance(second))
	var low := minf(_luminance(first), _luminance(second))
	return (high + 0.05) / (low + 0.05)


func _verdict(findings: Array) -> String:
	for finding in findings:
		if finding["severity"] == "high":
			return "BLOCKED"
	for finding in findings:
		if finding["severity"] == "medium":
			return "REVIEW_REQUIRED"
	return "READY_FOR_UI"


func _summary(findings: Array) -> Dictionary:
	var summary := {"high": 0, "medium": 0, "low": 0, "info": 0}
	for finding in findings:
		summary[finding["severity"]] += 1
	return summary


func _finding(code: String, severity: String, message: String, subject := "") -> Dictionary:
	var finding := {"code": code, "severity": severity, "message": message}
	if not subject.is_empty():
		finding["subject"] = subject
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
			"text_contrast_low", "large_contrast_low", "accent_contrast_low":
				actions.append("increase_contrast")
			"missing_required_role", "duplicate_token":
				actions.append("fix_palette_roles")
			"display_not_larger", "duplicate_weight", "weight_not_multiple":
				actions.append("fix_typography")
			"view_box_invalid":
				actions.append("fix_logo_view_box")
			"spacing_below_base", "spacing_not_ascending":
				actions.append("fix_spacing_scale")
			"contrast_threshold_order", "focus_ring_too_small":
				actions.append("fix_accessibility_thresholds")
			"provenance_without_evidence":
				actions.append("add_provenance_evidence")
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
		"analysis only: no logo, theme, SVG or UI asset is generated or approved",
		"contrast is computed from declared hex values, not measured on screen",
		"typography and spacing are validated structurally, not visually",
		"brand approval and trademark review are out of scope",
		"no FPS, rendering or quality claim is produced",
		"no scene, engine or project.godot integration",
	]


func _invalid(reason: String) -> Dictionary:
	last_error = reason
	var report := {
		"schema_version": REPORT_SCHEMA,
		"verdict": "INVALID_INPUT",
		"metrics": {},
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


func _is_hex(value: String) -> bool:
	if value.length() != 7 or not value.begins_with("#"):
		return false
	for character in value.substr(1):
		if not "0123456789abcdef".contains(character):
			return false
	return true


func _is_sha256(value: String) -> bool:
	if value.length() != 64:
		return false
	for character in value:
		if not "0123456789abcdef".contains(character):
			return false
	return true


func _is_number(value) -> bool:
	return (value is int or value is float) and not (value is bool) and is_finite(float(value))


func _is_integer(value) -> bool:
	return value is int or (value is float and is_finite(value) and value == floor(value))


func get_last_report() -> Dictionary:
	return _last_report


func clear() -> void:
	_document.clear()
	_last_report = {}
	last_error = ""
