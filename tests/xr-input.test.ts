import {test} from 'node:test';
import assert from 'node:assert/strict';
import {dispatchSelection} from '../src/xr-input';
test('panel buttons and blank panel hits never relocate the world',()=>{let actions=0,placements=0;const place=()=>placements++;assert.equal(dispatchSelection({button:{run:()=>actions++}},true,place),'button');assert.equal(dispatchSelection({button:{enabled:false,run:()=>actions++}},true,place),'panel');assert.equal(dispatchSelection({},true,place),'panel');assert.equal(actions,1);assert.equal(placements,0);});
test('only empty space in Place mode relocates the world',()=>{let placements=0;const place=()=>placements++;assert.equal(dispatchSelection(null,false,place),'none');assert.equal(dispatchSelection(null,true,place),'place');assert.equal(placements,1);});
