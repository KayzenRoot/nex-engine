extends RefCounted
class_name FXLibrary

# NEX M05-S02 elemental VFX reference library. Native GPUParticles3D +
# ParticleProcessMaterial; original procedural radial texture; no third-party
# assets, no gameplay authority and no PoE2 parity claim.

static func _radial_texture() -> ImageTexture:
	var image := Image.create(64, 64, false, Image.FORMAT_RGBA8)
	for y in range(64):
		for x in range(64):
			var dx := (float(x) - 31.5) / 31.5
			var dy := (float(y) - 31.5) / 31.5
			var distance := sqrt(dx * dx + dy * dy)
			image.set_pixel(x, y, Color(1.0, 1.0, 1.0, clampf(1.0 - distance, 0.0, 1.0)))
	return ImageTexture.create_from_image(image)


static func _particle_material(color: Color, additive: bool) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD if additive else BaseMaterial3D.BLEND_MODE_MIX
	material.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	material.albedo_texture = _radial_texture()
	material.albedo_color = color
	material.emission_enabled = true
	material.emission = color
	material.emission_energy_multiplier = 1.6
	return material


static func _gradient(colors: Array) -> GradientTexture1D:
	var gradient := Gradient.new()
	gradient.colors = colors
	gradient.offsets = [0.0, 1.0]
	var texture := GradientTexture1D.new()
	texture.gradient = gradient
	return texture


static func _particles(amount: int, lifetime: float, size: float, color: Color,
		velocity_min: float, velocity_max: float, gravity: Vector3, spread: float,
		additive: bool, explosiveness := 0.0) -> GPUParticles3D:
	var particles := GPUParticles3D.new()
	particles.amount = amount
	particles.lifetime = lifetime
	particles.one_shot = false
	particles.explosiveness = explosiveness
	particles.randomness = 0.2
	particles.local_coords = false
	particles.visibility_aabb = AABB(Vector3(-4.0, -1.0, -4.0), Vector3(8.0, 8.0, 8.0))
	var process := ParticleProcessMaterial.new()
	process.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	process.emission_sphere_radius = 0.35
	process.direction = Vector3(0.0, 1.0, 0.0)
	process.spread = spread
	process.initial_velocity_min = velocity_min
	process.initial_velocity_max = velocity_max
	process.gravity = gravity
	process.scale_min = 0.5
	process.scale_max = 1.2
	process.color = color
	process.color_ramp = _gradient([color, Color(color.r, color.g, color.b, 0.0)])
	particles.process_material = process
	var quad := QuadMesh.new()
	quad.size = Vector2(size, size)
	quad.material = _particle_material(color, additive)
	particles.draw_pass_1 = quad
	particles.emitting = true
	return particles


static func create_fire() -> Node3D:
	return _particles(64, 1.2, 0.35, Color(1.0, 0.42, 0.08), 1.0, 2.5, Vector3(0.0, 1.4, 0.0), 25.0, true)


static func create_frost() -> Node3D:
	return _particles(48, 0.9, 0.28, Color(0.35, 0.75, 1.0), 1.5, 3.0, Vector3(0.0, -0.2, 0.0), 180.0, true)


static func create_smoke() -> Node3D:
	return _particles(32, 2.2, 0.55, Color(0.35, 0.34, 0.32), 0.3, 0.9, Vector3(0.0, 0.4, 0.0), 40.0, false)


static func create_impact(color := Color(1.0, 0.7, 0.25)) -> Node3D:
	return _particles(40, 0.6, 0.22, color, 2.0, 4.0, Vector3(0.0, -1.0, 0.0), 180.0, true, 0.9)


static func create_lightning() -> Node3D:
	var root := Node3D.new()
	var beam := MeshInstance3D.new()
	var cylinder := CylinderMesh.new()
	cylinder.top_radius = 0.03
	cylinder.bottom_radius = 0.08
	cylinder.height = 3.0
	beam.mesh = cylinder
	beam.rotation_degrees = Vector3(0.0, 0.0, 18.0)
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = Color(0.55, 0.8, 1.0)
	material.emission_enabled = true
	material.emission = Color(0.45, 0.75, 1.0)
	material.emission_energy_multiplier = 4.0
	beam.material_override = material
	root.add_child(beam)
	var sparks := create_impact(Color(0.55, 0.8, 1.0))
	sparks.position = Vector3(0.0, -1.4, 0.0)
	root.add_child(sparks)
	return root


static func create_projectile() -> Node3D:
	var root := Node3D.new()
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = Color(1.0, 0.62, 0.2)
	material.emission_enabled = true
	material.emission = Color(1.0, 0.52, 0.12)
	material.emission_energy_multiplier = 4.5
	var core := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 0.18
	sphere.height = 0.36
	core.mesh = sphere
	core.material_override = material
	root.add_child(core)
	var trail := MeshInstance3D.new()
	var cylinder := CylinderMesh.new()
	cylinder.top_radius = 0.02
	cylinder.bottom_radius = 0.1
	cylinder.height = 2.4
	trail.mesh = cylinder
	trail.material_override = material
	trail.rotation_degrees = Vector3(90.0, 0.0, 0.0)
	trail.position = Vector3(0.0, 0.0, 1.2)
	root.add_child(trail)
	var sparks := _particles(24, 0.35, 0.12, Color(1.0, 0.68, 0.3), 0.2, 0.8, Vector3(0.0, 0.2, 0.0), 35.0, true)
	sparks.position = Vector3(0.0, 0.0, 0.2)
	root.add_child(sparks)
	return root


static func create_element(element: String) -> Node3D:
	match element:
		"fire":
			return create_fire()
		"frost":
			return create_frost()
		"lightning":
			return create_lightning()
		"smoke":
			return create_smoke()
		"impact":
			return create_impact()
		"projectile":
			return create_projectile()
	return create_fire()


static func element_color(element: String) -> Color:
	match element:
		"fire":
			return Color(1.0, 0.42, 0.08)
		"frost":
			return Color(0.35, 0.75, 1.0)
		"lightning":
			return Color(0.55, 0.8, 1.0)
		"smoke":
			return Color(0.45, 0.44, 0.42)
		"projectile":
			return Color(1.0, 0.62, 0.2)
	return Color(1.0, 0.7, 0.25)
