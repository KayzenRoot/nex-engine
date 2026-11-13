extends SceneTree

# Headless deterministic smoke for NEX M04-TEXTUREBUDGET TextureBudgetPlanner.
# godot --headless --path nex_modules/materials/texturebudget --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _material(material_id: String, textures: Array) -> Dictionary:
	return {"material_id": material_id, "textures": textures}


func _texture(slot: String, sha: String, width: int, height: int, mipmaps := true, srgb := false) -> Dictionary:
	return {
		"slot": slot, "sha256": sha, "width_px": width, "height_px": height,
		"mipmaps": mipmaps, "srgb": srgb,
	}


func _materials() -> Array:
	return [
		_material("stone", [
			_texture("albedo", "a".repeat(64), 2048, 2048, true, true),
			_texture("normal", "b".repeat(64), 2048, 2048, true, false),
			_texture("orm", "c".repeat(64), 1024, 1024, true, false),
		]),
		_material("stone-copy", [
			_texture("albedo", "a".repeat(64), 2048, 2048, true, true),
		]),
	]


func _has_finding(report: Dictionary, code: String) -> bool:
	for finding in report["findings"]:
		if finding["code"] == code:
			return true
	return false


func _run() -> void:
	var packed := load("res://main.tscn") as PackedScene
	_check(packed != null, "main scene loads")
	if packed == null:
		_finish()
		return
	var planner = packed.instantiate()
	root.add_child(planner)
	await process_frame

	_check(planner.configure({}), "default configuration accepted")
	_check(not planner.configure({"max_decoded_bytes": -1}), "negative byte budget rejected")
	_check(not planner.configure({"max_texture_count": 2000}), "count above limit rejected")
	_check(not planner.configure({"atlas_size": 128}), "atlas below floor rejected")
	_check(planner.configure({"max_decoded_bytes": 268435456, "max_texture_count": 512, "atlas_size": 4096}), "valid configuration accepted")

	var empty: Dictionary = planner.analyze([])
	_check(empty["verdict"] == "FIT", "empty material set fits")
	_check(empty["unique_textures"].is_empty(), "empty material set has no textures")
	_check(empty["findings"].is_empty(), "empty material set has no findings")

	var report: Dictionary = planner.analyze(_materials())
	_check(report["schema_version"] == "texture_budget.report.v1", "report schema version")
	_check(report["verdict"] == "FIT", "fixture fits default budget")
	_check(report["materials"] == 2, "material count recorded")
	_check(report["texture_refs"] == 4, "texture references recorded")
	_check(report["unique_textures"].size() == 3, "duplicate SHA-256 collapsed")
	_check(report["duplicate_refs"] == 1, "duplicate reference counted")
	_check(report["duplicate_bytes_saved"] > 0, "duplicate savings computed")
	_check(report["decoded_bytes_dedup"] < report["decoded_bytes_total"], "dedup bytes below total bytes")
	_check(_has_finding(report, "duplicate_textures"), "duplicate texture finding")
	_check(report["atlas"]["tiles_required"] == 144, "atlas tiles estimated")
	_check(report["atlas"]["tiles_available"] == 256, "atlas tiles available")
	_check(report["limitations"].size() >= 5, "limitations documented")
	_check(JSON.stringify(report) == JSON.stringify(planner.analyze(_materials())), "analysis is deterministic")
	_check(JSON.stringify(planner.get_last_report()) == JSON.stringify(report), "last report retained")

	var one: Dictionary = planner.analyze([
		_material("single", [_texture("orm", "d".repeat(64), 1024, 1024, false, false)]),
	])
	_check(one["unique_textures"][0]["bytes"] == 4194304, "1024 texture without mips is 4 MiB")
	var mipped: Dictionary = planner.analyze([
		_material("single", [_texture("orm", "d".repeat(64), 1024, 1024, true, false)]),
	])
	_check(mipped["unique_textures"][0]["bytes"] > one["unique_textures"][0]["bytes"], "mips increase decoded bytes")

	planner.configure({"max_decoded_bytes": 41943040})
	var over: Dictionary = planner.analyze(_materials())
	_check(over["verdict"] == "OVER_BUDGET", "byte budget exceeded")
	_check(not over["downscale_plan"].is_empty(), "downscale plan generated")
	_check(over["projected_bytes_after_plan"] <= 41943040, "downscale plan reaches the budget")
	_check(over["downscale_plan"][0]["from_px"][0] == 2048, "largest texture downscaled first")
	_check(over["downscale_plan"][0]["to_px"][0] == 1024, "downscale halves the dimension")
	_check(over["recommendations"].any(func(item): return item["action"] == "downscale_largest"), "downscale recommendation present")

	planner.configure({"max_decoded_bytes": 268435456, "max_texture_count": 2})
	var count_over: Dictionary = planner.analyze(_materials())
	_check(count_over["verdict"] == "OVER_BUDGET", "texture count budget exceeded")
	_check(_has_finding(count_over, "over_texture_count"), "over count finding")
	_check(count_over["recommendations"].any(func(item): return item["action"] == "reduce_texture_count"), "count recommendation present")

	planner.configure({"max_texture_count": 512})
	var unique_bytes: int = int(report["decoded_bytes_dedup"])
	planner.configure({"max_decoded_bytes": int(float(unique_bytes) * 1.05)})
	_check(planner.analyze(_materials())["verdict"] == "TIGHT", "small headroom yields tight verdict")

	planner.configure({"max_decoded_bytes": 268435456, "atlas_size": 512})
	var pressure: Dictionary = planner.analyze(_materials())
	_check(pressure["verdict"] == "FIT", "atlas pressure does not change byte verdict")
	_check(_has_finding(pressure, "atlas_pressure"), "atlas pressure flagged")
	_check(pressure["recommendations"].any(func(item): return item["action"] == "increase_atlas_or_split"), "atlas recommendation present")

	var oversized: Dictionary = planner.analyze([
		_material("huge", [_texture("albedo", "e".repeat(64), 8192, 8192, true, true)]),
	])
	_check(_has_finding(oversized, "oversized_texture"), "oversized texture flagged")

	var non_pow2: Dictionary = planner.analyze([
		_material("odd", [_texture("albedo", "f".repeat(64), 1000, 1000, true, true)]),
	])
	_check(_has_finding(non_pow2, "non_power_of_two"), "non-power-of-two flagged")

	var bad_srgb: Dictionary = planner.analyze([
		_material("normal", [_texture("normal", "1".repeat(64), 1024, 1024, true, true)]),
	])
	_check(_has_finding(bad_srgb, "srgb_on_data_texture"), "sRGB data texture flagged")

	var no_mips: Dictionary = planner.analyze([
		_material("flat", [_texture("albedo", "2".repeat(64), 512, 512, false, true)]),
	])
	_check(_has_finding(no_mips, "missing_mips"), "missing mips flagged")

	var mismatch: Dictionary = planner.analyze([
		_material("mat-a", [_texture("albedo", "3".repeat(64), 2048, 2048, true, true)]),
		_material("mat-b", [_texture("albedo", "3".repeat(64), 1024, 1024, true, true)]),
	])
	_check(_has_finding(mismatch, "digest_dimension_mismatch"), "digest dimension mismatch flagged")
	_check(mismatch["verdict"] != "INVALID_INPUT", "mismatch report remains well-formed")

	planner.configure({"max_decoded_bytes": 268435456, "atlas_size": 4096})
	_check(planner.analyze([{"material_id": "Stone", "textures": []}])["verdict"] == "INVALID_INPUT", "uppercase id rejected by the contract pattern")
	_check(planner.analyze([{"material_id": "", "textures": []}])["verdict"] == "INVALID_INPUT", "empty material id rejected")
	_check(planner.analyze([{"material_id": "mat-x", "textures": [_texture("roughness", "4".repeat(64), 256, 256)]}])["verdict"] == "INVALID_INPUT", "invalid slot rejected")
	_check(planner.analyze([{"material_id": "mat-x", "textures": [_texture("albedo", "XYZ", 256, 256)]}])["verdict"] == "INVALID_INPUT", "invalid sha rejected")
	_check(planner.analyze([{"material_id": "mat-x", "textures": [_texture("albedo", "5".repeat(64), 0, 256)]}])["verdict"] == "INVALID_INPUT", "zero dimension rejected")
	var bad_mips := _texture("albedo", "6".repeat(64), 256, 256)
	bad_mips["mipmaps"] = "yes"
	_check(planner.analyze([{"material_id": "mat-x", "textures": [bad_mips]}])["verdict"] == "INVALID_INPUT", "non-boolean mipmaps rejected")
	_check(planner.analyze([{"material_id": "mat-x"}])["verdict"] == "INVALID_INPUT", "missing textures rejected")
	_check(planner.analyze([{"material_id": "mat-x", "textures": [_texture("albedo", "7".repeat(64), 64, 64, true, true)]}])["verdict"] == "FIT", "floor-sized texture accepted")
	_check(planner.analyze([{"material_id": "mat-x", "textures": [_texture("albedo", "7".repeat(64), 64, 64, true, true)]}])["findings"].is_empty(), "clean fixture has no findings")

	planner.clear()
	_check(planner.max_decoded_bytes == 268435456, "clear restores byte budget")
	_check(planner.atlas_size == 4096, "clear restores atlas size")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M04_TEXTUREBUDGET_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M04_TEXTUREBUDGET_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
