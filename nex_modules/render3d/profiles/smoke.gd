extends SceneTree

# Headless deterministic smoke for NEX M02-S05 RenderPassport.
# godot --headless --path nex_modules/render3d/profiles --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _inventory(overrides := {}) -> Dictionary:
	var base := {
		"godot": "4.7.2-stable", "os": "Windows", "renderer": "forward_plus",
		"driver": "vulkan", "gpu": "NVIDIA GeForce RTX 5050", "vram_mib": 8192,
	}
	for key in overrides.keys():
		base[key] = overrides[key]
	return base


func _capability(report: Dictionary, id: String) -> Dictionary:
	for capability in report.get("capabilities", []):
		if capability["id"] == id:
			return capability
	return {}


func _run() -> void:
	var packed := load("res://main.tscn") as PackedScene
	_check(packed != null, "main scene loads")
	if packed == null:
		_finish()
		return
	var passport = packed.instantiate()
	root.add_child(passport)
	await process_frame
	_check(passport.load_data(), "matrix and profiles load")
	_check(passport.matrix["schema_version"] == "nex_m02_capability_matrix.v1", "matrix schema")
	_check(passport.profiles_doc["schema_version"] == "nex_m02_profiles.v1", "profiles schema")
	_check(passport.matrix["capabilities"].size() == 9, "nine capabilities")
	_check(passport.list_profiles().size() == 3, "three profiles")
	_check(passport.profiles_doc["defaults"] == "quality", "quality is default")
	_check(not passport.list_profiles().has("ultra"), "no ultra profile")
	_check(passport.profiles_doc["status"] == "PROVISIONAL_NO_FPS_CLAIM", "profiles are provisional without FPS claim")

	var inventory := _inventory()
	var report: Dictionary = passport.build_passport(inventory)
	_check(report["verdict"] == "OK", "valid inventory yields a passport")
	_check(report["probe_status"] == "INCONCLUSIVE_NOT_PROBED", "no probe is inconclusive")
	_check(report["effective"]["renderer"] == "forward_plus", "effective renderer recorded")
	_check(report["effective"]["driver"] == "vulkan", "effective driver recorded")
	_check(report["effective"]["degraded"] == false, "primary path is not degraded")
	_check(report["flags"]["project_godot_writes"] == false, "no project.godot writes")
	_check(report["flags"]["personal_hardware_collected"] == false, "no personal hardware collection")
	_check(report["flags"]["gpu_name_implies_capability"] == false, "GPU name does not imply capability")
	_check(report["limitations"].size() >= 5, "limitations documented")
	_check(_capability(report, "visibility.mesh_lod")["state"] == "SUPPORTED", "mesh LOD documented")
	_check(_capability(report, "composition.temporal_aa")["state"] == "REQUIRES_MEASUREMENT", "TAA requires measurement")
	_check(_capability(report, "composition.temporal_aa")["verification"] == "DOCUMENTED_UNVERIFIED", "documented state is unverified")

	var probed: Dictionary = passport.build_passport(inventory, {"visibility.mesh_lod": true})
	_check(probed["probe_status"] == "RUNTIME_PROBED", "probe reported")
	_check(_capability(probed, "visibility.mesh_lod")["state"] == "MEASURED_ENABLED", "probe enables capability")
	_check(_capability(probed, "visibility.mesh_lod")["verification"] == "RUNTIME_PROBED", "probe verification")
	var probed_off: Dictionary = passport.build_passport(inventory, {"visibility.mesh_lod": false})
	_check(_capability(probed_off, "visibility.mesh_lod")["state"] == "MEASURED_DISABLED", "probe disables capability")
	var unknown_probe: Dictionary = passport.build_passport(inventory, {"unknown.capability": true})
	_check(unknown_probe["probe_status"] == "INCONCLUSIVE_NOT_PROBED", "unknown probe id ignored")
	_check(_capability(probed, "visibility.mesh_lod")["state"] != _capability(probed_off, "visibility.mesh_lod")["state"], "same GPU, probe changes state")

	for bad in [
		_inventory({"renderer": "metal"}), _inventory({"driver": "metal"}),
		_inventory({"os": "Linux"}), _inventory({"godot": "4.6"}), _inventory({"vram_mib": 0}),
		_inventory({"gpu": ""}), _inventory({"vulkan_available": "yes"}),
	]:
		_check(passport.build_passport(bad)["verdict"] == "INCONCLUSIVE", "invalid inventory blocked")

	var compatibility: Dictionary = passport.build_passport(_inventory({"renderer": "gl_compatibility", "driver": "opengl3"}))
	_check(compatibility["effective"]["degraded"], "compatibility tier is degraded")
	_check(_capability(compatibility, "visibility.mesh_lod")["state"] == "UNSUPPORTED", "mesh LOD unsupported in compatibility")
	var compatibility_profile: Dictionary = passport.select_profile("quality", _inventory({"renderer": "gl_compatibility", "driver": "opengl3"}))
	_check(compatibility_profile["verdict"] == "DEGRADED", "profile on compatibility is degraded")
	_check(compatibility_profile["degraded_features"].has("mesh_lod"), "degraded feature listed")
	_check(compatibility_profile["settings"]["mesh_lod"] == false, "unsupported feature disabled")
	_check(compatibility_profile["settings"]["renderer"] == "gl_compatibility", "effective renderer applied")
	_check(compatibility_profile["writes_project_godot"] == false, "profile selection does not write project.godot")

	var fallback_d3d12: Dictionary = passport.build_passport(_inventory({"vulkan_available": false}))
	_check(fallback_d3d12["effective"]["driver"] == "d3d12", "vulkan fallback selects d3d12")
	_check(fallback_d3d12["effective"]["fallback_chain"].has("forward_plus+d3d12"), "fallback chain recorded")
	_check(not fallback_d3d12["effective"]["degraded"], "d3d12 fallback stays forward_plus")
	var fallback_gl: Dictionary = passport.build_passport(_inventory({"vulkan_available": false, "d3d12_available": false}))
	_check(fallback_gl["effective"]["renderer"] == "gl_compatibility", "full fallback selects compatibility")
	_check(fallback_gl["effective"]["degraded"], "full fallback is degraded")
	_check(fallback_gl["effective"]["fallback_chain"].size() == 2, "full fallback chain length")

	var quality: Dictionary = passport.select_profile("quality", inventory)
	_check(quality["settings"]["render_scale"] == 1.0, "quality render scale")
	_check(quality["settings"]["msaa"] == "4x", "quality MSAA")
	_check(quality["settings"]["max_fps"] == 0, "quality max fps")
	_check(quality["settings"]["vsync"] == 1, "quality vsync")
	_check(quality["reversible"], "profile selection is reversible")
	var balanced: Dictionary = passport.select_profile("balanced", inventory)
	_check(absf(float(balanced["settings"]["render_scale"]) - 0.85) < 0.001, "balanced render scale")
	_check(balanced["settings"]["msaa"] == "2x", "balanced MSAA")
	_check(balanced["settings"]["max_fps"] == 60, "balanced max fps")
	var performance: Dictionary = passport.select_profile("performance", inventory)
	_check(absf(float(performance["settings"]["render_scale"]) - 0.75) < 0.001, "performance render scale")
	_check(performance["settings"]["msaa"] == "disabled", "performance MSAA disabled")
	_check(passport.select_profile("ultra", inventory)["verdict"] == "INCONCLUSIVE", "unknown profile rejected")

	var switch_report: Dictionary = passport.switch_profile("quality", "performance", inventory)
	_check(switch_report["verdict"] == "OK", "profile switch accepted")
	_check(switch_report["round_trip"], "profile switch round-trips")
	_check(not switch_report["diff"].is_empty(), "profile switch reports a diff")
	_check(switch_report["diff"].has("render_scale"), "diff includes render scale")
	var reverse: Dictionary = passport.switch_profile("performance", "quality", inventory)
	_check(reverse["round_trip"], "reverse switch round-trips")
	var same: Dictionary = passport.switch_profile("quality", "quality", inventory)
	_check(same["diff"].is_empty(), "same-profile switch has empty diff")
	_check(passport.switch_profile("quality", "ultra", inventory)["verdict"] == "INCONCLUSIVE", "unknown switch target rejected")

	var first: Dictionary = passport.build_passport(inventory, {"visibility.mesh_lod": true})
	var second: Dictionary = passport.build_passport(inventory, {"visibility.mesh_lod": true})
	_check(JSON.stringify(first) == JSON.stringify(second), "passport is deterministic")

	var bad_profiles: Dictionary = passport.profiles_doc.duplicate(true)
	bad_profiles["profiles"]["quality"]["render_scale"] = 0.4
	_check(not passport.configure({"profiles": bad_profiles}), "invalid render scale rejected")
	bad_profiles = passport.profiles_doc.duplicate(true)
	bad_profiles["profiles"]["quality"]["msaa"] = "16x"
	_check(not passport.configure({"profiles": bad_profiles}), "invalid MSAA rejected")
	bad_profiles = passport.profiles_doc.duplicate(true)
	bad_profiles["profiles"]["quality"]["vsync"] = 3
	_check(not passport.configure({"profiles": bad_profiles}), "invalid vsync rejected")
	bad_profiles = passport.profiles_doc.duplicate(true)
	bad_profiles["profiles"]["quality"]["max_fps"] = 300
	_check(not passport.configure({"profiles": bad_profiles}), "invalid max fps rejected")
	bad_profiles = passport.profiles_doc.duplicate(true)
	bad_profiles["profiles"]["quality"]["camera_distance_m"] = 0.0
	_check(not passport.configure({"profiles": bad_profiles}), "invalid camera distance rejected")
	bad_profiles = passport.profiles_doc.duplicate(true)
	bad_profiles["profiles"]["quality"].erase("pixel_snap")
	_check(not passport.configure({"profiles": bad_profiles}), "missing profile field rejected")
	bad_profiles = passport.profiles_doc.duplicate(true)
	bad_profiles["profiles"]["ultra"] = bad_profiles["profiles"]["quality"].duplicate(true)
	_check(not passport.configure({"profiles": bad_profiles}), "extra ultra profile rejected")
	bad_profiles = passport.profiles_doc.duplicate(true)
	bad_profiles["profiles"]["quality"]["driver"] = "opengl3"
	_check(not passport.configure({"profiles": bad_profiles}), "driver incompatible with renderer rejected")
	bad_profiles = passport.profiles_doc.duplicate(true)
	bad_profiles["profiles"].erase("balanced")
	_check(not passport.configure({"profiles": bad_profiles}), "missing balanced profile rejected")

	var bad_matrix: Dictionary = passport.matrix.duplicate(true)
	bad_matrix["capabilities"][0].erase("states")
	_check(not passport.configure({"matrix": bad_matrix}), "malformed matrix rejected")
	_check(passport.build_passport(inventory)["verdict"] == "OK", "valid state survives failed configuration")

	for capability in passport.matrix["capabilities"]:
		_check(str(capability["source"]).begins_with("https://docs.godotengine.org/"), "capability has an official source")
	_check(passport.matrix["fallbacks"].has("forward_plus+vulkan"), "fallback map documented")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M02_S05_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M02_S05_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
