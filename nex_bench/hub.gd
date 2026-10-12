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
var diagnostics_panel: PanelContainer
var diagnostics_label: Label
var diagnostics_elapsed := 0.0

func _ready() -> void:
    DisplayServer.window_set_title("NEX Engine | Visual Lab")
    _make_toolbar()
    _make_diagnostics_panel()
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
    var diagnostics_button := Button.new()
    diagnostics_button.text = "DIAGNOSTICO [F9]"
    diagnostics_button.custom_minimum_size = Vector2(132, 40)
    diagnostics_button.pressed.connect(_toggle_diagnostics)
    toolbar.add_child(diagnostics_button)

func _make_diagnostics_panel() -> void:
    diagnostics_panel = PanelContainer.new()
    diagnostics_panel.name = "RenderDiagnostics"
    diagnostics_panel.anchor_top = 1.0
    diagnostics_panel.anchor_bottom = 1.0
    diagnostics_panel.offset_left = 16.0
    diagnostics_panel.offset_top = -247.0
    diagnostics_panel.offset_right = 440.0
    diagnostics_panel.offset_bottom = -18.0
    diagnostics_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    diagnostics_label = Label.new()
    diagnostics_label.name = "RenderStats"
    diagnostics_label.custom_minimum_size = Vector2(410.0, 218.0)
    diagnostics_label.add_theme_font_size_override("font_size", 15)
    diagnostics_panel.add_child(diagnostics_label)
    $HUD.add_child(diagnostics_panel)
    diagnostics_panel.visible = false

func _toggle_diagnostics() -> void:
    if diagnostics_panel == null:
        return
    diagnostics_panel.visible = not diagnostics_panel.visible
    if diagnostics_panel.visible:
        _refresh_diagnostics()

func _process(delta: float) -> void:
    if diagnostics_panel == null or not diagnostics_panel.visible:
        return
    diagnostics_elapsed += delta
    if diagnostics_elapsed >= 0.75:
        diagnostics_elapsed = 0.0
        _refresh_diagnostics()

func _refresh_diagnostics() -> void:
    if diagnostics_label == null:
        return
    var driver: String = RenderingServer.get_current_rendering_driver_name()
    var method_name: String = RenderingServer.get_current_rendering_method()
    var adapter: String = RenderingServer.get_video_adapter_name()
    var backend: String = DisplayServer.get_name()
    if adapter.is_empty():
        adapter = "N/A (headless / unavailable)"
    var is_headless: bool = backend == "headless"
    var fps: float = Performance.get_monitor(Performance.TIME_FPS)
    var process_ms: float = Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0
    var calls: int = int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
    var objects: int = int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME))
    var memory: float = Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)
    var memory_text: String = "N/A (headless / unavailable)" if is_headless or memory <= 0.0 else "%.1f MiB (renderer allocation)" % (memory / (1024.0 * 1024.0))
    diagnostics_label.text = (
        "NEX ENGINE  |  DIAGNOSTICO LOCAL [F9]\n"
        + "Cena: %s\n" % SCENE_LABELS[active_mode]
        + "Render method: %s / driver: %s\n" % [method_name, driver]
        + "Display: %s\n" % backend
        + "Adapter: %s\n" % adapter
        + "FPS observado: %.0f (nao e benchmark)\n" % fps
        + "CPU process: %.2f ms/frame (nao GPU time)\n" % process_ms
        + "Draw calls: %d | objetos 3D: %d\n" % [calls, objects]
        + "Memoria do renderizador: %s\n" % memory_text
        + "NAO representa VRAM total, p95 ou latencia GPU"
    )

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
        KEY_F9:
            _toggle_diagnostics()
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
    _hide_diff_preview()
    for child in world_root.get_children():
        world_root.remove_child(child)
        child.queue_free()
    world_root.add_child(next_world)
    active_world = next_world
    active_mode = index
    if diagnostics_panel != null and diagnostics_panel.visible:
        _refresh_diagnostics()
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
    var report: Dictionary = _pixel_diff(first, second)
    match str(report.get("status", "INVALID_IMAGE")):
        "SIZE_MISMATCH":
            _status("FAIL: screenshot resolution mismatch")
        "INVALID_IMAGE", "BUFFER_MISMATCH":
            _status("BLOCKED: pixel buffers incompatible")
        _:
            var heatmap: Image = _create_heatmap(first, second)
            if heatmap == null:
                _status("BLOCKED: heatmap could not be created")
                return
            _show_diff_preview(heatmap, report)
            var output_path: String = directory.path_join(stem + "_heatmap.png")
            var write_error: Error = heatmap.save_png(output_path)
            var image_note: String = "heatmap saved" if write_error == OK else "heatmap preview only (save failed)"
            _status("VISUAL TRUTH | %.3f%% changed (> %d/255) | MAE %.6f | %s | %s" % [
                float(report["changed_ratio"]) * 100.0,
                int(report["pixel_tolerance"]),
                float(report["mean_absolute_error_normalized"]),
                str(report["status"]),
                image_note
            ])

