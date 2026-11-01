"""Independent re-import and deformation checks of the shipped GLB."""
import bpy, os, json, math, struct, hashlib
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT=os.path.join(ROOT,'artifacts','orbit');path=os.path.join(ROOT,'public','assets','orbit','orbit.glb')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
bpy.context.scene.render.fps=30
bpy.ops.import_scene.gltf(filepath=path)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
for tr in rig.animation_data.nla_tracks:tr.mute=True
scene=bpy.context.scene;scene.render.fps=30
actions=list(bpy.data.actions)
result={'file':path,'bytes':os.path.getsize(path),'imported_meshes':len(meshes),'bones':len(rig.data.bones),'animations':{}}
result['sha256']=hashlib.sha256(open(path,'rb').read()).hexdigest()
source_path=os.path.join(ROOT,'assets','orbit','source','orbit-spritesheet.png')
source_meta=json.load(open(os.path.join(ROOT,'assets','orbit','source','orbit-source.json')))
result['original_source_hash_unchanged']=hashlib.sha256(open(source_path,'rb').read()).hexdigest().upper()==source_meta['sha256']
assert result['original_source_hash_unchanged']
for action in actions:
    rig.animation_data.action=action
    frames=[action.frame_range[0]+(action.frame_range[1]-action.frame_range[0])*i/24 for i in range(25)]
    feet={'L':[],'R':[]};bounds=[]
    for frame in frames:
        scene.frame_set(int(frame),subframe=frame-int(frame));deps=bpy.context.evaluated_depsgraph_get()
        points=[]
        for ob in meshes:
            ev=ob.evaluated_get(deps);me=ev.to_mesh();pts=[ev.matrix_world @ v.co for v in me.vertices];points.extend(pts)
            for side in feet:
                group=ob.vertex_groups.get('foot.'+side)
                if group:
                    ids=[v.index for v in ob.data.vertices if any(g.group==group.index and g.weight>.9 for g in v.groups)]
                    if ids: feet[side].append(min(pts[i].z for i in ids))
            ev.to_mesh_clear()
        assert all(math.isfinite(c) for v in points for c in v), 'non-finite deformation'
        bounds.append([[min(v[k] for v in points),max(v[k] for v in points)] for k in range(3)])
    result['animations'][action.name]={'duration_seconds':round((action.frame_range[1]-action.frame_range[0])/30,4),'samples':len(frames),'foot_height_ranges_m':{s:[round(min(v),5),round(max(v),5)] for s,v in feet.items() if v},'all_vertices_finite':True,'min_z':min(b[2][0] for b in bounds),'max_z':max(b[2][1] for b in bounds)}
    if action.name.startswith('walk'):
        contact_error=max(abs(min(l,r)) for l,r in zip(feet['L'],feet['R']))
        result['animations'][action.name]['max_planted_foot_ground_error_m']=contact_error
        assert contact_error<.00001,'walk contact error'
with open(path,'rb') as f:b=f.read()
n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n])
result['gltf']={'meshes':len(g['meshes']),'primitives':sum(len(m['primitives']) for m in g['meshes']),'materials':len(g['materials']),'skins':len(g['skins']),'triangles':sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']),'animations':[a['name'] for a in g['animations']]}
result['gltf']['clip_durations_seconds']={a['name']:max(g['accessors'][s['input']]['max'][0] for s in a['samplers']) for a in g['animations']}
assert sorted(result['gltf']['animations'])==['ask_wait','celebrate','idle','interact','walk']
with open(os.path.join(OUT,'glb-verification.json'),'w') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
# Render the imported runtime geometry, not the original modelling scene.
with bpy.data.libraries.load(os.path.join(ROOT,'assets','orbit','blender','orbit.blend')) as (src,dst):
    dst.objects=[n for n in src.objects if n in ['PREVIEW ground','Key','Fill','Rim','Preview camera']]
for o in dst.objects:
    if o:scene.collection.objects.link(o)
scene.camera=bpy.data.objects['Preview camera'];scene.render.engine='BLENDER_EEVEE'
scene.eevee.use_gtao=True;scene.eevee.gtao_distance=.16;scene.eevee.taa_render_samples=64
scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.world.color=(.18,.18,.18);scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast'
rig.animation_data.action=next(a for a in actions if a.name.startswith('idle'));scene.frame_set(1)
scene.render.filepath=os.path.join(OUT,'glb-reimport.png');bpy.ops.render.render(write_still=True)
