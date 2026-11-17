extends Control

# Original NEX ARPG HUD: life/mana orbs, target bar and skill hints.
# Drawn procedurally; no third-party textures, fonts or Path of Exile assets.

var health := 100.0
var mana := 100.0
var target_health := 100.0
var message := ""
var message_timer := 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	queue_redraw()


func refresh(current_health: float, current_mana: float, current_target: float, note: String = "") -> void:
	health = clampf(current_health, 0.0, 100.0)
	mana = clampf(current_mana, 0.0, 100.0)
	target_health = clampf(current_target, 0.0, 100.0)
	if not note.is_empty():
		message = note
		message_timer = 1.2
	queue_redraw()


func _process(delta: float) -> void:
	if message_timer > 0.0:
		message_timer -= delta
		if message_timer <= 0.0:
			message = ""
			queue_redraw()


func _draw() -> void:
	var view := size
	var font := ThemeDB.fallback_font

	var bar := Rect2(view.x * 0.5 - 180.0, 178.0, 360.0, 18.0)
	draw_rect(bar, Color(0.03, 0.03, 0.04, 0.88), true)
	draw_rect(Rect2(bar.position + Vector2(2, 2),
		Vector2((bar.size.x - 4.0) * target_health / 100.0, bar.size.y - 4.0)),
		Color(0.55, 0.12, 0.12), true)
	draw_rect(bar, Color(0.28, 0.3, 0.36, 0.9), false, 1.0)
	draw_string(font, Vector2(bar.position.x, bar.position.y - 7.0), "TRAINING DUMMY",
		HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.85, 0.8, 0.75))
	draw_string(font, Vector2(bar.position.x + bar.size.x - 58.0, bar.position.y - 7.0),
		"%d / 100" % int(target_health), HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.85, 0.8, 0.75))

	_draw_orb(Vector2(84.0, view.y - 92.0), 46.0, health / 100.0, Color(0.72, 0.12, 0.12), "LIFE")
	_draw_orb(Vector2(view.x - 84.0, view.y - 92.0), 46.0, mana / 100.0, Color(0.12, 0.32, 0.72), "MANA")

	var slot := 52.0
	var total := slot * 3.0 + 24.0
	var start := Vector2(view.x * 0.5 - total * 0.5, view.y - 78.0)
	var keys := ["LMB", "RMB", "SPACE"]
	var actions := ["MOVE", "SLASH", "SLASH"]
	for index in range(3):
		var rect := Rect2(start + Vector2(index * (slot + 12.0), 0.0), Vector2(slot, slot))
		draw_rect(rect, Color(0.04, 0.05, 0.07, 0.92), true)
		draw_rect(rect, Color(0.25, 0.28, 0.34, 0.95), false, 1.5)
		draw_string(font, rect.position + Vector2(5, 20), keys[index],
			HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color(0.85, 0.88, 0.94))
		draw_string(font, rect.position + Vector2(5, 36), actions[index],
			HORIZONTAL_ALIGNMENT_LEFT, -1, 9, Color(0.55, 0.62, 0.72))

	draw_string(font, Vector2(view.x * 0.5 - 220.0, view.y - 12.0),
		"LMB move · RMB / SPACE attack · WHEEL zoom · F1–F5 switch lab",
		HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.55, 0.62, 0.72))
	if not message.is_empty():
		draw_string(font, Vector2(view.x * 0.5 - 140.0, view.y - 128.0), message,
			HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(1.0, 0.72, 0.3))


func _draw_orb(center: Vector2, radius: float, ratio: float, color: Color, label: String) -> void:
	var font := ThemeDB.fallback_font
	draw_circle(center, radius + 5.0, Color(0.015, 0.018, 0.025, 0.92))
	draw_circle(center, radius, Color(0.04, 0.045, 0.055, 0.95))
	var clamped := clampf(ratio, 0.0, 1.0)
	if clamped > 0.0:
		var points := PackedVector2Array([center])
		var steps := 40
		var start_angle := -PI * 0.5
		var end_angle := start_angle + TAU * clamped
		for index in range(steps + 1):
			var angle := lerpf(start_angle, end_angle, float(index) / float(steps))
			points.append(center + Vector2(cos(angle), sin(angle)) * (radius - 5.0))
		draw_colored_polygon(points, color)
	draw_arc(center, radius, 0.0, TAU, 48, Color(0.3, 0.33, 0.4, 0.9), 2.0)
	draw_string(font, center + Vector2(-24, 5), label,
		HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color(0.92, 0.94, 0.98))
