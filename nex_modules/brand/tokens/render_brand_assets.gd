extends SceneTree

# NEX M12 brand rasterizer: renders the original SVG mark to deterministic
# PNG app-icon sizes and the brand sheet. No engine/editor files are touched.

const SIZES := [16, 24, 32, 48, 64, 128, 256, 512, 1024]
const OUTPUT_ENV := "NEX_BRAND_OUTPUT"


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var base := ProjectSettings.globalize_path("res://")
	var root := base + "../../.."
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if output.is_empty():
		output = root + "/assets/brand/app-icons"
	DirAccess.make_dir_recursive_absolute(output)
	var svg := FileAccess.get_file_as_string(root + "/assets/brand/logo-mark.svg")
	if svg.is_empty():
		print("NEX_BRAND_RENDER_FAIL svg missing")
		quit(2)
		return
	for size in SIZES:
		var image := Image.new()
		var load_error: int = image.load_svg_from_string(svg, float(size) / 128.0)
		if load_error != OK or image.get_width() == 0:
			print("NEX_BRAND_RENDER_FAIL size %d" % size)
			quit(2)
			return
		var path := output + "/nex-engine-%d.png" % size
		var error: int = image.save_png(path)
		if error != OK:
			print("NEX_BRAND_RENDER_FAIL save %d: %s" % [size, str(error)])
			quit(2)
			return
	print("NEX_BRAND_RENDER_PASS sizes=%d" % SIZES.size())
	quit(0)
