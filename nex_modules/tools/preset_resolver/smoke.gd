extends SceneTree

# Headless deterministic smoke for NEX M09-RESOLVER PresetResolver.
# godot --headless --path nex_modules/tools/preset_resolver --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _preset(preset_id: String, tier: String, resolution: float, shadow: String, atlas: int, fps: int,
		reduced := false, shake := 1.0, hit_stop := 1.0) -> Dictionary:
	return {
		"preset_id": preset_id,
		"label": preset_id,
		"tier": tier,
		"settings": {
			"rendering": {
				"renderer_id": "godot.forward_plus", "driver_id": "vulkan",
				"resolution_scale": resolution, "msaa": "4x", "shadow_quality": shadow,
			},
			"lighting": {
				"tonemap": "filmic", "glow": true,
				"shadow_atlas_size": atlas, "max_shadowed_lights": 8,
			},
			"performance": {"target_fps": fps, "max_draw_calls": 8000, "lod_bias": 0.5},
			"feedback": {"hit_stop_scale": hit_stop, "shake_scale": shake, "reduced_motion": reduced},
		},
	}


func _pack() -> Dictionary:
	return {
		"schema_version": "preset_pack.v1",
		"observation_id": "m09-smoke-001",
		"captured_at_utc": "2026-11-13T12:00:00Z",
		"pack_id": "nex-quality-pack",
		"presets": [
			_preset("quality-low", "low", 0.5, "low", 1024, 60),
			_preset("quality-medium", "medium", 0.75, "medium", 2048, 60),
			_preset("quality-high", "high", 1.0, "high", 4096, 120),
			_preset("quality-ultra", "ultra", 1.0, "ultra", 8192, 120),
			_preset("accessibility-reduced-motion", "custom", 1.0, "high", 4096, 60, true, 0.25, 0.5),
		],
		"compatibility": {
			"contract_versions": ["render_core.v1", "lighting.v1", "performance.v1", "composition.v1", "feedback.v1"],
			"godot_version_range": "4.7.x",
			"hardware_tier": "desktop",
		},
	}


func _ids(entries: Array) -> Array:
	var ids: Array = []
	for entry in entries:
		ids.append(entry["preset_id"])
	return ids


