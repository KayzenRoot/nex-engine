extends RefCounted
class_name BatchWeave

# NEX M06-S02 BatchWeave: deterministic spatial grouping for MultiMesh
# instancing. It plans groups only; rendering stays with Godot's MultiMesh.

const MAX_GROUPS := 64
const MAX_ITEMS := 100000

var target_groups := 4
var last_error := ""


func configure(config := {}) -> bool:
	last_error = ""
	var requested := int(config.get("target_groups", target_groups))
	if requested < 1 or requested > MAX_GROUPS:
		last_error = "target_groups outside [1,%d]" % MAX_GROUPS
		return false
	target_groups = requested
	return true


func plan(items: Array) -> Dictionary:
	last_error = ""
	if items.is_empty():
		return {"ok": true, "groups": [], "item_count": 0, "target_groups": target_groups}
	if items.size() > MAX_ITEMS:
		last_error = "item budget exceeded"
		return {"ok": false, "reason": last_error}
	var min_x := INF
	var max_x := -INF
	var min_z := INF
	var max_z := -INF
	for item in items:
		if not item is Dictionary or not item.has("position"):
			last_error = "item must be an object with position"
			return {"ok": false, "reason": last_error}
		var position: Array = item["position"]
		if position.size() != 3:
			last_error = "position must have 3 values"
			return {"ok": false, "reason": last_error}
		min_x = minf(min_x, float(position[0]))
		max_x = maxf(max_x, float(position[0]))
		min_z = minf(min_z, float(position[2]))
		max_z = maxf(max_z, float(position[2]))
	var axis := ceili(sqrt(float(target_groups)))
	var size_x := maxf(max_x - min_x, 0.001)
	var size_z := maxf(max_z - min_z, 0.001)
	var grouped: Dictionary = {}
	for item in items:
		var position: Array = item["position"]
		var cell_x := mini(axis - 1, int(floor((float(position[0]) - min_x) / size_x * axis)))
		var cell_z := mini(axis - 1, int(floor((float(position[2]) - min_z) / size_z * axis)))
		var key := "%d:%d" % [cell_x, cell_z]
		if not grouped.has(key):
			grouped[key] = {"cell": [cell_x, cell_z], "ids": [], "positions": []}
		grouped[key]["ids"].append(String(item.get("id", "")))
		grouped[key]["positions"].append(position)
	var groups: Array = []
	for key in grouped.keys():
		var group: Dictionary = grouped[key]
		var bounds := AABB(Vector3(float(group["positions"][0][0]), 0.0, float(group["positions"][0][2])), Vector3.ZERO)
		for position in group["positions"]:
			bounds = bounds.expand(Vector3(float(position[0]), 0.0, float(position[2])))
		groups.append({
			"cell": group["cell"],
			"ids": group["ids"],
			"positions": group["positions"],
			"count": group["ids"].size(),
			"bounds": {"position": [bounds.position.x, bounds.position.y, bounds.position.z],
				"size": [bounds.size.x, bounds.size.y, bounds.size.z]},
		})
	groups.sort_custom(func(a, b): return str(a["cell"]) < str(b["cell"]))
	if groups.size() > MAX_GROUPS:
		last_error = "group budget exceeded"
		return {"ok": false, "reason": last_error, "groups": groups.size()}
	return {"ok": true, "groups": groups, "item_count": items.size(), "target_groups": target_groups}


static func build_multimesh(transforms: Array, mesh: Mesh, material: Material) -> MultiMeshInstance3D:
	if transforms.is_empty() or mesh == null:
		return null
	var multimesh := MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.use_colors = false
	multimesh.use_custom_data = false
	multimesh.mesh = mesh
	multimesh.instance_count = transforms.size()
	for index in range(transforms.size()):
		multimesh.set_instance_transform(index, transforms[index])
	var node := MultiMeshInstance3D.new()
	node.multimesh = multimesh
	node.material_override = material
	return node
