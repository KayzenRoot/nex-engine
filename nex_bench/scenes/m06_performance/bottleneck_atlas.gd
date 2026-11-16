extends RefCounted
class_name BottleneckAtlas

# NEX M06-S01 Bottleneck Atlas: classification and summary of measured
# performance observations. It does not replace the source captures.

var last_error := ""


func classify(gpu_ms: float, cpu_ms: float, pacing_ms: float) -> Dictionary:
	last_error = ""
	if not is_finite(gpu_ms) or not is_finite(cpu_ms) or not is_finite(pacing_ms):
		last_error = "timings must be finite"
		return {"classification": "insufficient_data", "evidence": "unavailable",
			"confidence": "low", "rationale": last_error}
	if gpu_ms < 0.0 or cpu_ms < 0.0 or pacing_ms < 0.0:
		last_error = "timings must be non-negative"
		return {"classification": "insufficient_data", "evidence": "unavailable",
			"confidence": "low", "rationale": last_error}
	var render_max := maxf(gpu_ms, cpu_ms)
	var headroom := pacing_ms - render_max
	var gpu_share := 0.0 if pacing_ms <= 0.0 else gpu_ms / pacing_ms * 100.0
	if pacing_ms > render_max + 1.0:
		return {"classification": "pacing", "evidence": "measured", "confidence": "high",
			"gpu_share_of_frame_pct": snappedf(gpu_share, 0.01),
			"render_headroom_ms": snappedf(headroom, 0.001),
			"rationale": "frame pacing p95 exceeds max(gpu, cpu) by more than 1 ms"}
	if gpu_ms > cpu_ms * 1.5:
		return {"classification": "gpu", "evidence": "measured", "confidence": "medium",
			"gpu_share_of_frame_pct": snappedf(gpu_share, 0.01),
			"render_headroom_ms": snappedf(headroom, 0.001),
			"rationale": "GPU p95 exceeds CPU p95 by more than 50%"}
	if cpu_ms > gpu_ms * 1.5:
		return {"classification": "cpu", "evidence": "measured", "confidence": "medium",
			"gpu_share_of_frame_pct": snappedf(gpu_share, 0.01),
			"render_headroom_ms": snappedf(headroom, 0.001),
			"rationale": "CPU p95 exceeds GPU p95 by more than 50%"}
	return {"classification": "unknown", "evidence": "measured", "confidence": "low",
		"gpu_share_of_frame_pct": snappedf(gpu_share, 0.01),
		"render_headroom_ms": snappedf(headroom, 0.001),
		"rationale": "GPU and CPU p95 are within 50% of each other"}


func summarize(observations: Array) -> Dictionary:
	var counts := {"gpu": 0, "cpu": 0, "pacing": 0, "memory": 0, "unknown": 0, "insufficient_data": 0}
	var max_gpu := 0.0
	var max_pacing := 0.0
	for observation in observations:
		var classification := String(observation.get("classification", "unknown"))
		if counts.has(classification):
			counts[classification] += 1
		max_gpu = maxf(max_gpu, float(observation.get("gpu_p95_ms", 0.0)))
		max_pacing = maxf(max_pacing, float(observation.get("pacing_p95_ms", 0.0)))
	return {"observations": observations.size(), "classifications": counts,
		"max_gpu_p95_ms": snappedf(max_gpu, 0.001), "max_pacing_p95_ms": snappedf(max_pacing, 0.001)}
