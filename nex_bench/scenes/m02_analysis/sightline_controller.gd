extends Node3D
class_name SightlineController

# NEX-M02-S02 prototype: deterministic sightline/reveal policy.
# Occluders are AABB volumes (mock geometry; no rendering integration).
# Policy: player is always revealed; critical threats are revealed; decoration
# never is; gameplay visibility is computed independently and never altered.
# Hard occluders (wall/column/tall prop) keep opacity and expose a silhouette;
# soft occluders (vegetation/effect) fade to target_alpha. Hysteresis prevents
# flicker. No shader, scene or engine change.

enum OccluderKind { WALL, COLUMN, VEGETATION, EFFECT, TALL_PROP }
enum ActorPriority { PLAYER, THREAT, DECORATION }

@export var max_reveal_occluders := 8
@export var enter_delay_s := 0.08
@export var exit_delay_s := 0.20
@export var fade_speed := 6.0
@export var target_alpha := 0.35
@export var silhouette_alpha := 0.6
@export var critical_threat_distance_m := 12.0

var last_error := ""
var _camera_position := Vector3.ZERO
var _occluders: Dictionary = {}
var _actors: Array = []
var _states: Dictionary = {}


func configure(config: Dictionary) -> bool:
	last_error = ""
	var next_max := int(config.get("max_reveal_occluders", max_reveal_occluders))
	var next_enter := float(config.get("enter_delay_s", enter_delay_s))
	var next_exit := float(config.get("exit_delay_s", exit_delay_s))
	var next_fade := float(config.get("fade_speed", fade_speed))
	var next_target := float(config.get("target_alpha", target_alpha))
	var next_silhouette := float(config.get("silhouette_alpha", silhouette_alpha))
	var next_critical := float(config.get("critical_threat_distance_m", critical_threat_distance_m))
	if next_max < 1 or next_max > 64:
		last_error = "max_reveal_occluders outside [1,64]"
		return false
	if not is_finite(next_enter) or next_enter < 0.0 or next_enter > 2.0:
		last_error = "enter_delay_s outside [0,2]"
		return false
	if not is_finite(next_exit) or next_exit < 0.0 or next_exit > 2.0:
		last_error = "exit_delay_s outside [0,2]"
		return false
	if not is_finite(next_fade) or next_fade <= 0.0 or next_fade > 60.0:
		last_error = "fade_speed outside (0,60]"
		return false
	if not is_finite(next_target) or next_target < 0.0 or next_target > 0.95:
		last_error = "target_alpha outside [0,0.95]"
		return false
	if not is_finite(next_silhouette) or next_silhouette < 0.05 or next_silhouette > 1.0:
		last_error = "silhouette_alpha outside [0.05,1]"
		return false
	if not is_finite(next_critical) or next_critical <= 0.0 or next_critical > 100.0:
		last_error = "critical_threat_distance_m outside (0,100]"
		return false
	max_reveal_occluders = next_max
	enter_delay_s = next_enter
	exit_delay_s = next_exit
	fade_speed = next_fade
	target_alpha = next_target
	silhouette_alpha = next_silhouette
	critical_threat_distance_m = next_critical
	return true


func set_camera_position(position: Vector3) -> void:
	_camera_position = position


func register_occluder(id: String, box: AABB, kind: OccluderKind, transparent := false) -> bool:
	last_error = ""
	if id.is_empty():
		last_error = "occluder id is empty"
		return false
	if _occluders.has(id):
		last_error = "duplicate occluder id: " + id
		return false
	if box.size.x <= 0.0 or box.size.y <= 0.0 or box.size.z <= 0.0:
		last_error = "occluder size must be positive"
		return false
	if kind < OccluderKind.WALL or kind > OccluderKind.TALL_PROP:
		last_error = "invalid occluder kind"
		return false
	_occluders[id] = {"box": box, "kind": kind, "transparent": transparent}
	_states[id] = {
		"active": false, "progress": 0.0, "silhouette": false, "capped": false,
		"blocked_elapsed": 0.0, "clear_elapsed": 0.0, "blockers": [],
	}
	return true


func move_occluder(id: String, box: AABB) -> bool:
	if not _occluders.has(id) or box.size.x <= 0.0 or box.size.y <= 0.0 or box.size.z <= 0.0:
		return false
	_occluders[id]["box"] = box
	return true


func remove_occluder(id: String) -> bool:
	if not _occluders.has(id):
		return false
	_occluders.erase(id)
	_states.erase(id)
	return true


func clear_occluders() -> void:
	_occluders.clear()
	_states.clear()


func set_actors(actors: Array) -> bool:
	last_error = ""
	var next_actors: Array = []
	var seen: Dictionary = {}
	var player_count := 0
	for entry in actors:
		if not (entry is Dictionary):
			last_error = "actor must be a dictionary"
			return false
		var id := str(entry.get("id", ""))
		var priority := int(entry.get("priority", -1))
		var position = entry.get("position", null)
		if id.is_empty() or seen.has(id):
			last_error = "actor id is empty or duplicated"
			return false
		if priority < ActorPriority.PLAYER or priority > ActorPriority.DECORATION:
			last_error = "invalid actor priority"
			return false
		if not (position is Vector3):
			last_error = "actor position must be Vector3"
			return false
		if priority == ActorPriority.PLAYER:
			player_count += 1
			if player_count > 1:
				last_error = "at most one player actor is allowed"
				return false
		seen[id] = true
		next_actors.append({"id": id, "priority": priority, "position": position})
	_actors = next_actors
	return true


