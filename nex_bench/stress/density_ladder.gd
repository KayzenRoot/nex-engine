extends Node3D

# Standalone bounded Godot stress demo. FPS readout is *observational* only,
# NOT a validated hardware benchmark, GPU time, frametime p99, or VRAM measurement.
const SETTINGS_NAME := "config/ladder.v1.json"
const DEFAULT_COUNTS := [25, 50, 100, 200]
const MODE_NAMES := ["geometry", "lights", "vfx", "combined"]

@onready var workload_root: Node3D = $WorkloadRoot
@onready var status_label: Label = $HUD/Status

var counts: Array = DEFAULT_COUNTS.duplicate()
var max_proxies := 200
var max_lights := 6
var max_particle_emitters := 4
var min_safe_fps := 12
var safety_seconds := 5.0
var count_index := 0
var current_mode := 0
var safe_fps_timer := 0.0
var display_timer := 0.0
var scene_camera: Camera3D
var proxy_mesh: CapsuleMesh
var proxy_material: StandardMaterial3D
var glow_mesh: SphereMesh
var glow_material: StandardMaterial3D

func _ready() -> void:
    if not _load_settings():
        status_label.text = "NEX DENSITY LADDER | INVALID CONFIG: FAIL CLOSED"
        set_process(false)
        return
    _make_materials()
    _create_base()
    _build_workload()
    _show_status()

func _load_settings() -> bool:
    var settings_path: String = (get_script() as Script).resource_path.get_base_dir().path_join(SETTINGS_NAME)
    if not FileAccess.file_exists(settings_path):
        push_error("NEX stress config missing")
        return false
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(settings_path))
    if not (parsed is Dictionary):
        return false
    if parsed.get("schema_version", "") != "nex_density_ladder.v1":
        return false
    if parsed.get("renderer", "") != "forward_plus":
        return false
    var levels: Variant = parsed.get("counts", [])
    if not (levels is Array) or levels != DEFAULT_COUNTS:
        return false
    var cap: Variant = parsed.get("max_proxies", 0)
    var light_cap: Variant = parsed.get("max_lights", 0)
    var particle_cap: Variant = parsed.get("max_particle_emitters", 0)
    var threshold: Variant = parsed.get("minimum_safe_fps_observed", 0)
    var safety: Variant = parsed.get("safety_consecutive_seconds", 0)
    if not (cap is int and light_cap is int and particle_cap is int and threshold is int):
        return false
    if not (safety is int or safety is float):
        return false
    if cap != 200 or light_cap < 0 or light_cap > 6 or particle_cap < 0 or particle_cap > 4:
        return false
    if threshold < 5 or threshold > 30 or safety < 2 or safety > 20:
        return false
    max_proxies = cap
    max_lights = light_cap
    max_particle_emitters = particle_cap
    min_safe_fps = threshold
    safety_seconds = float(safety)
    counts = levels.duplicate()
    return true

func _make_materials() -> void:
    proxy_mesh = CapsuleMesh.new()
    proxy_mesh.radius = 0.34
    proxy_mesh.height = 1.5
    proxy_material = StandardMaterial3D.new()
    proxy_material.albedo_color = Color(0.35, 0.65, 0.85)
    proxy_material.roughness = 0.78
    glow_mesh = SphereMesh.new()
    glow_mesh.radius = 0.18
    glow_mesh.height = 0.36
    glow_material = StandardMaterial3D.new()
    glow_material.albedo_color = Color(0.13, 0.54, 1.0)
    glow_material.emission_enabled = true
    glow_material.emission = Color(0.16, 0.65, 1.0)
    glow_material.emission_energy_multiplier = 2.0

func _create_base() -> void:
    var floor := MeshInstance3D.new()
    floor.name = "Floor"
    var floor_box := BoxMesh.new()
    floor_box.size = Vector3(48.0, 0.4, 48.0)
    floor.mesh = floor_box
    floor.position = Vector3(0.0, -0.24, 0.0)
    var floor_mat := StandardMaterial3D.new()
    floor_mat.albedo_color = Color(0.14, 0.17, 0.22)
    floor.material_override = floor_mat
    add_child(floor)

    var sun := DirectionalLight3D.new()
    sun.name = "Sun"
    sun.rotation_degrees = Vector3(-56.0, 35.0, 0.0)
    sun.light_energy = 0.85
    add_child(sun)

    scene_camera = Camera3D.new()
    scene_camera.name = "IsometricCamera"
    scene_camera.position = Vector3(38.0, 38.0, 38.0)
    scene_camera.fov = 60.0
    scene_camera.near = 0.1
    scene_camera.far = 300.0
    add_child(scene_camera)
    scene_camera.look_at(Vector3.ZERO, Vector3.UP)
    scene_camera.current = true

