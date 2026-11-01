/** Frame-rate independent easing: rate is the fraction approached per second. */
export function easeFactor(rate:number, dt:number):number { return 1-Math.exp(-Math.max(0,rate)*Math.max(0,dt)); }
export function scaleFromStick(scale:number, axis:number, dt:number):number {
  const deadzone=.2;
  if(!Number.isFinite(axis)||Math.abs(axis)<deadzone)return scale;
  const adjusted=Math.sign(axis)*(Math.abs(axis)-deadzone)/(1-deadzone);
  return Math.min(1.3,Math.max(.35,scale*Math.exp(-adjusted*.55*Math.max(0,dt))));
}
