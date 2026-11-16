extends SceneTree

# NEX M06 module smoke: deterministic checks for the performance planners.
# No renderer optimization is claimed; this validates the bounded APIs.

const BATCH_WEAVE := preload("res://scenes/m06_performance/batch_weave.gd")
const LOD_GOVERNOR := preload("res://scenes/m06_performance/lod_governor.gd")
const OCCLUSION_MAPPER := preload("res://scenes/m06_performance/occlusion_mapper.gd")
const FRAME_PACER := preload("res://scenes/m06_performance/frame_pacer.gd")
const VRAM_SENTINEL := preload("res://scenes/m06_performance/vram_sentinel.gd")
const FILL_RATE := preload("res://scenes/m06_performance/fill_rate_xray.gd")
const BOTTLENECK := preload("res://scenes/m06_performance/bottleneck_atlas.gd")
const OUTPUT_ENV := "NEX_M06_MODULE_OUTPUT"

var checks := 0
var failures: Array[String] = []


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	_check_batch_weave()
	_check_lod()
	_check_occlusion()
	_check_frame_pacer()
	_check_vram()
	_check_fill_rate()
	_check_bottleneck()
	var output := OS.get_environment(OUTPUT_ENV).strip_edges()
	if output.is_empty():
		output = ProjectSettings.globalize_path("user://m06_modules_smoke.json")
	var document := {
		"schema_version": "m06_modules_smoke.v1",
		"source_sha": "c763319d04d0bf353c15db8378872bdf8fab1734",
		"checks": checks,
		"failures": failures,
		"verdict": "PASS" if failures.is_empty() else "FAIL",
		"limitations": [
			"planner checks only; no frame-time gain is claimed",
			"native captures are separate evidence",
			"audit remains ADMIN_SOLO / NOT_INDEPENDENT",
		],
	}
	var file := FileAccess.open(output, FileAccess.WRITE)
	if file == null:
		print("M06_MODULE_SMOKE_FAIL cannot write")
		quit(2)
		return
	file.store_string(JSON.stringify(document, "  ") + "\n")
	file.close()
	if failures.is_empty():
		print("M06_MODULE_SMOKE_PASS %d checks" % checks)
		quit(0)
	else:
		print("M06_MODULE_SMOKE_FAIL " + ", ".join(failures))
		quit(2)


func _check_batch_weave() -> void:
	var planner = BATCH_WEAVE.new()
	_check(planner.configure({"target_groups": 4}), "batch configure")
	_check(not planner.configure({"target_groups": 0}), "batch reject zero groups")
	_check(not planner.configure({"target_groups": 999}), "batch reject excess groups")
	planner.configure({"target_groups": 4})
	var items: Array = []
	for index in range(100):
		items.append({"id": "item_%03d" % index, "position": [float(index % 10) * 2.0, 0.6, float(index / 10) * 2.0]})
	var plan: Dictionary = planner.plan(items)
	_check(bool(plan.get("ok", false)), "batch plan ok")
	_check(int(plan.get("item_count", 0)) == 100, "batch keeps 100 items")
	var groups: Array = plan.get("groups", [])
	_check(groups.size() <= 4 and groups.size() >= 1, "batch group budget")
	var total := 0
	for group in groups:
		total += int(group["count"])
	_check(total == 100, "batch groups sum to 100")
	var again: Dictionary = planner.plan(items)
	_check(JSON.stringify(plan) == JSON.stringify(again), "batch plan deterministic")
	_check(not bool(planner.plan([{"id": "bad"}]).get("ok", true)), "batch rejects missing position")
	var transforms: Array[Transform3D] = []
	for index in range(3):
		transforms.append(Transform3D(Basis.IDENTITY, Vector3(index, 0.0, 0.0)))
	var mesh := BoxMesh.new()
	var material := StandardMaterial3D.new()
	var node := BATCH_WEAVE.build_multimesh(transforms, mesh, material)
	_check(node != null and node.multimesh.instance_count == 3, "batch multimesh instances")
	_check(node != null and is_equal_approx(node.multimesh.get_instance_transform(1).origin.x, 1.0), "batch multimesh transform")
	_check(node != null and node.material_override == material, "batch multimesh material")
	_check(BATCH_WEAVE.build_multimesh([], mesh, material) == null, "batch empty multimesh rejected")


func _check_lod() -> void:
	var governor = LOD_GOVERNOR.new()
	_check(governor.configure({"near_m": 18.0, "far_m": 35.0, "hysteresis_m": 3.0}), "lod configure")
	_check(not governor.configure({"near_m": 40.0, "far_m": 20.0}), "lod reject inverted range")
	_check(governor.select(10.0, 0) == 0, "lod keeps near high")
	_check(governor.select(50.0, 0) == 1, "lod far switches low")
	_check(governor.select(50.0, 1) == 1, "lod far stays low")
	_check(governor.select(10.0, 1) == 0, "lod near switches high")
	_check(governor.select(20.0, 1) == 1, "lod hysteresis keeps low")
	_check(governor.select(34.0, 0) == 0, "lod hysteresis keeps high")
	var result: Dictionary = governor.classify([[0, 0, 0], [100, 0, 0]], [0, 0, 0])
	_check(bool(result.get("ok", false)) and int(result["high"]) == 1 and int(result["low"]) == 1, "lod classify")
	_check(not bool(governor.classify([[0, 0]], [0, 0, 0]).get("ok", true)), "lod rejects malformed position")


