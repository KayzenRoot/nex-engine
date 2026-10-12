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
    if toolbar == null or toolbar.get_child_count() != 7:
        _fail("Integrated toolbar does not expose all seven controls")
        return
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
    window.queue_free()
    print("NEX_NATIVE_IMPORT_SMOKE_PASS: 4 integrated modes, headless parser only")
    quit(0)

func _fail(message: String) -> void:
    push_error("NEX_NATIVE_IMPORT_SMOKE_FAIL: " + message)
    quit(1)
