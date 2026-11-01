import * as THREE from 'three';

/** A short, bounded burst in village space. */
export class Celebration {
  private group=new THREE.Group(); private pieces:{mesh:THREE.Mesh;velocity:THREE.Vector3}[]=[]; private age=0;
  constructor(private parent:THREE.Object3D){this.group.visible=false;parent.add(this.group);const colors=['#f8c451','#f07c70','#58c0a4','#d69fd9'];for(let i=0;i<32;i++){const mesh=new THREE.Mesh(new THREE.PlaneGeometry(.085,.12),new THREE.MeshBasicMaterial({color:colors[i%colors.length],side:THREE.DoubleSide,transparent:true}));this.group.add(mesh);this.pieces.push({mesh,velocity:new THREE.Vector3()});}}
  burst(position:THREE.Vector3){this.group.position.copy(position);this.age=0;this.group.visible=true;this.pieces.forEach(({mesh,velocity},i)=>{const angle=i*2.39996;mesh.position.set(0,.8,0);mesh.rotation.set(i*.31,i*.47,0);(mesh.material as THREE.MeshBasicMaterial).opacity=1;velocity.set(Math.cos(angle)*(.3+(i%3)*.08),.85+(i%5)*.07,Math.sin(angle)*(.3+(i%3)*.08));});}
  clear(){this.group.visible=false;}
  update(dt:number){if(!this.group.visible)return;this.age+=dt;if(this.age>=2){this.clear();return;}for(const {mesh,velocity} of this.pieces){velocity.y-=.65*dt;mesh.position.addScaledVector(velocity,dt);mesh.rotation.x+=dt*2;mesh.rotation.z+=dt*1.5;(mesh.material as THREE.MeshBasicMaterial).opacity=Math.min(1,(2-this.age)*2);}}
}
