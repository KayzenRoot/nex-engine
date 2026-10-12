extends Node3D

# One native Godot entry point for existing S01, S03 and S04 implementations.
# S03's Python CLI remains the reference for offline PNG reports.
const SCENE_PATHS := [
    "res://scenes/base/corridor_static.tscn",
    "res://scenes/base/arena_combat.tscn",
    "res://scenes/base/dense_city.tscn",
]
const SCENE_LABELS := ["CORRIDOR", "ARENA", "DENSE CITY", "DENSITY LADDER"]
const DENSITY_SCRIPT := "res://stress/density_ladder.gd"
const CAPTURE_ROOT := "user://visual_truth"
const PIXEL_TOLERANCE := 2

@onready var world_root: Node3D = $WorldRoot
@onready var title_label: Label = $HUD/Title
@onready var status_label: Label = $HUD/Status

var active_mode := 0
var active_world: Node3D
var capture_pending := false

func _ready() -> void:
    DisplayServer.window_set_title("NEX Engine | Visual Lab")
    _make_toolbar()
    _activate_mode(0)

func _make_toolbar() -> void:
    var toolbar := HBoxContainer.new()
    toolbar.name = "Toolbar"
    toolbar.position = Vector2(20, 48)
    toolbar.add_theme_constant_override("separation", 8)
    $HUD.add_child(toolbar)
    for i in range(SCENE_LABELS.size()):
        var button := Button.new()
        button.name = "Mode_%d" % i
        button.text = "%s  [F%d]" % [SCENE_LABELS[i], i + 1]
        button.custom_minimum_size = Vector2(148, 40)
        button.pressed.connect(_activate_mode.bind(i))
        toolbar.add_child(button)
    for action in ["BASELINE [B]", "CANDIDATE [N]", "COMPARE [D]"]:
        var button := Button.new()
        button.text = action
        button.custom_minimum_size = Vector2(132, 40)
        toolbar.add_child(button)
        if action.begins_with("BASELINE"):
            button.pressed.connect(_capture.bind("baseline"))
        elif action.begins_with("CANDIDATE"):
            button.pressed.connect(_capture.bind("candidate"))
        else:
            button.pressed.connect(_compare_captures)

func _unhandled_key_input(event: InputEvent) -> void:
    if not (event is InputEventKey):
        return
    var key_event := event as InputEventKey
    if not key_event.pressed or key_event.echo:
        return
    match key_event.keycode:
        KEY_F1:
            _activate_mode(0)
        KEY_F2:
            _activate_mode(1)
        KEY_F3:
            _activate_mode(2)
        KEY_F4:
            _activate_mode(3)
        KEY_B:
            _capture("baseline")
        KEY_N:
            _capture("candidate")
        KEY_D:
            _compare_captures()
        _:
            return
    get_viewport().set_input_as_handled()

func _activate_mode(index: int) -> void:
    if index < 0 or index >= SCENE_LABELS.size():
        return
    var next_world: Node3D
    if index < SCENE_PATHS.size():
        var packed := load(SCENE_PATHS[index]) as PackedScene
        if packed == null:
            _status("BLOCKED: missing reference scene")
            return
        next_world = packed.instantiate() as Node3D
    else:
        next_world = _make_density_root()
    if next_world == null:
        _status("BLOCKED: unable to create native module")
        return
    for child in world_root.get_children():
        world_root.remove_child(child)
        child.queue_free()
    world_root.add_child(next_world)
    active_world = next_world
    active_mode = index
    title_label.text = "NEX ENGINE  /  " + SCENE_LABELS[index]
    if index == 3:
        _status("Density controls: [1-4] 25/50/100/200 proxies   [G/L/V/C] modes   |  FPS not a benchmark")
    else:
        _status("Reference scene | B baseline, N candidate, D compare | Native Forward+ requested, not measured")

func _make_density_root() -> Node3D:
    var script := load(DENSITY_SCRIPT) as Script
    if script == null:
        return null
    var root := Node3D.new()
    root.name = "DensityLadder"
    root.set_script(script)
    var workload := Node3D.new()
    workload.name = "WorkloadRoot"
    root.add_child(workload)
    var hud := CanvasLayer.new()
    hud.name = "HUD"
    root.add_child(hud)
    var label := Label.new()
    label.name = "Status"
    label.position = Vector2(20, 166)
    label.add_theme_font_size_override("font_size", 16)
    hud.add_child(label)
    return root

func _capture(kind: String) -> void:
    if active_mode == 3:
        _status("Choose a static scene for repeatable screenshots, not live Density Ladder effects")
        return
    if capture_pending:
        return
    capture_pending = true
    $HUD.visible = false
    await RenderingServer.frame_post_draw
    var image := get_viewport().get_texture().get_image()
    $HUD.visible = true
    capture_pending = false
    if image == null or image.is_empty():
        _status("BLOCKED: screenshot unavailable")
        return
    var directory := ProjectSettings.globalize_path(CAPTURE_ROOT)
    var err := DirAccess.make_dir_recursive_absolute(directory)
    if err != OK:
        _status("BLOCKED: cannot create screenshot directory")
        return
    var filename := "%s_%s.png" % [SCENE_PATHS[active_mode].get_file().get_basename(), kind]
    err = image.save_png(directory.path_join(filename))
    if err != OK:
        _status("BLOCKED: screenshot save failed")
        return
    _status("%s SAVED: %s | run D for pixel comparison" % [kind.to_upper(), directory.path_join(filename)])

func _compare_captures() -> void:
    if active_mode == 3:
        _status("Pixel reference comparison is limited to static scenes")
        return
    var directory := ProjectSettings.globalize_path(CAPTURE_ROOT)
    var stem: String = SCENE_PATHS[active_mode].get_file().get_basename()
    var baseline := directory.path_join(stem + "_baseline.png")
    var candidate := directory.path_join(stem + "_candidate.png")
    if not FileAccess.file_exists(baseline) or not FileAccess.file_exists(candidate):
        _status("Capture both B baseline and N candidate first")
        return
    var first := Image.load_from_file(baseline)
    var second := Image.load_from_file(candidate)
    if first == null or second == null or first.is_empty() or second.is_empty():
        _status("BLOCKED: PNG could not be decoded")
        return
    if first.get_size() != second.get_size():
        _status("FAIL: screenshot resolution mismatch")
        return
    first.convert(Image.FORMAT_RGB8)
    second.convert(Image.FORMAT_RGB8)
    var lhs: PackedByteArray = first.get_data()
    var rhs: PackedByteArray = second.get_data()
    if lhs.size() != rhs.size() or lhs.size() == 0:
        _status("BLOCKED: pixel buffers incompatible")
        return
    var changed := 0
    var absolute_error := 0
    for i in range(0, lhs.size(), 3):
        var dr := absi(int(lhs[i]) - int(rhs[i]))
        var dg := absi(int(lhs[i + 1]) - int(rhs[i + 1]))
        var db := absi(int(lhs[i + 2]) - int(rhs[i + 2]))
        absolute_error += dr + dg + db
        if maxi(dr, maxi(dg, db)) > PIXEL_TOLERANCE:
            changed += 1
    var pixels := first.get_width() * first.get_height()
    var ratio := float(changed) / float(pixels)
    var mae := float(absolute_error) / float(pixels * 3 * 255)
    _status("VISUAL TRUTH | %.3f%% pixels changed (> %d/255) | MAE %.6f | %s" % [
        ratio * 100.0, PIXEL_TOLERANCE, mae, "PASS" if changed == 0 else "DIFF"
    ])

func _status(message: String) -> void:
    status_label.text = message
