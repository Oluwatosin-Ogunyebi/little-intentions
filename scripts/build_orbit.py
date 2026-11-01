"""Reproducible Orbit character. Blender 3.4.1, no external dependencies.
Run: blender --background --python scripts/build_orbit.py -- [--render] [--motion]
Blender -Y is front; glTF +Z is front. One Blender unit = one metre.
"""
import bpy, bmesh, math, os, sys, json
from mathutils import Vector, Euler
from math import sin, cos, pi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'artifacts', 'orbit')
BLEND = os.path.join(ROOT, 'assets', 'orbit', 'blender')
GLB = os.path.join(ROOT, 'public', 'assets', 'orbit', 'orbit.glb')
for d in [OUT, BLEND, os.path.dirname(GLB)]: os.makedirs(d, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.actions): bpy.data.actions.remove(d)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.eevee.use_gtao=True; scene.eevee.gtao_distance=0.16; scene.eevee.gtao_factor=1.2
scene.eevee.taa_render_samples=64
scene.render.resolution_x=720; scene.render.resolution_y=720; scene.render.resolution_percentage=100
scene.render.fps=30
scene.view_settings.view_transform='Standard'; scene.view_settings.look='Medium High Contrast'
scene.view_settings.exposure=0; scene.view_settings.gamma=1
scene.world.color=(0.18,0.18,0.18)
parts=[]

def mat(name,color,rough=.45,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m
teal=mat('Orbit | teal plush',(0.005,0.25,0.265),.64)
cream=mat('Orbit | warm cream',(.9,.76,.48),.65)
dark=mat('Headset | midnight graphite',(.012,.034,.045),.42,.08)
rim=mat('Headset | cyan rim',(.025,.47,.57),.36,.12)
black=mat('Face | ink',(.012,.018,.019),.38)
lens=mat('Headset | aurora lens',(.20,.016,.67),.19,.35)
# Exportable texture: purple-to-blue gradient and restrained glossy reflection.
N=256; im=bpy.data.images.new('Orbit visor gradient',width=N,height=N,alpha=True)
px=[]
for iy in range(N):
    v=iy/(N-1)
    for ix in range(N):
        u=ix/(N-1)
        glow=math.exp(-(((u-.28)/.23)**2+((v-.78)/.12)**2)*2)
        line=math.exp(-(((u-.21)/.045)**2+((v-.58)/.26)**2)*2)*.38
        px.extend((min(1,.10+.43*v+glow*.40+line),min(1,.025+.12*(1-v)+glow*.26+line),min(1,.35+.32*v+glow*.3+line),1))
im.pixels=px; im.filepath_raw=os.path.join(BLEND,'visor.png'); im.file_format='PNG'; im.save(); im.pack()
tex=lens.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=im
p=lens.node_tree.nodes.get('Principled BSDF'); lens.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
p.inputs['Coat Weight' if 'Coat Weight' in p.inputs else 'Clearcoat'].default_value=.65

def mesh(name,verts,faces,material,bone=None,weights=None):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); scene.collection.objects.link(ob); ob.data.materials.append(material)
    for f in me.polygons: f.use_smooth=True
    if bone:
        ob.vertex_groups.new(name=bone).add(list(range(len(verts))),1,'REPLACE')
    if weights:
        for i,w in enumerate(weights):
            for bn,value in w.items():
                vg=ob.vertex_groups.get(bn) or ob.vertex_groups.new(name=bn); vg.add([i],value,'REPLACE')
    parts.append(ob); return ob

def ellipsoid(name,loc,scale,material,bone,seg=28,rings=16):
    verts=[]; faces=[]
    for j in range(rings+1):
        a=pi*j/rings
        for i in range(seg):
            t=2*pi*i/seg; verts.append((loc[0]+scale[0]*sin(a)*cos(t),loc[1]+scale[1]*sin(a)*sin(t),loc[2]+scale[2]*cos(a)))
    for j in range(rings):
        for i in range(seg):
            a=j*seg+i;b=j*seg+(i+1)%seg;faces.append((a,b,b+seg,a+seg))
    return mesh(name,verts,faces,material,bone)

