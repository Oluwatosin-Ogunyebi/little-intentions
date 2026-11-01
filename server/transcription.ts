import { readUnits } from '../src/usage';
export async function transcribeDetailed(audio:Uint8Array,type:string,key:string,fetcher:typeof fetch=fetch,signal?:AbortSignal):Promise<{text:string;usage:ReturnType<typeof readUnits>}>{
 const clean=type.split(';')[0].toLowerCase();const extensions:Record<string,string>={'audio/webm':'webm','audio/mp4':'mp4','audio/wav':'wav','audio/mpeg':'mp3'};const ext=extensions[clean];if(!ext||audio.byteLength<256||audio.byteLength>8_000_000)throw Error('Unsupported or empty audio');
 const form=new FormData();form.set('model','gpt-transcribe');form.set('file',new Blob([Uint8Array.from(audio)],{type:clean}),`instruction.${ext}`);form.set('prompt','Little Intentions village. Names: Mira, Rowan. Items: tea, cake, flowers.');
 const timeout=AbortSignal.timeout(20000);const response=await fetcher('https://api.openai.com/v1/audio/transcriptions',{method:'POST',headers:{Authorization:`Bearer ${key}`},body:form,signal:signal?AbortSignal.any([signal,timeout]):timeout});if(!response.ok)throw Error('Transcription unavailable');const data=await response.json() as any;if(typeof data.text!=='string'||!data.text.trim()||data.text.length>600)throw Error('No usable transcript');return {text:data.text.trim(),usage:readUnits(data.usage)};
}

export async function transcribe(audio:Uint8Array,type:string,key:string,fetcher:typeof fetch=fetch,signal?:AbortSignal):Promise<string>{return (await transcribeDetailed(audio,type,key,fetcher,signal)).text;}