func segment_intersects_aabb(start: Vector3, end: Vector3, box: AABB) -> bool:
	var tmin := 0.0
	var tmax := 1.0
	for axis in range(3):
		var origin: float = start[axis]
		var direction: float = end[axis] - origin
		var low: float = box.position[axis]
		var high: float = low + box.size[axis]
		if absf(direction) < 0.000000001:
			if origin < low or origin > high:
				return false
		else:
			var first := (low - origin) / direction
			var second := (high - origin) / direction
			if first > second:
				var swap := first
				first = second
				second = swap
			tmin = maxf(tmin, first)
			tmax = minf(tmax, second)
			if tmin > tmax:
				return false
	return true


func update(delta: float) -> void:
	if not is_finite(delta) or delta <= 0.0:
		return
	var actor_states: Array = []
	for actor in _actors:
		var blocked_by: Array[String] = []
		var blocked: bool = false
		for id in _occluders.keys():
			if bool(_occluders[id]["transparent"]):
				continue
			if segment_intersects_aabb(_camera_position, actor["position"], _occluders[id]["box"]):
				blocked_by.append(id)
				blocked = true
		var distance: float = _camera_position.distance_to(actor["position"])
		var critical: bool = actor["priority"] == ActorPriority.THREAT and distance <= critical_threat_distance_m
		var needs_reveal: bool = actor["priority"] == ActorPriority.PLAYER or critical
		var danger_alert: bool = actor["priority"] == ActorPriority.THREAT and blocked
		actor_states.append({
			"id": actor["id"], "priority": actor["priority"], "position": actor["position"],
			"gameplay_visible": not blocked, "needs_reveal": needs_reveal,
			"critical": critical, "danger_alert": danger_alert, "blocked_by": blocked_by,
		})

	for id in _occluders.keys():
		var state: Dictionary = _states[id]
		var requested := false
		var request_priorities: Array[int] = []
		if not bool(_occluders[id]["transparent"]):
			for actor_state in actor_states:
				if actor_state["needs_reveal"] and actor_state["blocked_by"].has(id):
					requested = true
					request_priorities.append(int(actor_state["priority"]))
		state["blockers"] = request_priorities
		if requested:
			state["blocked_elapsed"] = float(state["blocked_elapsed"]) + delta
			state["clear_elapsed"] = 0.0
			if float(state["blocked_elapsed"]) >= enter_delay_s:
				state["active"] = true
				state["progress"] = minf(1.0, float(state["progress"]) + fade_speed * delta)
				state["silhouette"] = _is_hard(int(_occluders[id]["kind"]))
		else:
			state["blocked_elapsed"] = 0.0
			state["clear_elapsed"] = float(state["clear_elapsed"]) + delta
			if float(state["clear_elapsed"]) >= exit_delay_s:
				state["progress"] = maxf(0.0, float(state["progress"]) - fade_speed * delta)
				state["active"] = float(state["progress"]) > 0.0
				state["silhouette"] = bool(state["active"]) and _is_hard(int(_occluders[id]["kind"]))
		state["capped"] = false

	_apply_cap()

	var readable: Dictionary = {}
	for actor_state in actor_states:
		var visible := true
		if not bool(actor_state["gameplay_visible"]):
			visible = false
			for blocker in actor_state["blocked_by"]:
				if bool(_states[blocker]["active"]):
					visible = true
					break
		readable[actor_state["id"]] = visible
		actor_state["visual_readable"] = visible

	var critical_unseen := false
	var alerts := 0
	for actor_state in actor_states:
		if actor_state["danger_alert"]:
			alerts += 1
			if actor_state["critical"] and not bool(actor_state["visual_readable"]):
				critical_unseen = true
		actor_state["position"] = _vector_array(actor_state["position"])

	last_state = {
		"camera_position": _vector_array(_camera_position),
		"actors": actor_states,
		"occluders": [],
		"summary": {
			"active_reveals": _active_count(),
			"max_reveal": max_reveal_occluders,
			"danger_alerts": alerts,
			"critical_unseen": critical_unseen,
		},
	}
	for id in _occluders.keys():
		var state: Dictionary = _states[id]
		var alpha := 1.0
		if not _is_hard(int(_occluders[id]["kind"])):
			alpha = lerpf(1.0, target_alpha, float(state["progress"]))
		last_state["occluders"].append({
			"id": id,
			"kind": int(_occluders[id]["kind"]),
			"transparent": bool(_occluders[id]["transparent"]),
			"active": bool(state["active"]),
			"reveal_progress": float(state["progress"]),
			"alpha": alpha,
			"silhouette": bool(state["silhouette"]),
			"capped": bool(state["capped"]),
			"blockers": state["blockers"],
		})


var last_state: Dictionary = {}


func get_state() -> Dictionary:
	return last_state.duplicate(true)


func _apply_cap() -> void:
	var active: Array = []
	for id in _occluders.keys():
		if bool(_states[id]["active"]):
			var center: Vector3 = _occluders[id]["box"].get_center()
			active.append({"id": id, "distance": _camera_position.distance_to(center)})
	active.sort_custom(func(a, b): return a["distance"] < b["distance"])
	for index in range(max_reveal_occluders, active.size()):
		var state: Dictionary = _states[active[index]["id"]]
		state["active"] = false
		state["progress"] = 0.0
		state["silhouette"] = false
		state["capped"] = true


func _active_count() -> int:
	var count := 0
	for id in _states:
		if bool(_states[id]["active"]):
			count += 1
	return count


func _is_hard(kind: int) -> bool:
	return kind == OccluderKind.WALL or kind == OccluderKind.COLUMN or kind == OccluderKind.TALL_PROP


func _vector_array(value: Vector3) -> Array:
	return [value.x, value.y, value.z]
