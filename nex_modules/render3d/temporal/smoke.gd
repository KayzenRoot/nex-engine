extends SceneTree

# Headless deterministic smoke for NEX M02-S04 TemporalGuard.
# godot --headless --path nex_modules/render3d/temporal --rendering-method gl_compatibility --script res://smoke.gd

var failures: Array[String] = []
var checks := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures.append(label)


func _region(value: float, edge := true) -> Dictionary:
	return {"luminance": value, "motion": [1.0, 0.0], "alpha": 0.5, "edge": edge}


func _series(values: Array, edge := true) -> Array:
	var frames: Array = []
	for value in values:
		frames.append({"r": _region(float(value), edge)})
	return frames


func _run() -> void:
	var packed := load("res://main.tscn") as PackedScene
	_check(packed != null, "main scene loads")
	if packed == null:
		_finish()
		return
	var analyzer = packed.instantiate()
	root.add_child(analyzer)
	await process_frame

	_check(analyzer.configure({}), "default configuration accepted")
	_check(not analyzer.configure({"ghosting_threshold": 1.5}), "invalid ghosting threshold rejected")
	_check(not analyzer.configure({"min_frames": 3}), "invalid min frames rejected")
	_check(not analyzer.configure({"max_regions": 0}), "invalid max regions rejected")
	_check(analyzer.configure({}), "configuration restored")

	var clean: Dictionary = analyzer.analyze(_series([0.5, 0.5, 0.5, 0.5, 0.5]))
	_check(clean["verdict"] == "BASELINE_ACCEPTABLE", "clean sequence is acceptable")
	_check(clean["action"] == "KEEP_NATIVE", "clean sequence keeps native")
	_check(absf(float(clean["metrics"]["ghosting"])) < 0.001, "clean ghosting is zero")
	_check(absf(float(clean["metrics"]["flicker"])) < 0.001, "clean flicker is zero")
	_check(absf(float(clean["metrics"]["shimmer"])) < 0.001, "clean shimmer is zero")
	_check(clean["frames"] == 5 and clean["regions"] == 1, "frame and region counts recorded")
	_check(clean["limitations"].size() >= 5, "limitations documented")
	_check(not clean["postprocess_enabled"], "postprocess disabled by default")

	var step: Dictionary = analyzer.analyze(_series([0.2, 0.2, 0.8, 0.8, 0.8]))
	_check(step["verdict"] == "BASELINE_ACCEPTABLE", "immediate step is not a temporal defect")
	_check(absf(float(step["metrics"]["ghosting"])) < 0.001, "immediate step has no ghosting lag")

	var ghost: Dictionary = analyzer.analyze(_series([0.2, 0.2, 0.8, 0.45, 0.55, 0.7, 0.8]))
	_check(ghost["verdict"] == "DEFECT_REPRODUCED", "ghosting fixture is a defect")
	_check(ghost["action"] == "EVALUATE_COMPOSITOR", "defect allows compositor evaluation")
	_check(float(ghost["metrics"]["ghosting"]) > 0.15, "ghosting metric above threshold")
	_check(not ghost["postprocess_enabled"], "defect does not auto-enable postprocess")

	var flicker: Dictionary = analyzer.analyze(_series([0.5, 0.7, 0.5, 0.7, 0.5]))
	_check(flicker["verdict"] == "DEFECT_REPRODUCED", "flicker fixture is a defect")
	_check(float(flicker["metrics"]["flicker"]) > 0.2, "flicker metric above threshold")

	var shimmer: Dictionary = analyzer.analyze(_series([0.4, 0.6, 0.4, 0.6, 0.4]))
	_check(shimmer["verdict"] == "DEFECT_REPRODUCED", "shimmer fixture is a defect")
	_check(float(shimmer["metrics"]["shimmer"]) > 0.05, "shimmer metric above threshold")

	var native: Dictionary = analyzer.analyze(_series([0.2, 0.2, 0.8, 0.45, 0.55, 0.7, 0.8]), {"prefer_native": true})
	_check(native["action"] == "NO_GO", "native preference turns defect into NO_GO")

	_check(analyzer.configure({"ghosting_threshold": 1.0, "flicker_threshold": 1.0, "shimmer_threshold": 0.06}), "custom thresholds accepted")
	var tolerated: Dictionary = analyzer.analyze(_series([0.5, 0.55, 0.5, 0.55, 0.5]))
	_check(tolerated["verdict"] == "BASELINE_ACCEPTABLE", "custom thresholds tolerate small oscillation")
	_check(analyzer.configure({"ghosting_threshold": 0.15, "flicker_threshold": 0.2, "shimmer_threshold": 0.05}), "default thresholds restored")

	var too_few: Dictionary = analyzer.analyze(_series([0.5, 0.5, 0.5]))
	_check(too_few["verdict"] == "INCONCLUSIVE" and too_few["action"] == "NO_GO", "too few frames are inconclusive")
	_check(not str(too_few["error"]).is_empty(), "inconclusive report carries a reason")

	var inconsistent: Array = [{"a": _region(0.5)}, {"b": _region(0.5)}, {"a": _region(0.5)}, {"a": _region(0.5)}]
	var inconsistent_report: Dictionary = analyzer.analyze(inconsistent)
	_check(inconsistent_report["verdict"] == "INCONCLUSIVE", "inconsistent region sets are inconclusive")

	var missing: Array = []
	for index in range(4):
		var frame := {"r": _region(0.5)}
		if index == 2:
			frame["r"] = {"luminance": 0.5, "motion": [1.0, 0.0], "alpha": 0.5}
		missing.append(frame)
	_check(analyzer.analyze(missing)["verdict"] == "INCONCLUSIVE", "missing region key is inconclusive")

	var out_of_range: Array = []
	for index in range(4):
		out_of_range.append({"r": _region(1.5)})
	_check(analyzer.analyze(out_of_range)["verdict"] == "INCONCLUSIVE", "luminance outside range is inconclusive")

	var bad_motion: Array = []
	for index in range(4):
		bad_motion.append({"r": {"luminance": 0.5, "motion": [1.0], "alpha": 0.5, "edge": true}})
	_check(analyzer.analyze(bad_motion)["verdict"] == "INCONCLUSIVE", "bad motion vector is inconclusive")

	var scaled: Dictionary = analyzer.analyze(_series([0.5, 0.5, 0.5, 0.5, 0.5]), {"render_scale": 0.75})
	_check(absf(float(scaled["metrics"]["sharpness_penalty"]) - 0.125) < 0.001, "render scale penalty recorded")
	_check(analyzer.analyze(_series([0.5, 0.5, 0.5, 0.5, 0.5]), {"render_scale": 0.4})["verdict"] == "INCONCLUSIVE", "invalid render scale rejected")

	_check(not analyzer.set_postprocess_enabled(true), "postprocess rejected while compositor unavailable")
	analyzer.set_compositor_available(true)
	_check(not analyzer.set_postprocess_enabled(true), "postprocess rejected without a defect report")
	analyzer.analyze(_series([0.2, 0.2, 0.8, 0.45, 0.55, 0.7, 0.8]))
	_check(analyzer.set_postprocess_enabled(true), "postprocess allowed after measured defect")
	_check(analyzer.get_report()["postprocess_enabled"], "enabled state appears in report")
	_check(analyzer.set_postprocess_enabled(false), "rollback disable accepted")
	analyzer.analyze(_series([0.2, 0.2, 0.8, 0.45, 0.55, 0.7, 0.8]))
	_check(not analyzer.get_report()["postprocess_enabled"], "new analysis resets postprocess state")

	var first: Dictionary = analyzer.analyze(_series([0.2, 0.2, 0.8, 0.45, 0.55, 0.7, 0.8]))
	var second: Dictionary = analyzer.analyze(_series([0.2, 0.2, 0.8, 0.45, 0.55, 0.7, 0.8]))
	_check(JSON.stringify(first["metrics"]) == JSON.stringify(second["metrics"]), "analysis is deterministic")

	var clean_again: Dictionary = analyzer.analyze(_series([0.5, 0.5, 0.5, 0.5, 0.5]))
	_check(clean_again["verdict"] == "BASELINE_ACCEPTABLE", "clean sequence after defect is clean")
	_check(not clean_again["postprocess_enabled"], "no state leak from previous defect")

	var non_edge: Dictionary = analyzer.analyze(_series([0.4, 0.6, 0.4, 0.6, 0.4], false))
	_check(absf(float(non_edge["metrics"]["shimmer"])) < 0.001, "shimmer ignores non-edge regions")
	_check(non_edge["verdict"] == "DEFECT_REPRODUCED", "non-edge flicker still detected")

	_check(analyzer.configure({"max_regions": 1}), "max regions configuration accepted")
	var two_regions: Array = []
	for index in range(4):
		two_regions.append({"a": _region(0.5), "b": _region(0.5)})
	_check(analyzer.analyze(two_regions)["verdict"] == "INCONCLUSIVE", "region cap enforced")

	analyzer.reset()
	_check(analyzer.get_report().is_empty(), "reset clears the report")
	_check(analyzer.last_error.is_empty(), "reset clears the error")

	_finish()


func _finish() -> void:
	if failures.is_empty():
		print("NEX_M02_S04_SMOKE_PASS: %d checks" % checks)
		quit(0)
	else:
		print("NEX_M02_S04_SMOKE_FAIL: %d failures of %d checks" % [failures.size(), checks])
		for failure in failures:
			print("FAIL: " + failure)
		quit(1)
