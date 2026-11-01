import express from 'express';
import 'dotenv/config';
import { createServer } from 'node:https';
import { readFileSync } from 'node:fs';
import { type World } from '../src/simulation';
import { planFor } from './planner';
import { transcribeDetailed } from './transcription';

const app=express(); app.use(express.json({limit:'8kb'}));
function validWorld(w:any): w is World {
 const places=['market','mira','rowan'], items=['tea','cake','flowers'];
 return !!w && Number.isSafeInteger(w.revision) && w.revision>=0 && places.includes(w.location) && (w.inventory===null||items.includes(w.inventory)) && !!w.items && items.every(i=>[...places,'carried'].includes(w.items[i])) && Array.isArray(w.blockedEdges) && w.blockedEdges.length<=3 && w.blockedEdges.every((e:unknown)=>typeof e==='string' && ['crossroads:market','crossroads:mira','crossroads:rowan'].includes(e)) && Array.isArray(w.events) && w.events.length<=100 && w.events.every((e:unknown)=>typeof e==='string' && e.length<=200);
}
app.post('/api/plan',async(req,res)=>{
 const dialogue=req.body?.dialogue ?? (typeof req.body?.instruction==='string'?[{role:'user',content:req.body.instruction}]:null); const world=req.body?.world as World;
 if(!Array.isArray(dialogue)||!dialogue.length||dialogue.length>12||dialogue.some((t:any)=>!t||!['user','assistant'].includes(t.role)||typeof t.content!=='string'||!t.content.trim()||t.content.length>600)||!validWorld(world)){res.status(400).json({error:'Invalid request'});return;}
 const attemptId=typeof req.body?.attemptId==='string'&&/^[0-9a-f-]{36}$/i.test(req.body.attemptId)?req.body.attemptId:null;const requestId=typeof req.body?.requestId==='string'&&/^[0-9a-f-]{36}$/i.test(req.body.requestId)?req.body.requestId:null;const pending=new AbortController();req.once('aborted',()=>pending.abort());res.once('close',()=>{if(!res.writableEnded)pending.abort();});const result=await planFor(dialogue,world,{key:process.env.OPENAI_API_KEY,model:process.env.OPENAI_MODEL,signal:pending.signal});if(!pending.signal.aborted)res.json({...result,attemptId,requestId});
});
app.get('/api/status',(_req,res)=>res.json({configured:!!(process.env.OPENAI_API_KEY&&process.env.OPENAI_MODEL)}));
app.post('/api/speech',async(req,res)=>{const text=req.body?.text;const key=process.env.OPENAI_API_KEY;if(typeof text!=='string'||!text.trim()||text.length>600){res.status(400).json({error:'Invalid speech text'});return;}if(!key){res.status(503).json({error:'Speech unavailable'});return;}const pending=new AbortController();res.once('close',()=>{if(!res.writableEnded)pending.abort();});try{const response=await fetch('https://api.openai.com/v1/audio/speech',{method:'POST',headers:{Authorization:`Bearer ${key}`,'Content-Type':'application/json'},body:JSON.stringify({model:'gpt-4o-mini-tts',voice:'coral',instructions:'Speak as a warm, gently playful and curious little companion. Use a soft, cozy tone, clear natural pacing, and pronounce names carefully. Keep every word exactly as given.',input:text}),signal:AbortSignal.any([pending.signal,AbortSignal.timeout(12000)])});if(!response.ok)throw Error('Speech unavailable');const audio=Buffer.from(await response.arrayBuffer());if(!pending.signal.aborted)res.type('audio/mpeg').send(audio);}catch{if(!pending.signal.aborted)res.status(502).json({error:'Speech unavailable'});}});
app.post('/api/transcribe',express.raw({type:'audio/*',limit:'8mb'}),async(req,res)=>{const key=process.env.OPENAI_API_KEY;if(!key){res.status(503).json({error:'Transcription is not configured.'});return;}if(!Buffer.isBuffer(req.body)){res.status(400).json({error:'Audio was not received.'});return;}const pending=new AbortController();req.once('aborted',()=>pending.abort());res.once('close',()=>{if(!res.writableEnded)pending.abort();});try{const result=await transcribeDetailed(req.body,req.get('content-type')||'',key,fetch,pending.signal);if(!pending.signal.aborted)res.json({...result,model:'gpt-transcribe'});}catch{if(!pending.signal.aborted)res.status(502).json({error:'Could not transcribe the recording. Try again or use the guided buttons.'});}});
app.use(express.static('dist')); app.get('/{*path}',(_req,res)=>res.sendFile('index.html',{root:'dist'}));
const port=Number(process.env.PORT)||3001;
const host=process.env.HOST||'0.0.0.0';
const cert=process.env.HTTPS_CERT, key=process.env.HTTPS_KEY;
if(Boolean(cert)!==Boolean(key))throw new Error('Set both HTTPS_CERT and HTTPS_KEY, or neither.');
if(cert&&key)createServer({cert:readFileSync(cert),key:readFileSync(key)},app).listen(port,host,()=>console.log('Little Intentions HTTPS server ready'));
else app.listen(port,host,()=>console.log('Little Intentions server ready'));
