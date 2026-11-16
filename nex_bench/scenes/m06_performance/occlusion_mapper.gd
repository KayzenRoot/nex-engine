extends RefCounted
class_name OcclusionMapper

# NEX M06-S04 Occlusion Mapper: CPU frustum/AABB classifier for diagnostics.
# It does not replace Godot's renderer culling and does not claim occlusion.

var planes: Array[Plane] = []
var last_error := ""


func set_frustum(frustum: Array) -> bool:
	last_error = ""
	planes.clear()
	for plane in frustum:
		if not plane is Plane:
			last_error = "frustum entries must be Plane"
			return false
		planes.append(plane)
	if planes.is_empty():
		last_error = "frustum is empty"
		return false
	return true


func is_visible(box: AABB) -> bool:
	if planes.is_empty():
		return true
	for plane in planes:
		var positive := box.position
		if plane.normal.x >= 0.0:
			positive.x = box.end.x
		if plane.normal.y >= 0.0:
			positive.y = box.end.y
		if plane.normal.z >= 0.0:
			positive.z = box.end.z
		if plane.distance_to(positive) < 0.0:
			return false
	return true


func is_visible_with_camera(camera: Camera3D, box: AABB) -> bool:
	if camera == null:
		return false
	if box.has_point(camera.global_position):
		return true
	for index in range(8):
		var corner := box.position
		if index & 1:
			corner.x = box.end.x
		if index & 2:
			corner.y = box.end.y
		if index & 4:
			corner.z = box.end.z
		if camera.is_position_in_frustum(corner):
			return true
	return false


func map(boxes: Array) -> Dictionary:
	var visible: Array[int] = []
	var culled: Array[int] = []
	for index in range(boxes.size()):
		if not boxes[index] is AABB:
			last_error = "boxes must contain AABB"
			return {"ok": false, "reason": last_error}
		if is_visible(boxes[index]):
			visible.append(index)
		else:
			culled.append(index)
	return {"ok": true, "visible": visible, "culled": culled,
		"visible_count": visible.size(), "culled_count": culled.size()}
