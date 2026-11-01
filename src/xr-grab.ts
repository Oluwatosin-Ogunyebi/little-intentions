import * as THREE from 'three';
/** Preserve the panel's offset and orientation when a controller starts gripping it. */
export function panelGripOffset(hand:THREE.Matrix4,panel:THREE.Matrix4):THREE.Matrix4{return hand.clone().invert().multiply(panel);}
export function panelGripPose(hand:THREE.Matrix4,offset:THREE.Matrix4):THREE.Matrix4{return hand.clone().multiply(offset);}
