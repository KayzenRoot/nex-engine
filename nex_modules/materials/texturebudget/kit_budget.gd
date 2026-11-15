extends SceneTree

# NEX M04 kit-budget run: feeds the committed material.v1 kit observation to
# the integrated TextureBudgetPlanner. Planning only: no texture is decoded,
# packed, imported or rendered.
# godot --headless --path nex_modules/materials/texturebudget --script res://kit_budget.gd

const PLANNER := preload("res://texture_budget_planner.gd")
const KIT_ENV := "NEX_M04_KIT_PATH"
const OUTPUT_ENV := "NEX_M04_KIT_BUDGET_OUTPUT"
const SOURCE_SHA := "873f4a7d05d3b70912a5112089e3ebfbf068703c"
const KIT_URI := "nex_modules/materials/kit/kit.v1.json"


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	print("M04_KIT_BUDGET_FAIL " + message)
	quit(2)


func _run() -> void:
	var kit_path := OS.get_environment(KIT_ENV).strip_edges()
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if kit_path.is_empty() or output.is_empty():
		_fail("missing kit or output path")
		return
	var text := FileAccess.get_file_as_string(kit_path)
	if text.is_empty():
		_fail("cannot read kit observation")
		return
	var kit = JSON.parse_string(text)
	if not kit is Dictionary or String(kit.get("schema_version", "")) != "material.v1":
		_fail("kit observation is not material.v1")
		return
	var budget: Dictionary = kit.get("texture_budget", {})
	var planner = PLANNER.new()
	root.add_child(planner)
	if not planner.configure({
		"max_decoded_bytes": int(budget.get("max_texture_bytes", 268435456)),
		"max_texture_count": int(budget.get("max_texture_count", 512)),
		"atlas_size": int(budget.get("atlas_size", 4096)),
	}):
		_fail("planner configure: " + planner.last_error)
		return
	var report: Dictionary = planner.analyze(kit.get("materials", []))
	if String(report.get("verdict", "")) == "INVALID_INPUT":
		_fail("planner rejected the kit materials")
		return
	var document := {
		"schema_version": "m04_kit_budget_run.v1",
		"source_sha": SOURCE_SHA,
		"kit_uri": KIT_URI,
		"kit_sha256": FileAccess.get_sha256(kit_path),
		"report": report,
	}
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		_fail("cannot write output")
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	print("M04_KIT_BUDGET_OK " + String(report.get("verdict", "")))
	quit(0)
