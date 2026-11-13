extends Node3D
class_name IsometricCameraRig

# NEX-M02-S01 prototype: stable isometric camera rig.
# Deterministic, engine-agnostic configuration; no rendering or gameplay changes.
# Perspective: inclined isometric view. Orthographic: classic isometric comparison.
# Known limitation: pixel_snap quantizes the camera position in meters, not a
# projection-space subpixel snap. Documented in README; not a performance claim.

enum ProjectionMode { PERSPECTIVE, ORTHOGRAPHIC }

@export var projection: ProjectionMode = ProjectionMode.PERSPECTIVE
@export var yaw_deg := 45.0
@export var pitch_deg := -35.264
@export var distance_m := 18.0
@export var ortho_size_m := 14.0
@export var vertical_fov_deg := 40.0
@export var near_clip_m := 0.1
@export var far_clip_m := 500.0
@export var follow_speed := 8.0
@export var dead_zone_fraction := Vector2(0.12, 0.12)
@export var zoom_min := 0.5
@export var zoom_max := 2.0
@export var bounds := Rect2(-50.0, -50.0, 100.0, 100.0)
@export var pixel_snap := false

var camera: Camera3D
var focus := Vector3.ZERO
var zoom := 1.0
var last_error := ""
var _viewport_override := Vector2i.ZERO


func _ready() -> void:
	_build_camera()
	_apply_transform()


func _build_camera() -> void:
	if camera != null:
		return
	camera = Camera3D.new()
	camera.name = "IsoCamera"
	camera.current = true
	camera.near = near_clip_m
	camera.far = far_clip_m
	add_child(camera)


func set_viewport_size(size: Vector2i) -> void:
	_viewport_override = size


func viewport_size() -> Vector2i:
	if _viewport_override != Vector2i.ZERO:
		return _viewport_override
	if is_inside_tree():
		var size := get_viewport().get_visible_rect().size
		if size.x >= 1.0 and size.y >= 1.0:
			return Vector2i(size)
	return Vector2i(1280, 720)


func configure(config: Dictionary) -> bool:
	last_error = ""
	var next_projection := projection
	if config.has("projection"):
		var value := str(config["projection"]).to_lower()
		if value == "perspective" or value == "isometric_perspective":
			next_projection = ProjectionMode.PERSPECTIVE
		elif value == "orthographic" or value == "isometric_orthographic":
			next_projection = ProjectionMode.ORTHOGRAPHIC
		else:
			last_error = "projection must be perspective or orthographic"
			return false

	var next_yaw := float(config.get("yaw_deg", yaw_deg))
	var next_pitch := float(config.get("pitch_deg", pitch_deg))
	var next_distance := float(config.get("distance_m", distance_m))
	var next_ortho := float(config.get("ortho_size_m", ortho_size_m))
	var next_fov := float(config.get("vertical_fov_deg", vertical_fov_deg))
	var next_near := float(config.get("near_clip_m", near_clip_m))
	var next_far := float(config.get("far_clip_m", far_clip_m))
	var next_zoom_min := float(config.get("zoom_min", zoom_min))
	var next_zoom_max := float(config.get("zoom_max", zoom_max))
	var next_speed := float(config.get("follow_speed", follow_speed))
	var next_dead: Variant = config.get("dead_zone_fraction", dead_zone_fraction)
	var next_bounds = config.get("bounds", bounds)
	var next_snap := bool(config.get("pixel_snap", pixel_snap))

	if not is_finite(next_yaw) or absf(next_yaw) > 360.0:
		last_error = "yaw_deg outside [-360,360]"
		return false
	if not is_finite(next_pitch) or next_pitch <= -89.0 or next_pitch >= 89.0:
		last_error = "pitch_deg must be within (-89,89)"
		return false
	if not is_finite(next_distance) or next_distance < 1.0 or next_distance > 500.0:
		last_error = "distance_m outside [1,500]"
		return false
	if not is_finite(next_ortho) or next_ortho < 1.0 or next_ortho > 500.0:
		last_error = "ortho_size_m outside [1,500]"
		return false
	if not is_finite(next_fov) or next_fov < 10.0 or next_fov > 100.0:
		last_error = "vertical_fov_deg outside [10,100]"
		return false
	if not is_finite(next_near) or next_near <= 0.0 or not is_finite(next_far) or next_far <= next_near:
		last_error = "clip planes invalid"
		return false
	if not is_finite(next_zoom_min) or not is_finite(next_zoom_max) or next_zoom_min <= 0.0 or next_zoom_min > next_zoom_max:
		last_error = "zoom range invalid"
		return false
	if not is_finite(next_speed) or next_speed <= 0.0 or next_speed > 100.0:
		last_error = "follow_speed outside (0,100]"
		return false
	if not (next_dead is Vector2) or next_dead.x < 0.0 or next_dead.y < 0.0 or next_dead.x > 0.45 or next_dead.y > 0.45:
		last_error = "dead_zone_fraction must be a Vector2 within [0,0.45]"
		return false
	if not (next_bounds is Rect2) or next_bounds.size.x <= 0.0 or next_bounds.size.y <= 0.0:
		last_error = "bounds must be a positive Rect2"
		return false

	projection = next_projection
	yaw_deg = next_yaw
	pitch_deg = next_pitch
	distance_m = next_distance
	ortho_size_m = next_ortho
	vertical_fov_deg = next_fov
	near_clip_m = next_near
	far_clip_m = next_far
	zoom_min = next_zoom_min
	zoom_max = next_zoom_max
	follow_speed = next_speed
	dead_zone_fraction = next_dead
	bounds = next_bounds
	pixel_snap = next_snap
	zoom = clampf(zoom, zoom_min, zoom_max)
	_build_camera()
	camera.near = near_clip_m
	camera.far = far_clip_m
	_apply_transform()
	return true


