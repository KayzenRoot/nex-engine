extends RefCounted
class_name LODGovernor

# NEX M06-S03 LOD Governor: distance-based detail selection with hysteresis.
# This is a bounded planner, not a replacement for Godot's native mesh LOD.

const HIGH := 0
const LOW := 1

var near_m := 18.0
var far_m := 35.0
var hysteresis_m := 3.0
var last_error := ""


func configure(config := {}) -> bool:
	last_error = ""
	var next_near := float(config.get("near_m", near_m))
	var next_far := float(config.get("far_m", far_m))
	var next_hysteresis := float(config.get("hysteresis_m", hysteresis_m))
	if not is_finite(next_near) or not is_finite(next_far) or not is_finite(next_hysteresis):
		last_error = "distances must be finite"
		return false
	if next_near < 0.0 or next_far <= next_near or next_hysteresis < 0.0:
		last_error = "require 0 <= near < far and hysteresis >= 0"
		return false
	near_m = next_near
	far_m = next_far
	hysteresis_m = next_hysteresis
	return true


func select(distance_m: float, current_level: int) -> int:
	if current_level != HIGH and current_level != LOW:
		current_level = HIGH
	if current_level == HIGH and distance_m > far_m + hysteresis_m:
		return LOW
	if current_level == LOW and distance_m < near_m - hysteresis_m:
		return HIGH
	return current_level


func classify(positions: Array, camera_position: Array) -> Dictionary:
	if camera_position.size() != 3:
		last_error = "camera_position must have 3 values"
		return {"ok": false, "reason": last_error}
	var camera := Vector3(float(camera_position[0]), float(camera_position[1]), float(camera_position[2]))
	var high := 0
	var low := 0
	for position in positions:
		if position.size() != 3:
			last_error = "position must have 3 values"
			return {"ok": false, "reason": last_error}
		var point := Vector3(float(position[0]), float(position[1]), float(position[2]))
		if select(point.distance_to(camera), HIGH) == HIGH:
			high += 1
		else:
			low += 1
	return {"ok": true, "high": high, "low": low, "total": high + low}
