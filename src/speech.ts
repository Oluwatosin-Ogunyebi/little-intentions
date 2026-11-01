import {type Units} from './usage';
export class OrbitSpeech {
  enabled=false; volume=1; status='Voice off.'; private generation=0; private aborter:AbortController|null=null; private audio:HTMLAudioElement|null=null; private url:string|null=null; private cache=new Map<string,Blob>(); private last=''; private listeners=new Set<()=>void>();
  onUsageStart:()=>string|null=()=>null; onUsageFinish:(id:string,usage:Units|null,durationMs:number)=>void=()=>{};
  subscribe(fn:()=>void){this.listeners.add(fn);return()=>this.listeners.delete(fn);}
  private emit(){this.listeners.forEach(fn=>fn());}
  toggle(){this.enabled=!this.enabled;if(!this.enabled)this.stop();this.status=this.enabled?'AI-generated voice on.':'AI-generated voice muted.';this.emit();}
  setVolume(value:number){this.volume=Math.max(0,Math.min(1,value));if(this.audio)this.audio.volume=this.volume;this.emit();}
  stop(){this.generation++;this.aborter?.abort();this.aborter=null;this.audio?.pause();this.audio=null;if(this.url)URL.revokeObjectURL(this.url);this.url=null;}
  clear(){this.stop();this.last='';}
  async say(text:string,remember=true,loop=false,allowFetch=true){if(!this.enabled||!text||(!allowFetch&&!this.cache.has(text)))return;this.stop();if(remember)this.last=text;const generation=this.generation;this.status='Preparing Orbit’s voice…';this.emit();try{let blob=this.cache.get(text);if(!blob){const controller=new AbortController();this.aborter=controller;const id=this.onUsageStart(),started=Date.now();try{const response=await fetch('/api/speech',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text}),signal:AbortSignal.any([controller.signal,AbortSignal.timeout(12000)])});if(!response.ok)throw Error('Speech unavailable');blob=await response.blob();}finally{if(id)this.onUsageFinish(id,null,Date.now()-started);}if(generation!==this.generation)return;this.cache.set(text,blob);if(this.cache.size>12)this.cache.delete(this.cache.keys().next().value!);}if(generation!==this.generation)return;this.url=URL.createObjectURL(blob);const audio=new Audio(this.url);audio.volume=this.volume;audio.loop=loop;this.audio=audio;await audio.play();if(generation!==this.generation){audio.pause();return;}this.status='Orbit is speaking.';this.emit();audio.onended=()=>{if(generation===this.generation){this.status='Voice ready.';this.emit();}};}catch{if(generation===this.generation){this.status='Voice unavailable; captions still work.';this.emit();}}}
  repeat(){if(this.last)void this.say(this.last);}
}