func _check_occlusion() -> void:
	var mapper = OCCLUSION_MAPPER.new()
	var planes: Array[Plane] = [
		Plane(Vector3(1, 0, 0), 0.0),
		Plane(Vector3(-1, 0, 0), -10.0),
		Plane(Vector3(0, 1, 0), 0.0),
		Plane(Vector3(0, -1, 0), -10.0),
		Plane(Vector3(0, 0, 1), 0.0),
		Plane(Vector3(0, 0, -1), -10.0),
	]
	_check(mapper.set_frustum(planes), "occlusion frustum accepted")
	_check(mapper.is_visible(AABB(Vector3(1, 1, 1), Vector3(1, 1, 1))), "occlusion visible box")
	_check(not mapper.is_visible(AABB(Vector3(-2, 1, 1), Vector3(1, 1, 1))), "occlusion left culled")
	_check(not mapper.is_visible(AABB(Vector3(20, 1, 1), Vector3(1, 1, 1))), "occlusion right culled")
	_check(mapper.is_visible(AABB(Vector3(9, 1, 1), Vector3(2, 1, 1))), "occlusion partial visible")
	_check(not mapper.is_visible(AABB(Vector3(1, -2, 1), Vector3(1, 1, 1))), "occlusion bottom culled")
	_check(not mapper.is_visible(AABB(Vector3(1, 1, 20), Vector3(1, 1, 1))), "occlusion far culled")
	var mapped: Dictionary = mapper.map([AABB(Vector3(1, 1, 1), Vector3(1, 1, 1)), AABB(Vector3(-2, 1, 1), Vector3(1, 1, 1))])
	_check(bool(mapped.get("ok", false)) and int(mapped["visible_count"]) == 1 and int(mapped["culled_count"]) == 1, "occlusion map counts")
	_check(not mapper.set_frustum([]), "occlusion empty frustum rejected")
	_check(not bool(mapper.map([Vector3.ZERO]).get("ok", true)), "occlusion rejects non-AABB")


func _check_frame_pacer() -> void:
	var pacer = FRAME_PACER.new()
	_check(pacer.configure({"min_scale": 0.6, "max_scale": 1.0, "target_ms": 16.67, "step": 0.05, "cooldown_frames": 30, "hysteresis_ms": 1.5}), "pacer configure")
	_check(not pacer.configure({"min_scale": 0.9, "max_scale": 0.5}), "pacer reject inverted scale")
	_check(not pacer.configure({"target_ms": 0.0}), "pacer reject zero target")
	var first: Dictionary = pacer.update(20.0, 100)
	_check(String(first["action"]) == "down" and is_equal_approx(float(first["scale"]), 0.95), "pacer down")
	var hold: Dictionary = pacer.update(20.0, 101)
	_check(String(hold["action"]) == "hold" and String(hold["reason"]) == "cooldown", "pacer cooldown")
	var down_again: Dictionary = pacer.update(20.0, 130)
	_check(String(down_again["action"]) == "down" and is_equal_approx(float(down_again["scale"]), 0.9), "pacer down again")
	var up: Dictionary = pacer.update(10.0, 160)
	_check(String(up["action"]) == "up" and is_equal_approx(float(up["scale"]), 0.95), "pacer up")
	_check(String(pacer.update(16.67, 190)["action"]) == "hold", "pacer in band")
	for index in range(20):
		pacer.update(30.0, 220 + index * 30)
	_check(pacer.get_state()["scale"] >= 0.6, "pacer min clamp")
	_check(not bool(pacer.update(-1.0, 1000).get("ok", true)), "pacer rejects negative frame")
	_check(not pacer.apply(null), "pacer rejects null viewport")
	pacer.reset()
	_check(is_equal_approx(float(pacer.get_state()["scale"]), 1.0), "pacer reset")