# Pure native Image comparator shared by the live UI and native runner tests.
# Keeps screenshots unchanged and does not touch user:// or invoke external programs.
func _pixel_diff(first: Image, second: Image) -> Dictionary:
    if first == null or second == null or first.is_empty() or second.is_empty():
        return {"status": "INVALID_IMAGE"}
    if first.get_size() != second.get_size():
        return {"status": "SIZE_MISMATCH"}
    var first_rgb := first.duplicate() as Image
    var second_rgb := second.duplicate() as Image
    first_rgb.convert(Image.FORMAT_RGB8)
    second_rgb.convert(Image.FORMAT_RGB8)
    var lhs: PackedByteArray = first_rgb.get_data()
    var rhs: PackedByteArray = second_rgb.get_data()
    if lhs.size() != rhs.size() or lhs.size() == 0 or lhs.size() % 3 != 0:
        return {"status": "BUFFER_MISMATCH"}
    var changed := 0
    var absolute_error := 0
    for i in range(0, lhs.size(), 3):
        var dr := absi(int(lhs[i]) - int(rhs[i]))
        var dg := absi(int(lhs[i + 1]) - int(rhs[i + 1]))
        var db := absi(int(lhs[i + 2]) - int(rhs[i + 2]))
        absolute_error += dr + dg + db
        if maxi(dr, maxi(dg, db)) > PIXEL_TOLERANCE:
            changed += 1
    var pixels := first_rgb.get_width() * first_rgb.get_height()
    return {
        "status": "PASS" if changed == 0 else "DIFF",
        "changed_pixels": changed,
        "changed_ratio": float(changed) / float(pixels),
        "mean_absolute_error_normalized": float(absolute_error) / float(pixels * 3 * 255),
        "pixel_tolerance": PIXEL_TOLERANCE
    }

# Deterministic red-difference heatmap. Never modifies the source images.
# This is an RGB pixel visualization, not GPU/perceptual validation.
func _create_heatmap(first: Image, second: Image) -> Image:
    if first == null or second == null or first.is_empty() or second.is_empty():
        return null
    if first.get_size() != second.get_size():
        return null
    var reference: Image = first.duplicate() as Image
    var candidate: Image = second.duplicate() as Image
    reference.convert(Image.FORMAT_RGB8)
    candidate.convert(Image.FORMAT_RGB8)
    var lhs: PackedByteArray = reference.get_data()
    var rhs: PackedByteArray = candidate.get_data()
    if lhs.size() != rhs.size() or lhs.size() == 0 or lhs.size() % 3 != 0:
        return null
    var pixels: int = reference.get_width() * reference.get_height()
    if lhs.size() != pixels * 3:
        return null
    var output := PackedByteArray()
    output.resize(pixels * 4)
    for pixel in range(pixels):
        var src: int = pixel * 3
        var dst: int = pixel * 4
        var dr: int = absi(int(lhs[src]) - int(rhs[src]))
        var dg: int = absi(int(lhs[src + 1]) - int(rhs[src + 1]))
        var db: int = absi(int(lhs[src + 2]) - int(rhs[src + 2]))
        if maxi(dr, maxi(dg, db)) > PIXEL_TOLERANCE:
            output[dst] = 255
            output[dst + 1] = 32
            output[dst + 2] = 48
        else:
            var grayscale: int = (int(lhs[src]) + int(lhs[src + 1]) + int(lhs[src + 2])) / 6
            output[dst] = grayscale
            output[dst + 1] = grayscale
            output[dst + 2] = grayscale
        output[dst + 3] = 255
    return Image.create_from_data(reference.get_width(), reference.get_height(), false, Image.FORMAT_RGBA8, output)

func _hide_diff_preview() -> void:
    var previous: Control = $HUD.get_node_or_null("DiffPreview") as Control
    if previous != null:
        $HUD.remove_child(previous)
        previous.queue_free()

func _show_diff_preview(heatmap: Image, report: Dictionary) -> void:
    _hide_diff_preview()
    var panel := PanelContainer.new()
    panel.name = "DiffPreview"
    panel.anchor_left = 1.0
    panel.anchor_top = 1.0
    panel.anchor_right = 1.0
    panel.anchor_bottom = 1.0
    panel.offset_left = -464.0
    panel.offset_top = -342.0
    panel.offset_right = -16.0
    panel.offset_bottom = -18.0
    panel.mouse_filter = Control.MOUSE_FILTER_STOP
    var content := VBoxContainer.new()
    panel.add_child(content)
    var title := Label.new()
    title.text = "VISUAL TRUTH  |  %d altered pixels" % int(report.get("changed_pixels", 0))
    content.add_child(title)
    var preview := TextureRect.new()
    preview.name = "HeatmapTexture"
    preview.custom_minimum_size = Vector2(420.0, 252.0)
    preview.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    preview.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
    preview.texture = ImageTexture.create_from_image(heatmap)
    content.add_child(preview)
    var close_button := Button.new()
    close_button.text = "FECHAR MAPA DE DIFERENCAS"
    close_button.pressed.connect(_hide_diff_preview)
    content.add_child(close_button)
    $HUD.add_child(panel)

func _status(message: String) -> void:
    status_label.text = message
