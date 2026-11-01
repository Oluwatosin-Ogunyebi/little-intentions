// Records the real desktop UI in clearly labelled practice mode, without narration.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { mkdir } from 'node:fs/promises';
const server=spawn(process.execPath,['node_modules/tsx/dist/cli.mjs','server/index.ts'],{env:{...process.env,PORT:'3016',OPENAI_API_KEY:'',OPENAI_MODEL:'',HTTPS_CERT:'',HTTPS_KEY:''},stdio:'pipe'});
let browser,context;
try{
 await new Promise((resolve,reject)=>{server.stdout.on('data',d=>{if(String(d).includes('server ready'))resolve();});server.on('exit',code=>reject(new Error(`Server exited ${code}`)));setTimeout(()=>reject(new Error('Server startup timeout')),10000).unref();});
 await mkdir('artifacts/demo',{recursive:true});browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--no-proxy-server']});context=await browser.newContext({viewport:{width:1440,height:900},recordVideo:{dir:'artifacts/demo',size:{width:1440,height:900}}});const page=await context.newPage();await page.goto('http://127.0.0.1:3016');await page.waitForTimeout(2500);
 const caption=async text=>page.evaluate(t=>{let el=document.getElementById('demo-caption');if(!el){el=document.createElement('div');el.id='demo-caption';Object.assign(el.style,{position:'fixed',zIndex:'99999',bottom:'18px',left:'50%',transform:'translateX(-50%)',background:'#243e37',color:'white',padding:'12px 22px',borderRadius:'10px',font:'600 16px sans-serif',boxShadow:'0 6px 22px #0003',textAlign:'center',maxWidth:'70%'});document.body.append(el);}el.textContent=t;},text);
 await caption('Little Intentions · a desktop practice-mode demonstration');await page.waitForTimeout(2500);
 await caption('Orbit can ask for the missing details.');await page.fill('#instruction','Please deliver something');await page.click('#send');await page.getByText('Could you tell me which item and who should receive it?').waitFor();await page.waitForTimeout(3000);
 await caption('Review the plan, then watch the actual actions.');await page.fill('#instruction','Take cake to Rowan');await page.click('#send');await page.locator('#approve').waitFor();await page.waitForTimeout(2000);await page.click('#approve');await page.locator('#rewind').waitFor({timeout:25000});await page.waitForTimeout(1800);
 await caption('Rewind the same world and revise the brief.');await page.click('#rewind');await page.fill('#instruction','Take tea to Mira');await page.click('#send');await page.locator('#approve').waitFor();await page.waitForTimeout(1800);await page.click('#approve');await page.locator('#rewind').waitFor({timeout:25000});await page.waitForTimeout(1500);
 await caption('The comparison comes from recorded actions, not a prompt score.');await page.waitForTimeout(5000);await caption('Practice mode is rule-based. Quest and live API require separate verification.');await page.waitForTimeout(4500);
 const video=page.video();await context.close();context=undefined;await video.saveAs('artifacts/demo/little-intentions-desktop.webm');await video.delete();console.log('Recorded artifacts/demo/little-intentions-desktop.webm');
}finally{await context?.close();await browser?.close();server.kill();}