func _check_vram() -> void:
	var sentinel = VRAM_SENTINEL.new()
	_check(sentinel.configure({"budget_bytes": 6000000000, "warn_ratio": 0.8, "critical_ratio": 0.92, "hysteresis_ratio": 0.03}), "vram configure")
	_check(not sentinel.configure({"budget_bytes": 0}), "vram reject zero budget")
	_check(not sentinel.configure({"warn_ratio": 0.95, "critical_ratio": 0.9}), "vram reject inverted ratios")
	_check(String(sentinel.evaluate({"status": "MEASURED", "video_bytes": 1000000000})["state"]) == "OK", "vram ok")
	_check(String(sentinel.evaluate({"status": "MEASURED", "video_bytes": 5000000000})["state"]) == "WARN", "vram warn")
	_check(String(sentinel.evaluate({"status": "MEASURED", "video_bytes": 5600000000})["state"]) == "CRITICAL", "vram critical")
	_check(String(sentinel.evaluate({"status": "MEASURED", "video_bytes": 5500000000})["state"]) == "CRITICAL", "vram critical hysteresis")
	_check(String(sentinel.evaluate({"status": "MEASURED", "video_bytes": 5000000000})["state"]) == "WARN", "vram critical recovery")
	_check(String(sentinel.evaluate({"status": "MEASURED", "video_bytes": 4500000000})["state"]) == "OK", "vram warn recovery")
	_check(String(sentinel.evaluate({"status": "UNAVAILABLE"})["state"]) == "UNKNOWN", "vram unavailable")
	var sample: Dictionary = sentinel.sample()
	_check(String(sample["status"]) in ["MEASURED", "UNAVAILABLE"], "vram sample status")
	_check(sample.has("provider"), "vram sample provider")
	sentinel.reset()
	_check(String(sentinel.get_state()["state"]) == "OK", "vram reset")


func _check_fill_rate() -> void:
	var xray = FILL_RATE.new()
	var low: Dictionary = xray.estimate({"count": 100, "width": 1920, "height": 1080, "sprite_px": 64.0, "layers": 1})
	_check(bool(low.get("ok", false)) and String(low["band"]) == "low", "fillrate low")
	var medium: Dictionary = xray.estimate({"count": 1000, "width": 1920, "height": 1080, "sprite_px": 64.0, "layers": 1})
	_check(String(medium["band"]) == "medium", "fillrate medium")
	var high: Dictionary = xray.estimate({"count": 3000, "width": 1920, "height": 1080, "sprite_px": 64.0, "layers": 1})
	_check(String(high["band"]) == "high", "fillrate high")
	var smaller: Dictionary = xray.estimate({"count": 1000, "width": 1280, "height": 720, "sprite_px": 64.0, "layers": 1})
	_check(float(smaller["overdraw_proxy"]) > float(medium["overdraw_proxy"]), "fillrate resolution scaling")
	_check(not bool(xray.estimate({"count": -1, "width": 1920, "height": 1080, "sprite_px": 64.0}).get("ok", true)), "fillrate reject negative count")
	_check(not bool(xray.estimate({"count": 1, "width": 0, "height": 1080, "sprite_px": 64.0}).get("ok", true)), "fillrate reject viewport")
	_check(not bool(xray.estimate({"count": 1, "width": 1920, "height": 1080, "sprite_px": 0.0}).get("ok", true)), "fillrate reject sprite")
	_check(not bool(xray.estimate({"count": 1, "width": 1920, "height": 1080, "sprite_px": 64.0, "layers": 0}).get("ok", true)), "fillrate reject layers")
	var matrix: Dictionary = xray.plan_matrix([1, 10, 100], [[1280, 720], [1920, 1080], [2560, 1440]], 64.0, 1)
	_check(bool(matrix.get("ok", false)) and int(matrix["count"]) == 9, "fillrate matrix 9 cells")
	_check(float(matrix["cells"][0]["overdraw_proxy"]) < float(matrix["cells"][8]["overdraw_proxy"]), "fillrate matrix order")


func _check_bottleneck() -> void:
	var atlas = BOTTLENECK.new()
	_check(String(atlas.classify(2.0, 1.0, 16.0)["classification"]) == "pacing", "bottleneck pacing")
	_check(String(atlas.classify(5.0, 1.0, 6.0)["classification"]) == "gpu", "bottleneck gpu")
	_check(String(atlas.classify(1.0, 5.0, 6.0)["classification"]) == "cpu", "bottleneck cpu")
	_check(String(atlas.classify(2.0, 2.0, 2.5)["classification"]) == "unknown", "bottleneck unknown")
	_check(String(atlas.classify(-1.0, 1.0, 1.0)["classification"]) == "insufficient_data", "bottleneck negative")
	_check(String(atlas.classify(INF, 1.0, 1.0)["classification"]) == "insufficient_data", "bottleneck non-finite")
	var summary: Dictionary = atlas.summarize([
		{"classification": "pacing", "gpu_p95_ms": 2.0, "pacing_p95_ms": 16.0},
		{"classification": "gpu", "gpu_p95_ms": 5.0, "pacing_p95_ms": 6.0},
		{"classification": "gpu", "gpu_p95_ms": 4.0, "pacing_p95_ms": 5.0},
	])
	_check(int(summary["observations"]) == 3, "bottleneck summary count")
	_check(int(summary["classifications"]["gpu"]) == 2, "bottleneck summary gpu")
	_check(float(summary["max_gpu_p95_ms"]) == 5.0, "bottleneck summary max")
	_check(String(atlas.classify(2.0, 1.0, 16.0)["evidence"]) == "measured", "bottleneck evidence")
