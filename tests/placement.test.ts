import { test } from 'node:test';
import assert from 'node:assert/strict';
import { easeFactor, scaleFromStick } from '../src/placement';
test('easing has the same result at different frame rates',()=>{const step=(n:number)=>{let value=0;for(let i=0;i<n;i++)value+=(1-value)*easeFactor(1.5,1/n);return value;};assert.ok(Math.abs(step(30)-step(90))<1e-12);assert.ok(step(90)<1);});
test('thumbstick dead zone, direction and size limits',()=>{assert.equal(scaleFromStick(.75,.1,1),.75);assert.ok(scaleFromStick(.75,-1,1)>.75);assert.ok(scaleFromStick(.75,1,1)<.75);assert.equal(scaleFromStick(1.3,-1,2),1.3);assert.equal(scaleFromStick(.35,1,2),.35);});
