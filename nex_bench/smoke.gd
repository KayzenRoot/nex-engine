extends SceneTree

# Execute with the pinned Godot 4.7.2 binary:
# godot --headless --path nex_bench --rendering-method gl_compatibility --script res://smoke.gd
# Headless parser/routing check only. Not a Forward+ GPU, FPS or screenshot benchmark.

func _initialize() -> void:
    call_deferred("_check_modules")

func _check_modules() -> void:
    for path in [
        "res://scenes/base/corridor_static.tscn",
        "res://scenes/base/arena_combat.tscn",
        "res://scenes/base/dense_city.tscn",
    ]:
        var scene := load(path) as PackedScene
        if scene == null:
            _fail("Cannot parse scene: " + path)
            return
        var node := scene.instantiate()
        if node == null:
            _fail("Cannot instantiate scene: " + path)
            return
        node.free()

    if load("res://stress/density_ladder.gd") == null:
        _fail("Density Ladder script could not be loaded")
        return
    if not FileAccess.file_exists("res://stress/config/ladder.v1.json"):
        _fail("Density Ladder config missing")
        return
    var app := load("res://main.tscn") as PackedScene
    if app == null:
        _fail("Integrated main scene could not be loaded")
        return
    var window := app.instantiate() as Node3D
    if window == null:
        _fail("Integrated main scene is not Node3D")
        return
    if not window.has_method("_activate_mode"):
        window.free()
        _fail("Integrated hub script failed to load _activate_mode")
        return
    root.add_child(window)
    await process_frame
    var toolbar := window.get_node_or_null("HUD/Toolbar")
    if toolbar == null or toolbar.get_child_count() != 8:
        _fail("Integrated toolbar does not expose all eight controls")
        return
    var diagnostics: Control = window.get_node_or_null("HUD/RenderDiagnostics") as Control
    if diagnostics == null or diagnostics.visible:
        _fail("Render diagnostics panel must exist and start hidden")
        return
    window.call("_toggle_diagnostics")
    if not diagnostics.visible:
        _fail("Render diagnostics could not be shown")
        return
    var stats := diagnostics.get_node_or_null("RenderStats") as Label
    if stats == null or not stats.text.contains("FPS observado:") or not stats.text.contains("Render method:"):
        _fail("Render diagnostics did not populate real engine monitor labels")
        return
    window.call("_toggle_diagnostics")
    if diagnostics.visible:
        _fail("Render diagnostics could not be hidden")
        return
    print("NEX_NATIVE_DIAGNOSTICS_PASS: F9 toggle, renderer API and headless-safe labels")
    for mode in range(4):
        window.call("_activate_mode", mode)
        await process_frame
        var world := window.get_node_or_null("WorldRoot")
        if world == null or world.get_child_count() != 1:
            _fail("Mode %d not activated as a single world" % mode)
            return
        var scene_root := world.get_child(0) as Node3D
        if scene_root == null or scene_root.get_node_or_null("IsometricCamera") == null:
            _fail("Mode %d missing native camera" % mode)
            return
        if mode == 3:
            var workload := scene_root.get_node_or_null("WorkloadRoot")
            if workload == null or workload.get_child_count() != 25:
                _fail("Density Ladder must initialize exactly 25 proxy instances")
                return
    # Check native Visual Truth algorithm using memory-only images, no screenshots
    # and no writes to existing user://visual_truth capture files.
    var reference := Image.create(2, 1, false, Image.FORMAT_RGB8)
    reference.fill(Color.BLACK)
    var identical := Image.create(2, 1, false, Image.FORMAT_RGB8)
    identical.fill(Color.BLACK)
    var same: Dictionary = window.call("_pixel_diff", reference, identical)
    if same.get("status", "") != "PASS" or int(same.get("changed_pixels", -1)) != 0:
        _fail("Native Visual Truth identical comparison failed")
        return
    var different := Image.create(2, 1, false, Image.FORMAT_RGB8)
    different.fill(Color.BLACK)
    different.set_pixel(1, 0, Color.RED)
    var changed: Dictionary = window.call("_pixel_diff", reference, different)
    if changed.get("status", "") != "DIFF" or int(changed.get("changed_pixels", -1)) != 1:
        _fail("Native Visual Truth changed-pixel count incorrect")
        return
    if not is_equal_approx(float(changed.get("changed_ratio", -1)), 0.5):
        _fail("Native Visual Truth changed-pixel ratio incorrect")
        return
    var wrong_size := Image.create(1, 1, false, Image.FORMAT_RGB8)
    wrong_size.fill(Color.BLACK)
    var invalid: Dictionary = window.call("_pixel_diff", reference, wrong_size)
    if invalid.get("status", "") != "SIZE_MISMATCH":
        _fail("Native Visual Truth mismatched dimensions not rejected")
        return
    var heatmap: Image = window.call("_create_heatmap", reference, different) as Image
    if heatmap == null or heatmap.get_size() != Vector2i(2, 1):
        _fail("Native Visual Truth heatmap dimensions invalid")
        return
    var highlighted: Color = heatmap.get_pixel(1, 0)
    var neutral: Color = heatmap.get_pixel(0, 0)
    if highlighted.r < 0.95 or highlighted.g > 0.2 or neutral.r > 0.5:
        _fail("Native Visual Truth heatmap difference colors incorrect")
        return
    if window.call("_create_heatmap", reference, wrong_size) != null:
        _fail("Native Visual Truth heatmap must reject mismatched dimensions")
        return
    window.call("_show_diff_preview", heatmap, changed)
    if window.get_node_or_null("HUD/DiffPreview") == null:
        _fail("Native Visual Truth heatmap preview not attached to HUD")
        return
    window.call("_hide_diff_preview")
    if window.get_node_or_null("HUD/DiffPreview") != null:
        _fail("Native Visual Truth preview close did not detach panel")
        return
    print("NEX_NATIVE_VISUAL_HEATMAP_PASS: red pixels, preview UI, close")

    print("NEX_NATIVE_VISUAL_TRUTH_PASS: identical/difference/dimensions, in-memory")

    window.queue_free()
    print("NEX_NATIVE_IMPORT_SMOKE_PASS: 4 integrated modes, headless parser only")
    quit(0)

func _fail(message: String) -> void:
    push_error("NEX_NATIVE_IMPORT_SMOKE_FAIL: " + message)
    quit(1)
