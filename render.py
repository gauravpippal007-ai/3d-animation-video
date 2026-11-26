import bpy, math, os
from mathutils import Vector

# 3D village comedy short: The Shoe Thief
OUT = os.path.join(os.getcwd(), "output")
os.makedirs(OUT, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.taa_render_samples = 8
scene.render.resolution_x = 854
scene.render.resolution_y = 480
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 24 * 32
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = os.path.join(OUT, "bablu_shoe_thief.mp4")
scene.world.color = (0.025, 0.035, 0.06)
scene.view_settings.view_transform = 'Standard'

def material(name, color, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = 0.78
    if emission:
        bs.inputs["Emission Color"].default_value = (*color, 1)
        bs.inputs["Emission Strength"].default_value = emission
    return m

earth=material("Warm village ground",(0.20,0.14,0.08))
wall=material("Mud house",(0.55,0.29,0.13))
roof=material("Thatched roof",(0.20,0.10,0.035))
blue=material("Bablu blue",(0.03,0.18,0.85))
orange=material("Pappu orange",(0.95,0.24,0.025))
purple=material("Sarpanch purple",(0.28,0.08,0.48))
skin=material("Skin",(0.72,0.39,0.22))
hair=material("Hair",(0.025,0.018,0.012))
white=material("Eyes",(0.95,0.92,0.78))
black=material("Black shoes",(0.012,0.012,0.018))
moonmat=material("Moonlight",(1.0,0.78,0.42),1.5)
green=material("Tree green",(0.035,0.20,0.07))
def assign(o,m): o.data.materials.append(m); return o
def cube(name, loc, scale, m, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod=o.modifiers.new("Rounded cartoon edges","BEVEL"); mod.width=bevel; mod.segments=2
    return assign(o,m)
def sphere(name, loc, scale, m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    return assign(o,m)
def cylinder(name, loc, radius, depth, m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius, depth=depth, location=loc)
    return assign(bpy.context.object,m)
def animate_z(obj, keys):
    for frame,z in keys:
        obj.location.z=z
        obj.keyframe_insert(data_path="location",frame=frame)
def caption(body, start, end, size=0.42):
    cu=bpy.data.curves.new("CaptionCurve","FONT"); cu.body=body; cu.size=size
    cu.extrude=0.002
    ob=bpy.data.objects.new("Caption "+body,cu); scene.collection.objects.link(ob)
    ob.location=(-7.4,-5.0,6.0); ob.rotation_euler=(math.radians(90),0,0)
    assign(ob, moonmat)
    ob.hide_render=True; ob.keyframe_insert(data_path="hide_render",frame=max(1,start-1))
    ob.hide_render=False; ob.keyframe_insert(data_path="hide_render",frame=start)
    ob.hide_render=True; ob.keyframe_insert(data_path="hide_render",frame=end)

# Ground, village houses, trees and moon
cube("Village floor",(0,0,-0.3),(32,24,0.5),earth)
sphere("Moon",(6,5,8),(1.0,1.0,1.0),moonmat)
for x in (-9,8):
    cube("Mud house",(x,3,1.25),(4,3,2.5),wall,0.12)
    roofob=cube("Sloping roof",(x,3,2.75),(4.5,3.5,0.35),roof,0.08)
    roofob.rotation_euler[1]=0.10
    cube("Door",(x,1.43,0.8),(0.8,0.12,1.6),hair,0.04)
for x in (-7,-5,6,9):
    cylinder("Tree trunk",(x,4,1.0),0.18,2.0,roof)
    sphere("Tree crown",(x,4,2.5),(1.0,1.0,1.3),green)

# Character rig made from grouped simple cartoon pieces
def character(name,x,y,shirt):
    root=bpy.data.objects.new(name+" movement",None); scene.collection.objects.link(root); root.location=(x,y,0)
    pieces=[]
    def add(o):
        o.parent=root; pieces.append(o); return o
    add(cube(name+" body",(0,0,1.25),(0.85,0.55,1.05),shirt,0.15))
    add(sphere(name+" head",(0,-0.02,2.05),(0.48,0.43,0.48),skin))
    add(sphere(name+" hair",(0,0.02,2.36),(0.49,0.44,0.20),hair))
    for dx in (-0.18,0.18):
        add(sphere(name+" eye",(dx,-0.405,2.12),(0.075,0.035,0.09),white))
        add(sphere(name+" pupil",(dx,-0.438,2.12),(0.028,0.018,0.04),hair))
        add(cube(name+" leg",(dx,0,0.42),(0.23,0.28,0.65),hair,0.06))
        add(sphere(name+" shoe",(dx,-0.15,0.12),(0.22,0.34,0.12),black))
    return root
bablu=character("Bablu",-3.2,-1.0,blue)
pappu=character("Pappu",0.0,-1.0,orange)
sarpanch=character("Sarpanch",4.0,1.0,purple)

# Shoes scattered in front of the houses; one pair is taken by the dog
shoes=[]
for i in range(7):
    sh=sphere("Stolen shoe",( -5.5+i*1.45, -2.8, 0.18),(0.34,0.16,0.12),black)
    sh.rotation_euler[2]=0.25*i
    shoes.append(sh)
dogmat=material("Dog brown",(0.30,0.12,0.035))
dog=sphere("Dog body",(5.8,-2.0,0.55),(0.72,0.35,0.38),dogmat)
doghead=sphere("Dog head",(6.35,-2.0,0.72),(0.35,0.30,0.32),dogmat)
for x in (5.4,6.0):
    cube("Dog leg",(x,-2.0,0.22),(0.16,0.18,0.48),dogmat)
shoe_in_mouth=sphere("Shoe in dog's mouth",(6.55,-2.25,0.58),(0.34,0.13,0.10),black)

# Camera and lights
bpy.ops.object.camera_add(location=(0,-19,8))
cam=bpy.context.object; scene.camera=cam; cam.data.lens=42
def look(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
look(cam,(0,0,1.2))
bpy.ops.object.light_add(type='AREA',location=(0,-5,10))
light=bpy.context.object; light.data.energy=1700; light.data.shape='DISK'; light.data.size=9; look(light,(0,0,0))
bpy.ops.object.light_add(type='POINT',location=(6,4,6))
bpy.context.object.data.energy=350

# Action beats: suspicious shadow, chase, reveal, dog punchline, faint
for f,loc in [(1,(-3.2,-1,0)),(180,(-3.2,-1,0)),(300,(-1.3,-1,0)),(480,(-3.2,-1,0)),(768,(-3.2,-1,0))]:
    bablu.location=loc; bablu.keyframe_insert(data_path="location",frame=f)
for f,loc in [(1,(0,-1,0)),(240,(0,-1,0)),(360,(1.2,-1,0)),(768,(0,-1,0))]:
    pappu.location=loc; pappu.keyframe_insert(data_path="location",frame=f)
for f,loc in [(1,(4,1,0)),(400,(4,1,0)),(520,(2.8,0,0)),(768,(4,1,0))]:
    sarpanch.location=loc; sarpanch.keyframe_insert(data_path="location",frame=f)
# Shadow thief movement and dog chewing
for f,z in [(1,0.18),(550,0.18),(610,0.65),(650,0.18),(768,0.18)]:
    shoe_in_mouth.location.z=z; shoe_in_mouth.keyframe_insert(data_path="location",frame=f)
for f,scale in [(1,(1,1,1)),(700,(1,1,1)),(730,(0.01,0.01,0.01)),(768,(0.01,0.01,0.01))]:
    bablu.scale=scale; bablu.keyframe_insert(data_path="scale",frame=f)

# On-screen Roman Hindi captions for viewers; add Hindi voice later in an editor.
beats=[
(1,120,"RAAT MEIN GAON KE JOOTE GAYAB!"),
(121,230,"BABLU: AAJ CHOR KO PAKADUNGA!"),
(231,330,"AADHI RAAT... KAALI PARCHHAI AAYI!"),
(331,420,"BABLU: PAKAD LIYA, CHAPPAL KE DON!"),
(421,500,"AREY! YE TOH SARPANCH NIKLA!"),
(501,580,"SARPANCH: MAIN JODI MILATA HOON!"),
(581,660,"TERE JOOTE MERE KUTTE NE KHA LIYE!"),
(661,730,"KAL SE JOOTE PE TAX LAGEGA!"),
(731,768,"BABLU BEHOSH! PART 2? COMMENT KARO!")
]
for a,b,t in beats: caption(t,a,b,0.40)

# Camera push-in on the final gag
for f,loc in [(1,(0,-19,8)),(300,(0,-17,7)),(540,(0,-15,6.5)),(768,(0,-16,7))]:
    cam.location=loc; look(cam,(0,0,1.2)); cam.keyframe_insert(data_path="location",frame=f); cam.keyframe_insert(data_path="rotation_euler",frame=f)

scene.frame_set(1)
scene.render.image_settings.color_mode='RGB'
scene.render.filepath=os.path.join(OUT,"bablu_shoe_thief.mp4")
bpy.ops.render.render(animation=True)
print("Rendered:",scene.render.filepath)
