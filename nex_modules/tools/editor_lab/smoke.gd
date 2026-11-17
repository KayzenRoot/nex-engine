extends SceneTree

# NEX M09 editor-tools smoke: PerfLint, ImportGuard and BenchmarkRecipe.
# Deterministic fixtures only; no rendering, import or benchmark is executed.

const PERF_LINT := preload("res://perf_lint.gd")
const IMPORT_GUARD := preload("res://import_guard.gd")
const RECIPE_BUILDER := preload("res://recipe_builder.gd")
const OUTPUT_ENV := "NEX_M09_EDITOR_OUTPUT"
const SOURCE_SHA := "371ca4ab4a5f70debc96e84bba55aba3870fc9cf"

var checks := 0
var failures: Array[String] = []


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _initialize() -> void:
	call_deferred("_run")


func _load(path: String) -> Dictionary:
	var text := FileAccess.get_file_as_string(path)
	if text.is_empty():
		return {}
	var value: Variant = JSON.parse_string(text)
	return value if value is Dictionary else {}


func _run() -> void:
	var assets_doc := _load("res://fixtures/assets.v1.json")
	var scenes_doc := _load("res://fixtures/scenes.v1.json")
	var files_doc := _load("res://fixtures/files.v1.json")
	var recipe_doc := _load("res://fixtures/recipe.v1.json")
	var lint = PERF_LINT.new()
	var guard = IMPORT_GUARD.new()
	var builder = RECIPE_BUILDER.new()

	_check(lint.configure({}), "lint configure")
	_check(not lint.configure({"max_texture_px": 1}), "lint reject small texture budget")
	_check(not lint.configure({"max_lights": -1}), "lint reject negative lights")
	var bundle: Dictionary = lint.lint_bundle(assets_doc.get("assets", []), scenes_doc.get("scenes", []))
	var summary: Dictionary = bundle["summary"]
	_check(int(summary["total"]) == 13, "lint total findings")
	_check(int(summary["counts"]["error"]) == 4, "lint error count")
	_check(int(summary["counts"]["warn"]) == 9, "lint warn count")
	_check(summary["highest"] == "error", "lint highest severity")
	for code in ["texture_too_large", "oversized_file", "sync_load_risk", "missing_license",
			"unknown_format", "duplicate_id", "invalid_dimensions", "light_budget_exceeded",
			"draw_call_budget_exceeded", "alpha_overdraw_risk", "shadow_budget_exceeded",
			"missing_scene_id"]:
		_check(int(summary["codes"].get(code, 0)) >= 1, "lint code " + code)
	_check(lint.lint_asset({"id": "clean", "path": "res://clean.png", "bytes": 128,
		"width": 128, "height": 128, "format": "png", "license": "original"}).is_empty(), "lint clean asset")
	_check(lint.lint_scene({"id": "clean", "lights": 1, "draw_calls": 1,
		"alpha_layers": 1, "shadowed_lights": 0, "sync_loads": 0}).is_empty(), "lint clean scene")
	var again: Dictionary = lint.lint_bundle(assets_doc.get("assets", []), scenes_doc.get("scenes", []))
	_check(JSON.stringify(bundle) == JSON.stringify(again), "lint deterministic")

	_check(guard.configure({}), "guard configure")
	_check(not guard.configure({"allowed_extensions": []}), "guard reject empty extensions")
	_check(not guard.configure({"max_file_bytes": 0}), "guard reject zero bytes")
	var plan: Dictionary = guard.plan(files_doc.get("files", []), files_doc.get("existing", {}))
	_check(int(plan["counts"]["accepted"]) == 1, "guard accepted")
	_check(int(plan["counts"]["rejected"]) == 3, "guard rejected")
	_check(int(plan["counts"]["noop"]) == 2, "guard noop")
	_check(int(plan["counts"]["conflicts"]) == 1, "guard conflict")
	var applied: Dictionary = guard.apply(plan, {})
	_check(int(applied["counts"]["applied"]) == 1, "guard apply")
	_check(int(applied["counts"]["blocked"]) == 0, "guard apply blocked")
	var blocked: Dictionary = guard.apply(plan, {"res://imported/data.json": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"})
	_check(int(blocked["counts"]["blocked"]) == 1, "guard apply conflict")
	var snapshot := guard.snapshot(plan)
	_check(snapshot.length() == 64, "guard snapshot length")
	_check(snapshot == guard.snapshot(plan), "guard snapshot deterministic")
	_check(JSON.stringify(plan) == JSON.stringify(guard.plan(files_doc.get("files", []), files_doc.get("existing", {}))), "guard plan deterministic")

	var built: Dictionary = builder.build(recipe_doc.get("config", {}))
	_check(bool(built.get("ok", false)), "recipe build")
	var recipe: Dictionary = built.get("recipe", {})
	_check(recipe.get("schema_version") == "nex_bench_recipe.v1", "recipe schema")
	_check(String(recipe.get("command", "")).contains("--path nex_bench"), "recipe command")
	_check(builder.validate(recipe).is_empty(), "recipe validate")
	var invalid: Dictionary = builder.build(recipe_doc.get("invalid", {}))
	_check(not bool(invalid.get("ok", true)), "recipe reject invalid")
	_check(invalid.get("errors", []).size() >= 5, "recipe invalid errors")
	var broken: Dictionary = recipe.duplicate(true)
	broken["schema_version"] = "wrong"
	broken["source_sha"] = "xyz"
	_check(builder.validate(broken).size() >= 2, "recipe validate broken")

	var document := {
		"schema_version": "m09_editor_smoke.v1",
		"source_sha": SOURCE_SHA,
		"checks": checks,
		"failures": failures,
		"verdict": "PASS" if failures.is_empty() else "FAIL",
		"lint": bundle,
		"import_plan": plan,
		"import_snapshot": snapshot,
		"recipe": recipe,
		"limitations": [
			"deterministic fixtures only; no asset is imported or rendered",
			"no FPS, frame-time or quality claim",
			"audit remains ADMIN_SOLO / NOT_INDEPENDENT",
		],
	}
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if output.is_empty():
		output = ProjectSettings.globalize_path("user://m09_editor_smoke.json")
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		print("M09_EDITOR_SMOKE_FAIL cannot write")
		quit(2)
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	if failures.is_empty():
		print("M09_EDITOR_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("M09_EDITOR_SMOKE_FAIL: " + ", ".join(failures))
		quit(2)