def tube(name,points,radii,material,bone,segments=12):
    vs=[];fs=[]
    for i,co in enumerate(points):
        co=Vector(co); tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
        tangent.normalize(); axis=tangent.cross(Vector((0,1,0)))
        if axis.length<.01: axis=tangent.cross(Vector((1,0,0)))
        axis.normalize(); other=tangent.cross(axis).normalized()
        for k in range(segments): vs.append(tuple(co+radii[i]*(cos(k*2*pi/segments)*axis+sin(k*2*pi/segments)*other)))
    for i in range(len(points)-1):
        for k in range(segments): a=i*segments+k;b=i*segments+(k+1)%segments;fs.append((a,b,b+segments,a+segments))
    fs += [tuple(reversed(range(segments))),tuple((len(points)-1)*segments+k for k in range(segments))]
    return mesh(name,vs,fs,material,bone)

# The compact pear-shaped torso is a continuous surface, with softened shoulders.
def torso():
    profile=[(.13,.065,.064),(.16,.115,.094),(.23,.153,.122),(.32,.17,.132),(.41,.157,.122),(.49,.13,.104),(.56,.10,.09),(.60,.061,.06)]
    vs=[];fs=[];ws=[];n=40
    for z,rx,ry in profile:
        for i in range(n):
            a=2*pi*i/n;vs.append((rx*cos(a),ry*sin(a),z)); ws.append({'body':1})
    for j in range(len(profile)-1):
        for i in range(n): a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
    fs.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
    o=mesh('Body — continuous pear silhouette',vs,fs,teal,weights=ws)
    mod=o.modifiers.new('Soft body surface','SUBSURF'); mod.levels=1
    bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
torso()
def belly_patch():
    vs=[];fs=[];n=40
    profile=[(.13,.065,.064),(.16,.115,.094),(.23,.153,.122),(.32,.17,.132),(.41,.157,.122),(.49,.13,.104),(.56,.10,.09),(.60,.061,.06)]
    for j in range(9):
        r=j/8
        for i in range(n):
            a=2*pi*i/n;x=.102*r*cos(a);z=.374+.157*r*sin(a)
            for k in range(len(profile)-1):
                z0,rx0,ry0=profile[k];z1,rx1,ry1=profile[k+1]
                if z0<=z<=z1:
                    f=(z-z0)/(z1-z0);rx=rx0+(rx1-rx0)*f;ry=ry0+(ry1-ry0)*f;break
            # Match subdivision rounding, then sit just above the teal surface.
            y=-ry*math.sqrt(max(0,1-(x/rx)**2))-.003
            vs.append((x,y,z))
    for j in range(8):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append((a,a+n,b+n,b))
    o=mesh('Belly cream surface marking',vs,fs,cream,'body')
    mod=o.modifiers.new('Conform marking to body','SHRINKWRAP');mod.target=bpy.data.objects['Body — continuous pear silhouette'];mod.wrap_method='NEAREST_SURFACEPOINT';mod.offset=.0018
    bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
belly_patch()
ellipsoid('Fox head',(0,0,.785),(.278,.196,.224),teal,'head',36,20)
# Low broad cream muzzle follows the reference; no protruding dog snout.
ellipsoid('Cream muzzle',(0,-.142,.682),(.222,.083,.096),cream,'head',40,20)
ellipsoid('Small dark nose',(0,-.232,.711),(.030,.018,.019),black,'head',24,12)
tube('Mouth centre',[(0,-.234,.704),(0,-.234,.689)], [.004,.004],black,'head',8)
for s in [-1,1]:
    tube('Gentle smile '+str(s),[(0,-.234,.689),(s*.012,-.232,.679),(s*.025,-.23,.679),(s*.035,-.225,.686)],[.004,.004,.0038,.002],black,'head',8)

