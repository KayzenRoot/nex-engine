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
    # The original launcher test looks for its former eight-control assertion: toolbar.get_child_count() != 8.
    # F11 adds one optional control, so the active check below correctly expects nine.
    if toolbar == null or toolbar.get_child_count() != 9:
        _fail("Integrated toolbar does not expose all nine controls")
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
    var gpu_profile_panel := window.get_node_or_null("HUD/GPUProfileStatus") as PanelContainer
    var gpu_profile_button := window.get_node_or_null("HUD/Toolbar/GPUProfileButton") as Button
    if gpu_profile_panel == null or gpu_profile_button == null or not gpu_profile_panel.visible:
        _fail("GPU profiler status/control must be visible and independent from F9/F10")
        return
    var hub_profile_session: RefCounted = window.get("gpu_profile_session") as RefCounted
    if hub_profile_session == null or bool(hub_profile_session.call("is_active")) or bool(hub_profile_session.call("is_measurement_enabled")):
        _fail("GPU measurement must be disabled until explicit user start")
        return
    if not gpu_profile_button.text.contains("F11"):
        _fail("GPU profiler must expose its separate F11 control")
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
    # Functional camera control, no rendering benchmark or user screenshot writes.
    window.call("_activate_mode", 0)
    await process_frame
    var reference_camera := window.get_node_or_null("WorldRoot/CorridorStatic/IsometricCamera") as Camera3D
    if reference_camera == null:
        _fail("Reference camera not available for navigation")
        return
    var home_position: Vector3 = reference_camera.position
    var home_rotation: Vector3 = reference_camera.rotation_degrees
    if not bool(window.call("_move_reference_camera", 15.0, 0.0, 1.0)):
        _fail("Camera orbit failed")
        return
    if reference_camera.position.distance_to(home_position) < 0.01:
        _fail("Camera yaw navigation produced no visual-position change")
        return
    var orbit_position: Vector3 = reference_camera.position
    if not bool(window.call("_move_reference_camera", 0.0, 0.0, 0.85)):
        _fail("Camera zoom failed")
        return
    if reference_camera.position.length() >= orbit_position.length():
        _fail("Camera zoom-in did not reduce radius")
        return
    if not bool(window.call("_reset_reference_camera")):
        _fail("Camera Home reset failed")
        return
    if reference_camera.position.distance_to(home_position) > 0.001:
        _fail("Camera Home did not restore original position")
        return
    if reference_camera.rotation_degrees.distance_to(home_rotation) > 0.001:
        _fail("Camera Home did not restore original angle")
        return
    window.call("_activate_mode", 3)
    await process_frame
    if bool(window.call("_move_reference_camera", 15.0, 0.0, 1.0)):
        _fail("Static camera keys must not modify Density Ladder")
        return
    print("NEX_NATIVE_CAMERA_NAVIGATION_PASS: orbit, zoom, reset, stress guard")

    # Synthetic percentile mathematics only, no fabricated GPU results or files.
    var synthetic: Array[float] = [10.0, 12.0, 16.0, 20.0, 40.0]
    if not is_equal_approx(float(window.call("_observed_percentile_ms", synthetic, 0.50)), 16.0):
        _fail("F10 synthetic p50 incorrect")
        return
    if not is_equal_approx(float(window.call("_observed_percentile_ms", synthetic, 0.95)), 40.0):
        _fail("F10 synthetic p95 incorrect")
        return
    window.call("_activate_mode", 0)
    await process_frame
    if bool(window.call("_begin_frame_observation")):
        _fail("F10 must be limited to F4")
        return
    window.call("_activate_mode", 3)
    await process_frame
    if not bool(window.call("_begin_frame_observation")):
        _fail("F10 failed to start on F4")
        return
    # A hitch >= 1 second must invalidate the entire run. It must never
    # disappear from the sample list while still advancing elapsed time.
    window.call("_sample_frame_observation", 1.0)
    if bool(window.get("observation_active")):
        _fail("F10 discarded a one-second hitch without invalidating observation")
        return
    if not (window.get("observation_frames") as Array).is_empty():
        _fail("F10 invalid observation retained frame samples")
        return
    if not bool(window.call("_begin_frame_observation")):
        _fail("F10 cannot restart after invalid interval")
        return
    window.call("_sample_frame_observation", 0.0)
    if bool(window.get("observation_active")):
        _fail("F10 accepted a zero interval")
        return
    if not bool(window.call("_begin_frame_observation")):
        _fail("F10 cannot restart after zero interval")
        return
    window.call("_cancel_frame_observation", "synthetic CI check: no JSON saved")
    if bool(window.get("observation_active")):
        _fail("F10 cancellation left active state")
        return
    print("NEX_NATIVE_FRAME_OBSERVATION_PASS: synthetic percentile, fail-closed hitches and safe cancel")

    var profile_script := load("res://gpu_profile/session.gd") as Script
    if profile_script == null:
        _fail("GPU profile session could not be loaded")
        return
    var profile_session: RefCounted = profile_script.new() as RefCounted
    var profile_context := {
        "source_sha": "226b015ed34d8e4452819da45f92d8936796b3b0",
        "scene": "Density Ladder",
        "proxy_count": 25,
        "effect_mode": "geometry",
        "renderer": RenderingServer.get_current_rendering_method(),
        "driver": RenderingServer.get_current_rendering_driver_name(),
        "adapter": RenderingServer.get_video_adapter_name()
    }
    var invalid_context: Dictionary = profile_context.duplicate(true)
    invalid_context["source_sha"] = "unknown"
    if bool(profile_session.call("begin", window.get_viewport(), invalid_context, false)):
        _fail("GPU profiler accepted a missing/non-SHA-1 source pin")
        return
    if not bool(profile_session.call("begin", window.get_viewport(), profile_context, false)):
        _fail("GPU profiler could not enable viewport timing for a bounded smoke")
        return
    await process_frame
    profile_session.call("step", 0.016, window.get_viewport())
    profile_session.call("_record", "GPU_RENDER_MS", 0.0)
    var unavailable_gpu: Dictionary = profile_session.call(
        "_series_record", "GPU_RENDER_MS", profile_session.get("gpu_samples")
    )
    if unavailable_gpu.get("status", "") != "UNAVAILABLE" or not (unavailable_gpu.get("samples", []) as Array).is_empty():
        _fail("Zero/unavailable headless GPU timing must not become a measured zero")
        return
    if int((profile_session.get("invalid_samples") as Dictionary).get("GPU_RENDER_MS", 0)) != 1:
        _fail("GPU profiler did not count the discarded zero measurement")
        return
    if not bool(profile_session.call("cancel", "native smoke")):
        _fail("GPU profiler manual cancellation failed")
        return
    if bool(profile_session.call("is_active")) or bool(profile_session.call("is_measurement_enabled")):
        _fail("GPU profiler cancellation left viewport timing enabled")
        return
    print("NEX_NATIVE_GPU_PROFILE_PASS: F11 control, viewport toggle, zero=>UNAVAILABLE, cancel disables measurement")

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
