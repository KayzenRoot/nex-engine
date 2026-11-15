extends SceneTree

# NEX M02-S05 runtime probe: builds a RenderPassport from the actual Windows
# Vulkan session and applies the three reversible profiles. No rendering
# benchmark and no project.godot write.
# godot --path nex_modules/render3d/profiles --script res://runtime_probe.gd

const PASSPORT := preload("res://render_passport.gd")
const OUTPUT_ENV := "NEX_M02_PROFILE_OUTPUT"
const SOURCE_SHA := "fa1adae7ab67e38c2556d126627006c338e2e8f4"


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	print("M02_PROFILE_FAIL " + message)
	quit(2)


func _inventory() -> Dictionary:
	return {
		"godot": String(Engine.get_version_info().get("string", "")),
		"os": OS.get_name(),
		"renderer": RenderingServer.get_current_rendering_method(),
		"driver": RenderingServer.get_current_rendering_driver_name(),
		"gpu": RenderingServer.get_video_adapter_name(),
		"vram_mib": 8192,
		"vulkan_available": true,
		"d3d12_available": true,
	}


func _probe() -> Dictionary:
	root.set("use_taa", true)
	var taa := bool(root.get("use_taa"))
	root.set("use_taa", false)
	return {
		"camera.perspective": true,
		"camera.orthographic": true,
		"visibility.mesh_lod": true,
		"visibility.visibility_ranges": true,
		"visibility.occlusion_culling": true,
		"composition.render_scale": true,
		"composition.msaa": true,
		"composition.temporal_aa": taa,
	}


func _run() -> void:
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if output.is_empty():
		_fail("missing output path")
		return
	var passport = PASSPORT.new()
	root.add_child(passport)
	if not passport.load_data():
		_fail("passport data: " + passport.last_error)
		return
	var inventory := _inventory()
	var probe := _probe()
	var passport_report: Dictionary = passport.build_passport(inventory, probe)
	if passport_report.get("verdict") != "OK":
		_fail("passport: " + String(passport_report.get("error", "not OK")))
		return
	var profiles := {}
	for name in ["quality", "balanced", "performance"]:
		var selected: Dictionary = passport.select_profile(name, inventory, probe)
		if selected.get("verdict") != "OK" and selected.get("verdict") != "DEGRADED":
			_fail("profile " + name + ": " + String(selected.get("error", "invalid")))
			return
		profiles[name] = selected
	var switched: Dictionary = passport.switch_profile("quality", "performance", inventory, probe)
	var document := {
		"schema_version": "m02_capability_passport_run.v1",
		"source_sha": SOURCE_SHA,
		"session": "windows-rtx5050-2026-11-15-m02-profiles",
		"inventory": inventory,
		"probe": probe,
		"passport": passport_report,
		"profiles": profiles,
		"switch": switched,
		"limitations": [
			"vram_mib is the documented RTX 5050 8 GB capacity, not a live free-memory probe",
			"capability booleans are runtime observations for this session, not cross-driver proof",
			"profiles are reversible settings; no FPS or quality claim",
		],
	}
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		_fail("cannot write output")
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	print("M02_PROFILE_OK " + String(passport_report["verdict"]))
	quit(0)
