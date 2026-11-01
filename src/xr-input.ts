export type PanelHit={button?:{enabled?:boolean;run:()=>void}}|null;
/** Panel hits are always consumed; only empty-space selections in Place mode move the world. */
export function dispatchSelection(hit:PanelHit,placing:boolean,place:()=>void):'button'|'panel'|'place'|'none'{
 if(hit){if(hit.button&&hit.button.enabled!==false){hit.button.run();return 'button';}return 'panel';}
 if(placing){place();return 'place';}return 'none';
}
