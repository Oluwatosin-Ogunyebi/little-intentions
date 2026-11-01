import {type Attempt} from './mission';
export type AttemptSummary={brief:string;question:string|null;answer:string|null;result:string;success:boolean};
/** Derive displayed evidence only from the recorded dialogue and actions. */
export function summarizeAttempt(attempt:Attempt):AttemptSummary{
 const brief=attempt.dialogue.find(t=>t.role==='user')?.content||'No brief recorded';
 const i=attempt.dialogue.findIndex(t=>t.role==='assistant'&&t.kind==='clarify');
 const question=i>=0?attempt.dialogue[i].content:null;
 const answer=i>=0?attempt.dialogue.slice(i+1).find(t=>t.role==='user')?.content||null:null;
 return {brief,question,answer,result:attempt.events.at(-1)||'No delivery recorded.',success:attempt.success};
}
