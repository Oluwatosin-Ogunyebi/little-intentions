import {test} from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {panelGripOffset,panelGripPose} from '../src/xr-grab';
test('grip preserves panel offset while translating and rotating, ready to dock',()=>{const handStart=new THREE.Matrix4().compose(new THREE.Vector3(.1,.3,.2),new THREE.Quaternion(),new THREE.Vector3(1,1,1));const panelStart=new THREE.Matrix4().compose(new THREE.Vector3(.4,.5,-.7),new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),.2),new THREE.Vector3(1,1,1));const offset=panelGripOffset(handStart,panelStart);const handMoved=new THREE.Matrix4().compose(new THREE.Vector3(1,2,3),new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),.7),new THREE.Vector3(1,1,1));const result=panelGripPose(handMoved,offset);const relative=handMoved.clone().invert().multiply(result);for(let i=0;i<16;i++)assert.ok(Math.abs(relative.elements[i]-offset.elements[i])<1e-10);});