# Sculpted pointed ears: rounded outline with bulged surfaces and cream inset.
ear_outline=[(-.091,0),(-.104,.058),(-.101,.14),(-.088,.226),(-.067,.246),(-.04,.23),(.033,.166),(.083,.096),(.078,.027),(.035,-.012)]
def ear(s,inner=False):
    center=(s*.176,.005,.949); k=.72 if inner else 1
    vs=[];fs=[];n=len(ear_outline)
    # smooth subdivided closed shell, front ring, central cap and back.
    for factor,y in [(0,-.074 if inner else -.061),(.48,-.072 if inner else -.071),(1,-.053 if inner else -.043),(.86,-.041 if inner else .028),(0,-.031 if inner else .04)]:
        for x,z in ear_outline:
            xx=x*k*factor; zz=(z-.10)*k*factor+.10
            vs.append((center[0]-s*xx,center[1]+y,center[2]+zz))
    for j in range(4):
        for i in range(n): a=j*n+i;b=j*n+(i+1)%n;fs.append((b,a,a+n,b+n) if s==1 else (a,b,b+n,a+n))
    o=mesh(('Inner ear' if inner else 'Ear')+('.L' if s>0 else '.R'),vs,fs,cream if inner else teal,'ear.L' if s>0 else 'ear.R')
    mod=o.modifiers.new('Rounded ear contour','SUBSURF');mod.levels=2
    bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=o.modifiers.new('Optimized ear surface','DECIMATE');mod.ratio=.5;bpy.ops.object.modifier_apply(modifier=mod.name)
for s in [-1,1]: ear(s);ear(s,True)

# Curved headset has a cushion, graphite shell, cyan piping and inset optical surface.
def goggles(name,w,h,z,y,material,bone='head',depth=.022,bulge=.035):
    n=48;vs=[];fs=[]
    for factor,dy in [(0,-bulge),(.35,-bulge*.96),(.70,-bulge*.68),(.92,-bulge*.27),(1,0),(.98,depth)]:
        for i in range(n):
            a=2*pi*i/n;x=w*math.copysign(abs(cos(a))**.58,cos(a))*factor
            zz=h*math.copysign(abs(sin(a))**.72,sin(a))*factor
            if zz<0: zz+=.014*(1-abs(x/w))**3*factor
            vs.append((x,y+dy+.047*(x/w)**2,z+zz))
    for j in range(5):
        for i in range(n): a=j*n+i;b=j*n+(i+1)%n;fs.append((a,a+n,b+n,b))
    fs.append(tuple(5*n+i for i in reversed(range(n))))
    o=mesh(name,vs,fs,material,bone)
    uv=o.data.uv_layers.new(name='Visor UV')
    for poly in o.data.polygons:
        for li in poly.loop_indices:
            v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=((v.x/w+1)/2,(v.z-z+h)/(2*h))
    return o
goggles('Headset soft cushion',.258,.121,.812,-.173,dark,depth=.045,bulge=.026)
goggles('Headset graphite frame',.253,.113,.815,-.215,dark,depth=.024)
goggles('Visor cyan perimeter',.236,.099,.815,-.241,rim,depth=.014,bulge=.025)
goggles('Purple blue optical visor',.228,.092,.816,-.250,lens,depth=.006,bulge=.029)
for s in [-1,1]:
    ellipsoid('Headset side pad '+str(s),(s*.263,-.015,.797),(.046,.092,.083),dark,'head',24,16)
    ellipsoid('Headset side disc '+str(s),(s*.296,-.019,.799),(.014,.064,.060),dark,'head',24,14)
    tube('Temple connector '+str(s),[(s*.231,-.17,.82),(s*.267,-.115,.817),(s*.275,-.055,.81)],[.025,.024,.022],dark,'head',12)
# Broad top band, fitted over skull, not a floating cylinder.
vs=[];fs=[]
for j in range(25):
    a=-.05+pi*.92*j/24
    for x in [-.033,.033]: vs.append((x,-.196*cos(a),.785+.228*sin(a)))
