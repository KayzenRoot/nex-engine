shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

// NEX M04 SurfaceBlend reference: triplanar albedo/ORM with a wetness blend.
// Normal mapping is intentionally omitted; the limitation is documented.

uniform sampler2D albedo_tex : source_color, filter_linear_mipmap, repeat_enable;
uniform sampler2D orm_tex : filter_linear_mipmap, repeat_enable;
uniform float uv_scale = 0.45;
uniform float wetness : hint_range(0.0, 1.0) = 0.65;

varying vec3 world_pos;
varying vec3 world_normal;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	vec3 blend = pow(abs(world_normal), vec3(4.0));
	blend /= max(vec3(0.0001), vec3(blend.x + blend.y + blend.z));
	vec3 p = world_pos * uv_scale;
	vec3 albedo = texture(albedo_tex, p.zy).rgb * blend.x
		+ texture(albedo_tex, p.xz).rgb * blend.y
		+ texture(albedo_tex, p.xy).rgb * blend.z;
	vec3 orm = texture(orm_tex, p.zy).rgb * blend.x
		+ texture(orm_tex, p.xz).rgb * blend.y
		+ texture(orm_tex, p.xy).rgb * blend.z;
	ALBEDO = albedo * mix(1.0, 0.62, wetness);
	ROUGHNESS = mix(orm.g, 0.16, wetness);
	METALLIC = orm.b;
	SPECULAR = 0.5;
}
