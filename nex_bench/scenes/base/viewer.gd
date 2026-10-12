extends Node3D

# Native Godot reference scene selector. No paid assets or engine modifications.
const SCENE_NAMES = ["CORRIDOR STATIC", "ARENA COMBAT", "DENSE CITY"]
const SCENE_PATHS = [
    "res://corridor_static.tscn",
    "res://arena_combat.tscn",
    "res://dense_city.tscn",
]

var current_scene: Node3D
@onready var status_label: Label = $HUD/Status

func _ready() -> void:
    _activate(0)

func _unhandled_key_input(event: InputEvent) -> void:
    if not (event is InputEventKey) or not event.pressed or event.echo:
        return
    match event.keycode:
        KEY_1:
            _activate(0)
        KEY_2:
            _activate(1)
        KEY_3:
            _activate(2)
        _:
            return
    get_viewport().set_input_as_handled()

func _activate(index: int) -> void:
    if index < 0 or index >= SCENE_PATHS.size():
        return
    var source := load(SCENE_PATHS[index]) as PackedScene
    if source == null:
        push_error("Missing NEX reference scene: " + SCENE_PATHS[index])
        return
    var instance := source.instantiate() as Node3D
    if instance == null:
        push_error("Invalid 3D reference scene: " + SCENE_PATHS[index])
        return
    if is_instance_valid(current_scene):
        current_scene.queue_free()
    add_child(instance)
    current_scene = instance
    status_label.text = "NEX ENGINE | VISUAL LAB\n" + SCENE_NAMES[index] + " | [1] Corridor  [2] Arena  [3] City\nForward+ reference | Native baseline, NOT a measured FPS result"
