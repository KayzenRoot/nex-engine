extends RefCounted
class_name FillRateXRay

# NEX M06-S10 FillRate X-Ray: deterministic overdraw proxy from particle
# count, sprite area, layers and viewport area. It is not a fragment counter.

var last_error := ""


func estimate(config := {}) -> Dictionary:
	last_error = ""
	var count := int(config.get("count", 0))
	var width := int(config.get("width", 0))
	var height := int(config.get("height", 0))
	var sprite_px := float(config.get("sprite_px", 0.0))
	var layers := int(config.get("layers", 1))
	if count < 0 or count > 1000000:
		last_error = "count outside [0,1000000]"
		return {"ok": false, "reason": last_error}
	if width < 1 or height < 1:
		last_error = "viewport must be positive"
		return {"ok": false, "reason": last_error}
	if not is_finite(sprite_px) or sprite_px <= 0.0:
		last_error = "sprite_px must be finite and positive"
		return {"ok": false, "reason": last_error}
	if layers < 1 or layers > 64:
		last_error = "layers outside [1,64]"
		return {"ok": false, "reason": last_error}
	var screen_px := float(width * height)
	var covered_px := float(count) * sprite_px * sprite_px * float(layers)
	var overdraw := covered_px / screen_px
	var coverage_pct := minf(100.0, overdraw * 100.0)
	var band := "low"
	if overdraw >= 4.0:
		band = "high"
	elif overdraw >= 1.0:
		band = "medium"
	return {"ok": true, "count": count, "viewport_px": [width, height],
		"sprite_px": sprite_px, "layers": layers, "overdraw_proxy": snappedf(overdraw, 0.0001),
		"coverage_pct": snappedf(coverage_pct, 0.001), "band": band}


func plan_matrix(counts: Array, resolutions: Array, sprite_px: float, layers := 1) -> Dictionary:
	var cells: Array = []
	for count in counts:
		for resolution in resolutions:
			if resolution.size() != 2:
				last_error = "resolution must have 2 values"
				return {"ok": false, "reason": last_error}
			var result := estimate({"count": count, "width": resolution[0], "height": resolution[1],
				"sprite_px": sprite_px, "layers": layers})
			if not bool(result.get("ok", false)):
				return result
			cells.append(result)
	return {"ok": true, "cells": cells, "count": cells.size()}