func set_focus(target: Vector3) -> void:
	focus = _clamp_to_bounds(target)
	_apply_transform()


func update_follow(target: Vector3, delta: float) -> void:
	if not is_finite(delta) or delta <= 0.0:
		return
	var clamped := _clamp_to_bounds(target)
	var extents := visible_world_extents()
	var dead := Vector2(
		extents["half_width_m"] * dead_zone_fraction.x,
		extents["half_height_m"] * dead_zone_fraction.y
	)
	var desired := focus
	var offset := clamped - focus
	if dead.x >= 0.0 and absf(offset.x) > dead.x:
		desired.x = clamped.x - signf(offset.x) * dead.x
	if dead.y >= 0.0 and absf(offset.y) > dead.y:
		desired.z = clamped.z - signf(offset.z) * dead.y
	var alpha := 1.0 - exp(-follow_speed * delta)
	focus = _clamp_to_bounds(focus.lerp(desired, alpha))
	_apply_transform()


func set_zoom(value: float) -> void:
	if not is_finite(value) or value <= 0.0:
		last_error = "zoom must be positive"
		return
	zoom = clampf(value, zoom_min, zoom_max)
	_apply_transform()


func zoom_by(factor: float) -> void:
	if not is_finite(factor) or factor <= 0.0:
		last_error = "zoom factor must be positive"
		return
	zoom = clampf(zoom * factor, zoom_min, zoom_max)
	_apply_transform()


func camera_basis() -> Basis:
	var yaw := deg_to_rad(yaw_deg)
	var pitch := deg_to_rad(pitch_deg)
	return Basis(Vector3.UP, yaw) * Basis(Vector3.RIGHT, pitch)


func visible_world_extents(aspect: float = -1.0) -> Dictionary:
	var view := viewport_size()
	var used_aspect := aspect if aspect > 0.0 else float(view.x) / float(maxi(view.y, 1))
	var half_height := 0.0
	if projection == ProjectionMode.ORTHOGRAPHIC:
		half_height = ortho_size_m * zoom * 0.5
	else:
		half_height = tan(deg_to_rad(vertical_fov_deg) * 0.5) * distance_m * zoom
	return {
		"half_height_m": half_height,
		"half_width_m": half_height * used_aspect,
		"aspect": used_aspect,
	}


