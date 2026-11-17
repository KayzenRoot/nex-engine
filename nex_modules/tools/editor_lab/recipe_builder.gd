extends RefCounted
class_name RecipeBuilder

# NEX M09 BenchmarkRecipe: deterministic one-click benchmark recipe.
# It generates a recipe document only; it does not run the benchmark.

const DRIVERS := ["vulkan", "d3d12", "opengl3"]
const ALLOWED_RUNS := [3, 5]


func _valid_sha(value: String) -> bool:
	if value.length() != 40:
		return false
	for index in range(value.length()):
		if not "0123456789abcdef".contains(value[index]):
			return false
	return true


func build(config: Dictionary) -> Dictionary:
	var errors: Array = []
	var scene := str(config.get("scene_id", ""))
	var preset := str(config.get("preset_id", ""))
	var seed := int(config.get("seed", -1))
	var driver := str(config.get("driver", ""))
	var source_sha := str(config.get("source_sha", "")).to_lower()
	var resolution: Variant = config.get("resolution", [])
	var runs := int(config.get("runs", 3))
	if scene.is_empty():
		errors.append("scene_id is required")
	if preset.is_empty():
		errors.append("preset_id is required")
	if seed < 0:
		errors.append("seed must be non-negative")
	if not DRIVERS.has(driver):
		errors.append("driver must be one of " + ", ".join(DRIVERS))
	if not _valid_sha(source_sha):
		errors.append("source_sha must be 40 lowercase hex")
	if not (resolution is Array) or resolution.size() != 2:
		errors.append("resolution must have 2 values")
	elif int(resolution[0]) < 320 or int(resolution[1]) < 180:
		errors.append("resolution must be at least 320x180")
	if not ALLOWED_RUNS.has(runs):
		errors.append("runs must be 3 or 5")
	if not errors.is_empty():
		return {"ok": false, "errors": errors}
	var recipe := {
		"schema_version": "nex_bench_recipe.v1",
		"recipe_id": "m09-%s-%s-%d" % [scene, preset, seed],
		"scene_id": scene, "preset_id": preset, "seed": seed, "driver": driver,
		"source_sha": source_sha, "resolution": [int(resolution[0]), int(resolution[1])],
		"runs": runs, "warmup_seconds": 2.0, "observation_seconds": 30.0,
		"command": "godot --path nex_bench --rendering-driver %s res://scenes/preset_ab/preset_ab.tscn" % driver,
		"provenance": {"base_sha": source_sha, "head_sha": source_sha,
			"audit": "ADMIN_SOLO_NOT_INDEPENDENT"},
		"limitations": [
			"recipe only; no benchmark is executed",
			"target FPS is not a measured claim",
		],
	}
	return {"ok": true, "recipe": recipe}


func validate(recipe: Dictionary) -> Array:
	var errors: Array = []
	if recipe.get("schema_version") != "nex_bench_recipe.v1":
		errors.append("schema_version is invalid")
	if str(recipe.get("scene_id", "")).is_empty():
		errors.append("scene_id is required")
	if not _valid_sha(str(recipe.get("source_sha", "")).to_lower()):
		errors.append("source_sha is invalid")
	if not DRIVERS.has(str(recipe.get("driver", ""))):
		errors.append("driver is invalid")
	if not ALLOWED_RUNS.has(int(recipe.get("runs", 0))):
		errors.append("runs is invalid")
	var command := str(recipe.get("command", ""))
	if not command.contains("--path nex_bench"):
		errors.append("command must target nex_bench")
	if not command.contains("--rendering-driver"):
		errors.append("command must pin a rendering driver")
	return errors
