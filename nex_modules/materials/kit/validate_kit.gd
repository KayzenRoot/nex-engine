extends SceneTree

# Headless load validation for the NEX M04 procedural material kit.
# godot --headless --path nex_modules/materials/kit --import
# godot --headless --path nex_modules/materials/kit --script res://validate_kit.gd
# Loading only: no rendering, shader compilation or scene integration.

const MATERIALS := ["concrete_floor", "brushed_metal", "oak_wood", "emissive_trim"]

var failures: Array[String] = []
var checks := 0


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	for material_id in MATERIALS:
		var material = load("res://materials/%s.tres" % material_id)
		_check(material != null, material_id + " loads")
		if material == null:
			continue
		_check(material is StandardMaterial3D, material_id + " is StandardMaterial3D")
		_check(material.albedo_texture != null, material_id + " albedo texture")
		_check(material.normal_texture != null, material_id + " normal texture")
		_check(material.orm_texture != null, material_id + " orm texture")
		if material.albedo_texture != null:
			_check(material.albedo_texture.get_width() == 128, material_id + " albedo width")
			_check(material.albedo_texture.get_height() == 128, material_id + " albedo height")
		print("KIT_MATERIAL_OK " + material_id)
	if failures.is_empty():
		print("KIT_LOAD_OK %d checks" % checks)
		quit(0)
	else:
		for failure in failures:
			print("KIT_LOAD_FAIL " + failure)
		quit(2)
