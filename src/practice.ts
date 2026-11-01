import { type Reply, type Turn } from './mission';
import { type Item, type Recipient, type World, validatePlan } from './simulation';
// Limited guided fallback. It retains the most recently named item and recipient.
export function practicePlan(dialogue:Turn[],world:World):Reply {
 let item:Item|undefined,recipient:Recipient|undefined,unavailable=false;
 for(const turn of dialogue.filter(t=>t.role==='user')){
  const text=turn.content.toLowerCase();
  if(/\bcoffee\b/.test(text)){unavailable=true;item=undefined;}
  const find=(names:string[])=>names.filter(n=>new RegExp(`\\b${n}\\b`,'i').test(text)&&!new RegExp(`\\b(?:not|never|avoid)\\s+${n}\\b`,'i').test(text));
  const foundItems=find(['tea','cake','flowers']),foundPeople=find(['mira','rowan']);
  if(foundItems.length>1||foundPeople.length>1)return {kind:'clarify',message:'Please choose one item and one recipient.',actions:[],revision:world.revision,source:'practice'};
  if(foundItems[0]){item=foundItems[0] as Item;unavailable=false;}if(foundPeople[0])recipient=foundPeople[0] as Recipient;
 }
 if(unavailable)return {kind:'blocked',message:'Coffee is not available at the market. Would you like a different item?',actions:[],revision:world.revision,source:'practice'};
 if(!item||!recipient)return {kind:'clarify',message:`Could you tell me ${!item&&!recipient?'which item and who should receive it':!item?'which item to deliver':'who should receive it'}?`,actions:[],revision:world.revision,source:'practice'};
 const actions:Reply['actions']=[];if(world.location!=='market')actions.push({type:'move_to',target:'market'});actions.push({type:'pick_up',item},{type:'move_to',target:recipient},{type:'deliver',recipient});
 const reply:Reply={kind:'propose',message:`I understood: ${item} to ${recipient[0].toUpperCase()+recipient.slice(1)}.`,revision:world.revision,actions,source:'practice'};
 try{validatePlan(world,reply);return reply;}catch{return {kind:'blocked',message:'I cannot complete that delivery from the current world. Please change the request or rewind.',actions:[],revision:world.revision,source:'practice'};}
}