func visible_margin(actors: Array, margin_fraction := 0.0) -> Dictionary:
	var extents := visible_world_extents()
	var basis := camera_basis()
	var right := basis.x
	var up := basis.y
	var half_width := float(extents["half_width_m"]) * (1.0 - margin_fraction)
	var half_height := float(extents["half_height_m"]) * (1.0 - margin_fraction)
	var offenders: Array[int] = []
	for index in range(actors.size()):
		if not (actors[index] is Vector3):
			offenders.append(index)
			continue
		var relative: Vector3 = actors[index] - focus
		if absf(relative.dot(right)) > half_width or absf(relative.dot(up)) > half_height:
			offenders.append(index)
	return {"all_inside": offenders.is_empty(), "offenders": offenders}


func world_to_screen(world: Vector3) -> Vector2:
	if camera == null:
		return Vector2.ZERO
	return camera.unproject_position(world)


func screen_to_world(screen: Vector2, plane_y := 0.0) -> Vector3:
	if camera == null:
		return Vector3.ZERO
	var origin := camera.project_ray_origin(screen)
	var direction := camera.project_ray_normal(screen)
	if absf(direction.y) < 0.000001:
		last_error = "screen ray is parallel to the reference plane"
		return Vector3.ZERO
	var distance := (plane_y - origin.y) / direction.y
	return origin + direction * distance


func get_state() -> Dictionary:
	var view := viewport_size()
	var state := {
		"preset_id": "m02-s01-default",
		"projection": "isometric_orthographic" if projection == ProjectionMode.ORTHOGRAPHIC else "isometric_perspective",
		"position_m": _vector_array(_camera_position()),
		"target_m": _vector_array(focus),
		"view_rotation_degrees": {"yaw_deg": yaw_deg, "pitch_deg": pitch_deg},
		"near_clip_m": near_clip_m,
		"far_clip_m": far_clip_m,
		"stability": {"snap_to_pixel": pixel_snap, "anchor_offset_px": [0, 0]},
		"viewport": {"width_px": view.x, "height_px": view.y, "unit": "px"},
		"focus_m": _vector_array(focus),
		"zoom": zoom,
	}
	if projection == ProjectionMode.ORTHOGRAPHIC:
		state["ortho_size_m"] = ortho_size_m * zoom
	else:
		state["vertical_fov_degrees"] = vertical_fov_deg
	return state


func replay(events: Array, fixed_delta := 0.0166667, initial_focus := Vector3.ZERO, initial_zoom := 1.0) -> Array:
	var states: Array = []
	set_zoom(initial_zoom)
	set_focus(initial_focus)
	for event in events:
		if not (event is Dictionary):
			continue
		if event.has("zoom"):
			zoom = clampf(float(event["zoom"]), zoom_min, zoom_max)
		if event.has("target"):
			var target_value = event["target"]
			if target_value is Vector3:
				update_follow(target_value, fixed_delta)
			elif target_value is Array and target_value.size() == 3:
				update_follow(Vector3(float(target_value[0]), float(target_value[1]), float(target_value[2])), fixed_delta)
		states.append(get_state())
	return states


func _camera_position() -> Vector3:
	if camera == null:
		return focus
	return camera.position


func _apply_transform() -> void:
	if camera == null:
		return
	var basis := camera_basis()
	var position := focus + basis.z * distance_m * zoom
	if pixel_snap:
		position = Vector3(snappedf(position.x, 0.01), snappedf(position.y, 0.01), snappedf(position.z, 0.01))
	camera.transform = Transform3D(basis, position)
	if projection == ProjectionMode.ORTHOGRAPHIC:
		camera.projection = Camera3D.PROJECTION_ORTHOGONAL
		camera.size = ortho_size_m * zoom
	else:
		camera.projection = Camera3D.PROJECTION_PERSPECTIVE
		camera.fov = vertical_fov_deg
	camera.near = near_clip_m
	camera.far = far_clip_m


func _clamp_to_bounds(point: Vector3) -> Vector3:
	return Vector3(
		clampf(point.x, bounds.position.x, bounds.position.x + bounds.size.x),
		point.y,
		clampf(point.z, bounds.position.y, bounds.position.y + bounds.size.y)
	)


func _vector_array(value: Vector3) -> Array:
	return [value.x, value.y, value.z]