func _unhandled_key_input(event: InputEvent) -> void:
    if not (event is InputEventKey):
        return
    var key_event := event as InputEventKey
    if not key_event.pressed or key_event.echo:
        return
    match key_event.keycode:
        KEY_1, KEY_2, KEY_3, KEY_4:
            count_index = int(key_event.keycode - KEY_1)
        KEY_G:
            current_mode = 0
        KEY_L:
            current_mode = 1
        KEY_V:
            current_mode = 2
        KEY_C:
            current_mode = 3
        _:
            return
    safe_fps_timer = 0.0
    _build_workload()
    _show_status()
    get_viewport().set_input_as_handled()

func _build_workload() -> void:
    for child in workload_root.get_children():
        workload_root.remove_child(child)
        child.queue_free()
    var count := mini(int(counts[count_index]), max_proxies)
    var side := ceili(sqrt(float(count)))
    var spacing := 1.8
    for i in range(count):
        var item := MeshInstance3D.new()
        item.name = "Proxy_%03d" % i
        item.mesh = proxy_mesh
        item.material_override = proxy_material
        var col := i % side
        var row := i / side
        item.position = Vector3(
            (float(col) - float(side - 1) * 0.5) * spacing,
            0.75,
            (float(row) - float(side - 1) * 0.5) * spacing
        )
        workload_root.add_child(item)

    if current_mode in [1, 3]:
        for i in range(max_lights):
            var lamp := OmniLight3D.new()
            lamp.name = "StressLight_%d" % i
            var angle := TAU * float(i) / float(maxi(max_lights, 1))
            lamp.position = Vector3(cos(angle) * 9.0, 4.0, sin(angle) * 9.0)
            lamp.light_color = Color(0.45, 0.68, 1.0)
            lamp.light_energy = 1.4
            lamp.omni_range = 9.0
            workload_root.add_child(lamp)
    if current_mode in [2, 3]:
        for i in range(max_particle_emitters):
            var particles := GPUParticles3D.new()
            particles.name = "VFX_%d" % i
            particles.amount = 12
            particles.lifetime = 1.0
            particles.position = Vector3(float(i - 2) * 4.0, 1.3, 0.0)
            var material := ParticleProcessMaterial.new()
            material.direction = Vector3.UP
            material.initial_velocity_min = 0.8
            material.initial_velocity_max = 1.8
            material.gravity = Vector3(0.0, -1.0, 0.0)
            particles.process_material = material
            particles.draw_pass_1 = glow_mesh
            workload_root.add_child(particles)
            particles.emitting = true

func _process(delta: float) -> void:
    display_timer += delta
    if display_timer >= 0.5:
        _show_status()
        display_timer = 0.0
    # Prevent a persistent overload from trapping a live session.
    # Startup and foreground throttling may trigger this observational fallback.
    if count_index > 0 and Engine.get_frames_per_second() > 0 and Engine.get_frames_per_second() < min_safe_fps:
        safe_fps_timer += delta
        if safe_fps_timer >= safety_seconds:
            count_index = 0
            current_mode = 0
            _build_workload()
            safe_fps_timer = 0.0
            push_warning("NEX stress safe fallback: load reduced to 25 geometry proxies")
    else:
        safe_fps_timer = 0.0

func _show_status() -> void:
    var count := int(counts[count_index])
    status_label.text = (
        "NEX DENSITY LADDER | %d proxies | %s\n" % [count, MODE_NAMES[current_mode]]
        + "[1]25  [2]50  [3]100  [4]200   [G] geometry  [L] lights  [V] vfx  [C] combined\n"
        + "Observed FPS: %d (not benchmark) | bounded load, safe fallback < %d FPS for %.0f s" % [
            Engine.get_frames_per_second(), min_safe_fps, safety_seconds
        ]
    )
