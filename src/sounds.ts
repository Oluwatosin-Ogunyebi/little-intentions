/** Quiet synthesized effects; no external media or audio requests. */
export class Soundscape {
  effectsVolume=.45; ambienceVolume=0; private ctx:AudioContext|null=null; private ambient:GainNode|null=null; private oscillators:OscillatorNode[]=[]; private paused=false; private listeners=new Set<()=>void>();
  subscribe(fn:()=>void){this.listeners.add(fn);return()=>this.listeners.delete(fn);}
  private emit(){this.listeners.forEach(fn=>fn());}
  private context(){if(!this.ctx)this.ctx=new AudioContext();if(this.ctx.state==='suspended')void this.ctx.resume().catch(()=>{});return this.ctx;}
  setEffects(value:number){this.effectsVolume=Math.max(0,Math.min(1,value));this.emit();}
  setAmbience(value:number){this.ambienceVolume=Math.max(0,Math.min(1,value));try{if(this.ambienceVolume>0)this.startAmbience();this.updateAmbience();}catch{}this.emit();}
  pauseAmbience(value:boolean){this.paused=value;this.updateAmbience();}
  private startAmbience(){if(this.ambient)return;const ctx=this.context(),gain=ctx.createGain();gain.gain.value=0;gain.connect(ctx.destination);this.ambient=gain;for(const hz of [110,164.81,220]){const o=ctx.createOscillator(),g=ctx.createGain();o.type='sine';o.frequency.value=hz;g.gain.value=.13;o.connect(g).connect(gain);o.start();this.oscillators.push(o);}}
  private updateAmbience(){if(this.ambient&&this.ctx)this.ambient.gain.setTargetAtTime(this.paused?0:this.ambienceVolume*.06,this.ctx.currentTime,.25);}
  victory(){if(!this.effectsVolume)return;try{const ctx=this.context(),start=ctx.currentTime;[523.25,659.25,783.99].forEach((hz,i)=>{const o=ctx.createOscillator(),g=ctx.createGain(),t=start+i*.12;o.type='sine';o.frequency.value=hz;g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(Math.max(.0002,this.effectsVolume*.12),t+.025);g.gain.exponentialRampToValueAtTime(.0001,t+.32);o.connect(g).connect(ctx.destination);o.start(t);o.stop(t+.33);o.onended=()=>{o.disconnect();g.disconnect();};});}catch{}}
  dispose(){for(const o of this.oscillators){try{o.stop();}catch{}o.disconnect();}this.oscillators=[];this.ambient?.disconnect();this.ambient=null;const ctx=this.ctx;this.ctx=null;if(ctx)void ctx.close().catch(()=>{});}
}
