import bpy, math, os
from mathutils import Vector

# Short stylized 3D comedy-suspense animation.
# Run: blender -b --python render.py

OUT = os.path.join(os.getcwd(), "output")
os.makedirs(OUT, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, "SceneEEVEE") else 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 24 * 32
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = os.path.join(OUT, "bablu_pappu_well.mp4")
scene.world.color = (0.012, 0.018, 0.04)

def mat(name, color, rough=0.75, emission=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    if emission:
        bs.inputs["Emission Color"].default_value=(*color,1)
        bs.inputs["Emission Strength"].default_value=emission
    return m

earth=mat("Moonlit earth",(0.045,0.075,0.09))
stone=mat("Old well stone",(0.22,0.27,0.29))
stone2=mat("Stone highlights",(0.36,0.39,0.37))
blue=mat("Bablu blue kurta",(0.04,0.22,0.8))
orange=mat("Pappu orange kurta",(0.95,0.22,0.035))
skin=mat("Warm skin",(0.72,0.39,0.22))
black=mat("Deep black",(0.008,0.012,0.02))
white=mat("Eyes",(0.95,0.95,0.82))
gold=mat("Moon",(1.0,0.78,0.38), emission=1.8)
green=mat("Tree",(0.025,0.12,0.07))
def apply(obj, material):
    obj.data.materials.append(material); return obj
def cube(name, loc, scale, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name
    o.dimensions=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod=o.modifiers.new("Soft cartoon edges","BEVEL"); mod.width=bevel; mod.segments=2
    return apply(o,material)
def uv(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.ops.object.shade_smooth(); return apply(o,material)
def cyl(name, loc, radius, depth, material, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name; return apply(o,material)
def text_obj(body, loc, size, material):
    cu=bpy.data.curves.new("Caption","FONT"); cu.body=body; cu.size=size; cu.extrude=0.003
    ob=bpy.data.objects.new("Caption: "+body,cu); scene.collection.objects.link(ob); ob.location=loc
    ob.rotation_euler=(math.radians(90),0,0); apply(ob,material); return ob

# Ground and moonlit village silhouettes
cube("Village ground",(0,0,-0.22),(30,22,0.4),earth)
uv("Full moon",(5,5,8),(1.15,1.15,1.15),gold)
for x in [-9,-7,7,9]:
    cyl("Tree trunk",(x,3,1.1),0.22,2.2,stone)
    uv("Tree canopy",(x,3,2.6),(1.15,1.0,1.45),green)
# Well ring and dark opening
cyl("Well base",(0,0,0.12),1.7,0.35,stone,32)
cyl("Well dark opening",(0,0,0.34),1.25,0.08,black,32)
for i in range(20):
    a=2*math.pi*i/20
    ob=cube("Individual well block",(1.48*math.cos(a),1.48*math.sin(a),0.67),(0.55,0.43,0.58),stone2,0.06)
    ob.rotation_euler[2]=a
cyl("Well rim",(0,0,0.98),1.55,0.16,stone,32)

# Two friendly cartoon characters built from simple shapes
def character(name,x,y,shirt):
    parts=[]
    parts.append(uv(name+" head",(x,y,1.95),(0.48,0.42,0.48),skin))
    parts.append(uv(name+" hair",(x,y,2.27),(0.49,0.43,0.22),black))
    parts.append(cube(name+" body",(x,y,1.12),(0.82,0.5,1.05),shirt,0.16))
    for dx in [-0.18,0.18]:
        parts.append(uv(name+" eye",(x+dx,y-0.39,2.02),(0.075,0.045,0.095),white))
        parts.append(uv(name+" pupil",(x+dx,y-0.432,2.02),(0.03,0.018,0.045),black))
    parts.append(uv(name+" nose",(x,y-0.43,1.91),(0.08,0.06,0.07),skin))
    for dx in [-0.22,0.22]:
        parts.append(cube(name+" leg",(x+dx,y,0.38),(0.23,0.28,0.62),black,0.07))
        parts.append(uv(name+" shoe",(x+dx,y-0.1,0.12),(0.2,0.32,0.12),black))
    # Animate a little bob for lively cartoon motion
    for p in parts:
        base=p.location.z
        p.keyframe_insert(data_path="location",frame=1)
        p.location.z=base+0.08
        p.keyframe_insert(data_path="location",frame=20)
        p.location.z=base
        p.keyframe_insert(data_path="location",frame=40)
    return parts
bablu=character("Bablu",-3.1,-1.5,blue)
pappu=character("Pappu",3.0,-1.5,orange)

# Camera and lighting
bpy.ops.object.camera_add(location=(0,-15,7))
cam=bpy.context.object; scene.camera=cam
def point_at(obj, target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
point_at(cam,(0,0,1.1)); cam.data.lens=40
def area(name, loc, power, color, size):
    bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.name=name
    l.data.energy=power; l.data.color=color; l.data.shape='DISK'; l.data.size=size; point_at(l,(0,0,0))
area("Cold moonlight",(0,-4,9),1500,(0.42,0.58,1.0),8)
area("Warm face light",(-5,-4,4),650,(1.0,0.42,0.18),5)

# Captions, timed like a short story. Text faces the camera.
captions=[
(1, "AADHI RAAT... GAON KA SUNSAAN KUAN", (1,1,1)),
(145, "BABLU: BHOOT HAI TOH PEHLE TOKEN LEGA!", (1,0.8,0.2)),
(290, "PAPPU: ANDAR SE AAWAAZ KYUN AA RAHI HAI?", (1,1,1)),
(435, "ANDAR SE: BACHAAO! MAIN PHANS GAYA HOON!", (1,0.85,0.4)),
(580, "BABLU NE RASSI DAALI... AUR EK AADMI NIKLA!", (1,1,1)),
(725, "AADMI: MAIN POLICE INSPECTOR HOON!", (1,0.8,0.2)),
(870, "PAPPU: TOH KUEN MEIN DUTY KARTE HO?", (1,1,1)),
(725, " ", (1,1,1))
]
for fr,body,col in captions:
    if body.strip():
        ob=text_obj(body,(-6.1,-4.0,5.4),0.36,mat("Caption "+str(fr),col,emission=0.5))
        ob.keyframe_insert(data_path="location",frame=fr)
        ob.location.z=5.8; ob.keyframe_insert(data_path="location",frame=fr+100)
        ob.hide_render=True; ob.keyframe_insert(data_path="hide_render",frame=max(1,fr-1))
        ob.hide_render=False; ob.keyframe_insert(data_path="hide_render",frame=fr)
        ob.hide_render=True; ob.keyframe_insert(data_path="hide_render",frame=min(scene.frame_end,fr+140))

# Camera gently pushes in toward the well and then the friends
for fr,loc in [(1,(0,-17,7)),(250,(0,-14,6.2)),(520,(0,-12,5.5)),(768,(0,-14,6.2))]:
    cam.location=loc; point_at(cam,(0,0,1.2)); cam.keyframe_insert(data_path="location",frame=fr); cam.keyframe_insert(data_path="rotation_euler",frame=fr)

# Fade-free end card
end=text_obj("THE END... YA KUEN KA PART 2?",(-4.2,-3.8,4.8),0.48,gold)
end.hide_render=True; end.keyframe_insert(data_path="hide_render",frame=767)
end.hide_render=False; end.keyframe_insert(data_path="hide_render",frame=768)

scene.render.image_settings.color_mode='RGB'
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'
scene.render.filepath=os.path.join(OUT,"bablu_pappu_well.mp4")
scene.frame_set(1)
bpy.ops.render.render(animation=True)
print("Rendered:", scene.render.filepath)