for j in range(24): fs.append((j*2,j*2+1,j*2+3,j*2+2))
strap=mesh('Top headset strap',vs,fs,dark,'head');mod=strap.modifiers.new('Strap thickness','SOLIDIFY');mod.thickness=.014
bpy.context.view_layer.objects.active=strap;bpy.ops.object.modifier_apply(modifier=mod.name)

# Deforming arm and leg capsules have gradual weights over elbow/knee regions.
def limb(name,profile,material,upper,lower,joint,axis='z',n=20):
    vs=[];fs=[];ws=[]
    for x,y,z,rx,ry in profile:
        for i in range(n):
            t=2*pi*i/n;vs.append((x+rx*cos(t),y+ry*sin(t),z))
            w=max(0,min(1,(joint+.045-z)/.09));ws.append({upper:1-w,lower:w})
    for j in range(len(profile)-1):
        for i in range(n): a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
    fs.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
    o=mesh(name,vs,fs,material,weights=ws)
    mod=o.modifiers.new('Soft limb surface','SUBSURF');mod.levels=1
    bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
for s,side in [(1,'L'),(-1,'R')]:
    limb('Arm.'+side,[(s*.139,0,.523,.025,.032),(s*.163,-.005,.501,.052,.054),(s*.196,-.01,.45,.054,.052),(s*.227,-.018,.389,.049,.046),(s*.245,-.026,.341,.046,.043),(s*.246,-.03,.315,.025,.026)],teal,'arm.'+side,'forearm.'+side,.405)
    limb('Leg.'+side,[(s*.084,.006,.228,.027,.032),(s*.09,.009,.20,.054,.059),(s*.096,.005,.155,.054,.058),(s*.102,0,.105,.05,.049),(s*.102,0,.072,.038,.039)],teal,'thigh.'+side,'shin.'+side,.145)
    ellipsoid('Foot.'+side,(s*.103,-.041,.052),(.075,.105,.052),teal,'foot.'+side,24,12)
    # Subtle toe creases, geometry that remains cheap and readable in a close-up.
    for dx in [-.023,.023]:
        tube('Toe crease '+side+str(dx),[(s*.103+dx,-.131,.047),(s*.103+dx,-.127,.061)],[.0018,.0012],dark,'foot.'+side,6)

# Weld parametric poles before glTF triangulation. Repeated centre vertices otherwise
# yield a visible pinched normal on re-import despite looking fine in Blender.
for ob in parts:
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(ob.data);bm.free();ob.data.update()

# Skeleton: body and limbs deform; optical parts have rigid head weights.
arm_data=bpy.data.armatures.new('Orbit skeleton');rig=bpy.data.objects.new('Orbit',arm_data);scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None):
    b=arm_data.edit_bones.new(name);b.head=head;b.tail=tail
    if parent: b.parent=arm_data.edit_bones[parent]
bone('root',(0,0,0),(0,0,.1))
bone('body',(0,0,.20),(0,0,.56),'root')
bone('head',(0,0,.57),(0,0,.91),'body')
for s,side in [(1,'L'),(-1,'R')]:
    bone('ear.'+side,(s*.176,0,.949),(s*.206,0,1.17),'head')
    bone('arm.'+side,(s*.142,0,.509),(s*.221,-.016,.405),'body')
    bone('forearm.'+side,(s*.221,-.016,.405),(s*.247,-.028,.32),'arm.'+side)
    bone('thigh.'+side,(s*.086,0,.225),(s*.099,0,.145),'body')
    bone('shin.'+side,(s*.099,0,.145),(s*.103,0,.065),'thigh.'+side)
    bone('foot.'+side,(s*.103,0,.065),(s*.103,-.095,.045),'shin.'+side)
bpy.ops.object.mode_set(mode='OBJECT')
for o in parts:
    mod=o.modifiers.new('Orbit skeletal deformation','ARMATURE');mod.object=rig;o.parent=rig
for b in rig.pose.bones: b.rotation_mode='XYZ'

def reset_pose():
    for b in rig.pose.bones: b.location=(0,0,0);b.rotation_euler=(0,0,0);b.scale=(1,1,1)
