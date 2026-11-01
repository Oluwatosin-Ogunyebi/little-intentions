export type Item = 'tea' | 'cake' | 'flowers';
export type Recipient = 'mira' | 'rowan';
export type Action = { type: 'move_to'; target: 'market' | Recipient } | { type: 'pick_up'; item: Item } | { type: 'deliver'; recipient: Recipient };
export type Plan = { message: string; actions: Action[]; revision: number };
export type Place = 'market' | Recipient;
export type World = { revision: number; location: Place; inventory: Item | null; items: Record<Item, 'market' | Recipient | 'carried'>; blockedEdges: string[]; events: string[] };
export const initialWorld = (): World => ({ revision: 0, location: 'market', inventory: null, items: { tea: 'market', cake: 'market', flowers: 'market' }, blockedEdges: [], events: [] });
const items = ['tea', 'cake', 'flowers'];
const recipients = ['mira', 'rowan'];
type Node = Place | 'crossroads';
const graph: Record<Node,Node[]> = {market:['crossroads'],crossroads:['market','mira','rowan'],mira:['crossroads'],rowan:['crossroads']};
export function routeBetween(from: Place, to: Place, blocked: string[] = []): Node[] {
  if (!graph[from] || !graph[to]) throw new Error('Unknown destination');
  const queue: Node[][] = [[from]], seen = new Set<Node>([from]);
  while(queue.length){const path=queue.shift()!, at=path[path.length-1];if(at===to)return path.slice(1);for(const next of graph[at]){const edge=[at,next].sort().join(':');if(!blocked.includes(edge)&&!seen.has(next)){seen.add(next);queue.push([...path,next]);}}}
  throw new Error('That route is blocked');
}
// Validate a whole plan on a private copy before committing any action.
export function applyAction(world: World, action: Action): World {
  const w = structuredClone(world);
  if (!action || typeof action !== 'object') throw new Error('Invalid action');
  if (action.type === 'move_to') {
    if (!['market', ...recipients].includes(action.target)) throw new Error('Unknown destination');
    routeBetween(w.location, action.target, w.blockedEdges);
    w.location = action.target; w.events.push(`Orbit walked to ${action.target}.`);
  } else if (action.type === 'pick_up') {
    if (!items.includes(action.item) || w.location !== 'market' || w.inventory || w.items[action.item] !== 'market') throw new Error('Cannot pick up that item');
    w.inventory = action.item; w.items[action.item] = 'carried'; w.events.push(`Orbit picked up ${action.item}.`);
  } else if (action.type === 'deliver') {
    if (!recipients.includes(action.recipient) || w.location !== action.recipient || !w.inventory) throw new Error('Cannot deliver here');
    const item = w.inventory; w.items[item] = action.recipient; w.inventory = null; w.events.push(`Orbit delivered ${item} to ${action.recipient}.`);
  } else throw new Error('Unknown action');
  w.revision++; return w;
}
export function validatePlan(world: World, plan: Plan): World {
  if (!plan || typeof plan.message !== 'string' || plan.message.length > 600 || plan.revision !== world.revision || !Array.isArray(plan.actions) || plan.actions.length > 6) throw new Error('This plan is invalid or out of date.');
  return plan.actions.reduce(applyAction, structuredClone(world));
}
export function offlinePlan(instruction: string, world: World): Plan {
  const text = instruction.toLowerCase();
  const mentionedItems = items.filter(x => new RegExp(`\\b${x}\\b`).test(text));
  const mentionedRecipients = recipients.filter(x => new RegExp(`\\b${x}\\b`).test(text));
  if (mentionedItems.length > 1 || mentionedRecipients.length > 1 || /\b(not|never|avoid|except|don't|do not|instead|without)\b/.test(text)) return { revision: world.revision, message: 'In practice mode, please name one item and one recipient in a simple delivery request.', actions: [] };
  const item = mentionedItems[0] as Item | undefined;
  const recipient = mentionedRecipients[0] as Recipient | undefined;
  if (!item || !recipient) return { revision: world.revision, message: `Could you tell me ${!item && !recipient ? 'which item and who should receive it' : !item ? 'which item to deliver' : 'who should receive it'}?`, actions: [] };
  const actions: Action[] = [];
  if (world.location !== 'market') actions.push({ type: 'move_to', target: 'market' });
  actions.push({ type: 'pick_up', item }, { type: 'move_to', target: recipient }, { type: 'deliver', recipient });
  return { revision: world.revision, message: `I'll take the ${item} from the market to ${recipient[0].toUpperCase() + recipient.slice(1)}.`, actions };
}
export function outcome(w: World): boolean { return w.items.tea === 'mira'; }
