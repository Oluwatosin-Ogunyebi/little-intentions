import {test} from 'node:test';
import assert from 'node:assert/strict';
import {OrbitSpeech} from '../src/speech';

test('speech ignores late audio after interruption and repeats cached audio',async()=>{
 const oldFetch=globalThis.fetch, oldAudio=globalThis.Audio, oldCreate=URL.createObjectURL, oldRevoke=URL.revokeObjectURL;
 let calls=0,plays=0, resolveFetch!:(r:Response)=>void;
 globalThis.fetch=(()=>{calls++;return new Promise<Response>(r=>resolveFetch=r);}) as typeof fetch;
 globalThis.Audio=class {onended:(()=>void)|null=null;pause(){} async play(){plays++;}} as unknown as typeof Audio;
 URL.createObjectURL=()=> 'blob:test';URL.revokeObjectURL=()=>{};
 try{const speech=new OrbitSpeech();speech.toggle();const pending=speech.say('A question');speech.stop();resolveFetch(new Response(new Blob(['audio'])));await pending;assert.equal(plays,0);const current=speech.say('A question');resolveFetch(new Response(new Blob(['audio'])));await current;assert.equal(plays,1);speech.repeat();await new Promise(r=>setTimeout(r,0));assert.equal(plays,2);assert.equal(calls,2);const cue=speech.say('Hmm...',false);resolveFetch(new Response(new Blob(['cue'])));await cue;assert.equal(plays,3);speech.repeat();await new Promise(r=>setTimeout(r,0));assert.equal(plays,4);assert.equal(calls,3);speech.clear();speech.repeat();await new Promise(r=>setTimeout(r,0));assert.equal(plays,4);}finally{globalThis.fetch=oldFetch;globalThis.Audio=oldAudio;URL.createObjectURL=oldCreate;URL.revokeObjectURL=oldRevoke;}
});

test('travel audio loops, stops on arrival, and respects voice volume',async()=>{
 const oldFetch=globalThis.fetch,oldAudio=globalThis.Audio,oldCreate=URL.createObjectURL,oldRevoke=URL.revokeObjectURL;let instance:any;
 globalThis.fetch=(async()=>new Response(new Blob(['sound']))) as typeof fetch;
 globalThis.Audio=class {loop=false;volume=1;paused=false;onended:null=null;constructor(){instance=this;}async play(){}pause(){this.paused=true;}} as unknown as typeof Audio;
 URL.createObjectURL=()=> 'blob:test';URL.revokeObjectURL=()=>{};
 try{const speech=new OrbitSpeech();speech.toggle();speech.setVolume(.5);await speech.say('Doo doo doo.',false,true);assert.equal(instance.loop,true);assert.equal(instance.volume,.5);speech.stop();assert.equal(instance.paused,true);}finally{globalThis.fetch=oldFetch;globalThis.Audio=oldAudio;URL.createObjectURL=oldCreate;URL.revokeObjectURL=oldRevoke;}
});

test('historical replay uses cached sound and never fetches missing audio',async()=>{
 const oldFetch=globalThis.fetch,oldAudio=globalThis.Audio,oldCreate=URL.createObjectURL,oldRevoke=URL.revokeObjectURL;let calls=0,plays=0;
 globalThis.fetch=(async()=>{calls++;return new Response(new Blob(['sound']));}) as typeof fetch;globalThis.Audio=class{loop=false;volume=1;onended:null=null;async play(){plays++;}pause(){}} as unknown as typeof Audio;URL.createObjectURL=()=> 'blob:test';URL.revokeObjectURL=()=>{};
 try{const s=new OrbitSpeech();s.toggle();await s.say('travel',false,true,false);assert.equal(calls,0);await s.say('travel',false,true);assert.equal(calls,1);await s.say('travel',false,true,false);assert.equal(calls,1);assert.equal(plays,2);}finally{globalThis.fetch=oldFetch;globalThis.Audio=oldAudio;URL.createObjectURL=oldCreate;URL.revokeObjectURL=oldRevoke;}
});