def rot(b,x=0,y=0,z=0):
    # Express animation rotations in character axes, converted to each bone's basis.
    basis=rig.data.bones[b].matrix_local.to_3x3()
    rig.pose.bones[b].rotation_euler=(basis.inverted() @ Euler((x,y,z),'XYZ').to_matrix() @ basis).to_euler('XYZ')
def make_action(name,seconds,pose):
    action=bpy.data.actions.new(name);rig.animation_data_create();rig.animation_data.action=action
    frames=round(seconds*30)
    for f in range(frames+1):
        reset_pose();pose(f/frames,f/30)
        for b in rig.pose.bones:
            b.keyframe_insert(data_path='rotation_euler',frame=f,group=b.name)
            b.keyframe_insert(data_path='location',frame=f,group=b.name)
    for fc in action.fcurves:
        for kp in fc.keyframe_points:kp.interpolation='LINEAR'
    rig.animation_data.action=None
    tr=rig.animation_data.nla_tracks.new();tr.name=name;st=tr.strips.new(name,0,action);st.name=name;tr.mute=True
    return action
def idle(t,sec):
    a=2*pi*t;rot('head',.018*sin(a),.012*sin(a),.025*sin(a));rot('body',.008*sin(a))
    for s,side in [(1,'L'),(-1,'R')]:rot('ear.'+side,.018*sin(a+s),0,s*.012*sin(a));rot('arm.'+side,.018*sin(a),s*.025*sin(a))
def walk(t,sec):
    a=2*pi*t
    # Small alternating steps suit the reference's short rounded legs.
    rig.pose.bones['root'].location.y=-.022+.002*cos(2*a)
    rot('head',-.025,0,-.022*sin(a))
    for s,side in [(1,'L'),(-1,'R')]:
        q=a+(0 if s==1 else pi);swing=-cos(q)
        phase=(t+(0 if s==1 else .5))%1
        if phase<.5:
            fy=-.075+.30*phase; lift=0
        else:
            u=(phase-.5)*2;fy=.075-.15*u;lift=.05*sin(pi*u)**1.5
        dz=.16-.022+.002*cos(2*a)-lift
        dist=min(.1599,math.sqrt(fy*fy+dz*dz))
        bend=2*math.acos(dist/.16)
        thigh=math.atan2(fy,dz)+bend/2
        rot('thigh.'+side,thigh);rot('shin.'+side,-bend);rot('foot.'+side,-thigh+bend)
        rot('arm.'+side,-.75*swing,0,0);rot('forearm.'+side,-.13-.18*max(0,-swing))
        rot('ear.'+side,.035*cos(2*a),s*.025*sin(a),0)
def ask(t,sec):
    a=2*pi*t;rot('head',-.035,.14+.025*sin(a),0);rot('arm.L',-1.5,.13,0);rot('forearm.L',-1.0)
    rot('ear.L',-.10,-.13,0);rot('ear.R',.045,.10,0);rot('arm.R',.04*sin(a))
def interact(t,sec):
    p=(1-cos(2*pi*t))/2;rot('body',.10*p);rot('head',.07*p)
    for s,side in [(1,'L'),(-1,'R')]:
        rot('arm.'+side,-.95*p,s*.13*p,0);rot('forearm.'+side,-.25*p);rot('thigh.'+side,-.10*p)
def celebrate(t,sec):
    a=2*pi*t;p=sin(pi*t)**2
    rig.pose.bones['root'].location.y=.065*p
    rot('head',-.08*p,.065*sin(2*a)*p,0)
    for s,side in [(1,'L'),(-1,'R')]:
        rot('arm.'+side,-.20*p,-s*1.8*p,0);rot('forearm.'+side,-.20*p)
        rot('ear.'+side,0,-s*.10*p,0);rot('thigh.'+side,.10*p);rot('shin.'+side,-.20*p);rot('foot.'+side,.10*p)
actions={}
for name,dur,fn in [('idle',3.2,idle),('walk',.8,walk),('ask_wait',2.4,ask),('interact',1.6,interact),('celebrate',1.8,celebrate)]: actions[name]=make_action(name,dur,fn)
reset_pose();scene.frame_start=0;scene.frame_set(0)

