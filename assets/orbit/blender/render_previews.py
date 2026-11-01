"""Render actual turntable and looping motion MP4s from the editable asset."""
import bpy, os, math, sys
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT=os.path.join(ROOT,'artifacts','orbit')
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'assets','orbit','blender','orbit.blend'))
scene=bpy.context.scene;rig=bpy.data.objects['Orbit'];cam=scene.camera
scene.render.resolution_x=480;scene.render.resolution_y=480;scene.eevee.taa_render_samples=32
scene.render.image_settings.file_format='FFMPEG';scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264';scene.render.ffmpeg.constant_rate_factor='MEDIUM'
scene.render.fps=30
def aim():cam.rotation_euler=(Vector((0,0,.60))-cam.location).to_track_quat('-Z','Y').to_euler()
for tr in rig.animation_data.nla_tracks:tr.mute=True
for name in ['walk','ask_wait','interact','celebrate']:
    action=bpy.data.actions[name];rig.animation_data.action=action
    for fc in action.fcurves:
        if not any(m.type=='CYCLES' for m in fc.modifiers):fc.modifiers.new('CYCLES')
    cam.location=(1.7,-3,1.45);aim();scene.frame_start=0;scene.frame_end=round(action.frame_range[1]*2)-1
    scene.render.filepath=os.path.join(OUT,name+'.mp4');bpy.ops.render.render(animation=True)
rig.animation_data.action=bpy.data.actions['idle'];scene.frame_start=0;scene.frame_end=89
def orbit_camera(scene):
    a=2*math.pi*scene.frame_current/90;cam.location=(3*math.sin(a),-3*math.cos(a),1.2);aim()
bpy.app.handlers.frame_change_pre.append(orbit_camera)
scene.render.filepath=os.path.join(OUT,'turntable.mp4');bpy.ops.render.render(animation=True)
