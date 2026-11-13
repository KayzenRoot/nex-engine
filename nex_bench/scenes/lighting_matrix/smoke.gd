extends SceneTree

# Headless parse/routing smoke for the S05 lighting matrix.
# godot --headless --path nex_bench --rendering-method gl_compatibility --script res://scenes/lighting_matrix/smoke.gd

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var packed := load("res://scenes/lighting_matrix/lighting_matrix.tscn") as PackedScene
	if packed == null:
		print("NEX_S05_SMOKE_FAIL scene_parse")
		quit(1)
		return
	var node := packed.instantiate()
	if node == null:
		print("NEX_S05_SMOKE_FAIL instantiate")
		quit(1)
		return
	root.add_child(node)
	await process_frame
	if not node.has_method("_apply_preset") or not node.has_method("_toggle_profile"):
		print("NEX_S05_SMOKE_FAIL missing_methods")
		quit(1)
		return
	var presets: Variant = node.get("presets")
	if not (presets is Array) or presets.size() != 5:
		print("NEX_S05_SMOKE_FAIL presets")
		quit(1)
		return
	print("NEX_S05_SMOKE_PASS: scene, 5 presets and profiler hooks loaded")
	quit(0)