# Merge an export copy to six material primitives / draw calls; retain named editable
# components in the .blend. All vertex groups and skin weights survive the merge.
bpy.ops.object.select_all(action='DESELECT')
export_parts=[]
for o in parts:
    cp=o.copy();cp.data=o.data.copy();scene.collection.objects.link(cp);cp.select_set(True);export_parts.append(cp)
bpy.context.view_layer.objects.active=export_parts[0];bpy.ops.object.join();combined=bpy.context.object;combined.name='Orbit skinned surface'
rig.select_set(True)
bpy.context.view_layer.objects.active=rig
for tr in rig.animation_data.nla_tracks:tr.mute=False
bpy.ops.export_scene.gltf(filepath=GLB,export_format='GLB',use_selection=True,export_animations=True,export_nla_strips=True,export_force_sampling=True,export_frame_range=False,export_skins=True,export_yup=True,export_apply=False)
bpy.data.objects.remove(combined,do_unlink=True)
for tr in rig.animation_data.nla_tracks:tr.mute=True
rig.animation_data.action=actions['idle'];scene.frame_end=96
triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in parts)
metadata={'units':'metres','runtime_up':'+Y','runtime_forward':'+Z','root':'ground contact','rest_height_m':max(v.co.z for o in parts for v in o.data.vertices),'mesh_count':len(parts),'triangles':triangles,'materials':len(set(o.data.materials[0].name for o in parts)),'bones':len(arm_data.bones),'animations':{n:round((a.frame_range[1]-a.frame_range[0])/30,4) for n,a in actions.items()},'walk':'in place; game controls translation','source':'original Orbit sprite sheet; custom authored geometry'}
metadata.update({'runtime_meshes':1,'runtime_primitives':6,'dimensions_m':{'width':.62,'height':metadata['rest_height_m'],'depth':.475},'walk_nominal_speed_m_s':.375,'walk_swing_lift_m':.05})
with open(os.path.join(OUT,'orbit-metadata.json'),'w') as f:json.dump(metadata,f,indent=2)

def aim(o,at):o.rotation_euler=(Vector(at)-o.location).to_track_quat('-Z','Y').to_euler()
groundmat=mat('Preview | ground',(.045,.070,.09),.8)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004));ground=bpy.context.object;ground.name='PREVIEW ground';ground.data.materials.append(groundmat)
for name,loc,power,size,color in [('Key',(-2,-3,4),450,3,(.76,.92,1)),('Fill',(2,-1,2),220,2,(.75,.80,1)),('Rim',(0,2,3),500,2,(.28,1,1))]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
    o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,.55))
data=bpy.data.cameras.new('Preview camera');cam=bpy.data.objects.new('Preview camera',data);scene.collection.objects.link(cam);scene.camera=cam
data.type='ORTHO';data.ortho_scale=1.52
cam.location=(1.7,-3,1.5);aim(cam,(0,0,.61))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BLEND,'orbit.blend'))
if '--render' in sys.argv:
    for name,angle in [('front',0),('three-quarter',35),('side',90),('back',180)]:
        a=math.radians(angle);cam.location=(3*sin(a),-3*cos(a),1.15);aim(cam,(0,0,.61));scene.render.filepath=os.path.join(OUT,name+'.png');bpy.ops.render.render(write_still=True)
if '--motion' in sys.argv:
    scene.render.resolution_x=480;scene.render.resolution_y=480;cam.location=(1.7,-3,1.45);aim(cam,(0,0,.59))
    for name in ['walk','ask_wait','interact','celebrate']:
        rig.animation_data.action=actions[name];end=int(actions[name].frame_range[1]);scene.frame_end=end
        for i in range(8):
            scene.frame_set(round(i*end/8));scene.render.filepath=os.path.join(OUT,name+'-'+str(i)+'.png');bpy.ops.render.render(write_still=True)
print('ORBIT_METADATA '+json.dumps(metadata))