func _run() -> void:
	var packed := load("res://main.tscn") as PackedScene
	_check(packed != null, "main scene loads")
	if packed == null:
		_finish()
		return
	var resolver = packed.instantiate()
	root.add_child(resolver)
	await process_frame

	_check(resolver.configure({}), "default configuration accepted")
	_check(not resolver.configure({"hardware_tier": "server"}), "invalid hardware tier rejected")
	_check(not resolver.configure({"godot_version": ""}), "empty Godot version rejected")
	_check(not resolver.configure({"available_contracts": "render_core.v1"}), "non-array contracts rejected")
	_check(resolver.configure({"hardware_tier": "desktop", "godot_version": "4.7.2-stable", "required_contracts": ["render_core.v1", "lighting.v1", "performance.v1"]}), "valid configuration accepted")

	_check(resolver.load_pack(_pack()), "valid pack loaded")
	_check(_ids(resolver.list_presets()) == ["quality-low", "quality-medium", "quality-high", "quality-ultra", "accessibility-reduced-motion"], "presets listed by tier")

	var low: Dictionary = resolver.resolve_tier("low")
	_check(low["status"] == "RESOLVED", "low tier resolved")
	_check(low["tier"] == "low", "low tier recorded")
	_check(low["settings"]["rendering"]["resolution_scale"] == 0.5, "low resolution")
	_check(low["settings"]["lighting"]["shadow_atlas_size"] == 1024, "low atlas")
	_check(low["overrides_applied"].is_empty(), "low has no overrides")
	_check(low["limitations"].size() >= 5, "limitations documented")

	var high: Dictionary = resolver.resolve_tier("high")
	_check(high["status"] == "RESOLVED", "high tier resolved")
	_check(high["settings"]["performance"]["target_fps"] == 120, "high target fps")
	_check(high["settings"]["rendering"]["shadow_quality"] == "high", "high shadow quality")

	var custom: Dictionary = resolver.resolve_preset("accessibility-reduced-motion")
	_check(custom["status"] == "RESOLVED", "custom preset resolved")
	_check(custom["warnings"].has("reduced motion is enabled"), "reduced motion warning")
	_check(custom["settings"]["feedback"]["shake_scale"] == 0.25, "custom shake scale")

	var by_id: Dictionary = resolver.resolve_preset("quality-medium")
	_check(by_id["preset_id"] == "quality-medium", "resolve by preset id")
	_check(by_id["tier"] == "medium", "resolve by preset id tier")

	_check(resolver.resolve_tier("potato")["status"] == "INVALID", "unknown tier rejected")
	_check(resolver.resolve_preset("missing")["status"] == "INVALID", "unknown preset rejected")

	var overridden: Dictionary = resolver.resolve_tier("low", {"rendering": {"resolution_scale": 0.6}})
	_check(overridden["status"] == "RESOLVED", "override resolved")
	_check(overridden["settings"]["rendering"]["resolution_scale"] == 0.6, "override applied")
	_check(overridden["settings"]["rendering"]["msaa"] == "4x", "override keeps sibling keys")
	_check(overridden["settings"]["lighting"]["shadow_atlas_size"] == 1024, "override keeps other blocks")
	_check(overridden["overrides_applied"] == ["rendering.resolution_scale"], "override path recorded")

	_check(resolver.resolve_tier("low", {"unknown": {}})["status"] == "INVALID", "unknown override block rejected")
	_check(resolver.resolve_tier("low", {"rendering": {"resolution_scale": 3.0}})["status"] == "INVALID", "invalid override value rejected")

	_check(resolver.resolve_tier("low", {"feedback": {"reduced_motion": true}})["status"] == "INVALID", "reduced motion without scaling rejected")
	var reduced: Dictionary = resolver.resolve_tier("low", {"feedback": {"reduced_motion": true, "shake_scale": 0.25, "hit_stop_scale": 0.5}})
	_check(reduced["status"] == "RESOLVED", "reduced motion with scaling resolved")
	_check(reduced["settings"]["feedback"]["shake_scale"] == 0.25, "reduced motion override applied")

	resolver.configure({"hardware_tier": "integrated"})
	_check(resolver.resolve_tier("high")["status"] == "INCOMPATIBLE", "hardware tier incompatibility")
	resolver.configure({"hardware_tier": "desktop", "required_contracts": ["material.v1"]})
	_check(resolver.resolve_tier("low")["status"] == "INCOMPATIBLE", "contract incompatibility")
	resolver.configure({"required_contracts": ["render_core.v1"], "godot_version": "4.6.0-stable"})
	_check(resolver.resolve_tier("low")["status"] == "INCOMPATIBLE", "Godot range incompatibility")
	resolver.configure({"godot_version": "4.7.2-stable", "required_contracts": ["render_core.v1", "lighting.v1", "performance.v1"]})

	var bad_schema := _pack()
	bad_schema["schema_version"] = "preset_pack.v2"
	_check(not resolver.load_pack(bad_schema), "wrong pack schema rejected")

	var duplicate := _pack()
	duplicate["presets"][1]["preset_id"] = "quality-low"
	_check(not resolver.load_pack(duplicate), "duplicate preset id rejected")

	var duplicate_tier := _pack()
	duplicate_tier["presets"][1]["tier"] = "low"
	_check(not resolver.load_pack(duplicate_tier), "duplicate standard tier rejected")

	var empty_settings := _pack()
	empty_settings["presets"][0]["settings"] = {}
	_check(not resolver.load_pack(empty_settings), "empty settings rejected")

	var invalid_settings := _pack()
	invalid_settings["presets"][0]["settings"]["rendering"]["resolution_scale"] = 0.1
	_check(not resolver.load_pack(invalid_settings), "invalid settings rejected")

	var non_monotonic := _pack()
	non_monotonic["presets"][1]["settings"]["rendering"]["resolution_scale"] = 0.4
	_check(not resolver.load_pack(non_monotonic), "non-monotonic tier rejected")

	var duplicate_version := _pack()
	duplicate_version["compatibility"]["contract_versions"] = ["lighting.v1", "lighting.v1"]
	_check(not resolver.load_pack(duplicate_version), "duplicate contract version rejected")

	var bad_hardware := _pack()
	bad_hardware["compatibility"]["hardware_tier"] = "server"
	_check(not resolver.load_pack(bad_hardware), "invalid pack hardware rejected")

	_check(resolver.load_pack(_pack()), "pack reloaded")
	var first: Dictionary = resolver.resolve_tier("high")
	var second: Dictionary = resolver.resolve_tier("high")
	_check(JSON.stringify(first) == JSON.stringify(second), "resolution is deterministic")
	_check(JSON.stringify(resolver.get_last_resolution()) == JSON.stringify(second), "last resolution retained")

	resolver.clear()
	_check(resolver.resolve_tier("low")["status"] == "INVALID", "cleared resolver is invalid")
	_check(resolver.hardware_tier == "desktop" and resolver.godot_version == "4.7.2-stable", "clear restores defaults")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M09_RESOLVER_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M09_RESOLVER_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
