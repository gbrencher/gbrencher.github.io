const fs = require('fs'), vm = require('vm'), assert = require('assert');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.style={};this.classList={add(){}};this.handlers={};}
 append(...nodes){this.children.push(...nodes)}
 replaceChildren(...nodes){this.children=nodes}
 setAttribute(k,v){this[k]=v}
 addEventListener(k,v){this.handlers[k]=v}
 focus(){}
 querySelector(s){return walk(this).find(n=>'.'+n.className===s)}
}
function walk(n){return [n,...n.children.flatMap(walk)]}
const data=JSON.parse(fs.readFileSync('dist/assets/snow/latest.json'));
async function check(available){
 const figure=new Element('figure');
 const sandbox={console,Image:class extends Element{constructor(){super('img')}async decode(){}},document:{createElement:t=>new Element(t),querySelector:()=>figure},fetch:async url=>({ok:!url.includes('april')||available,json:async()=>({...data,target_date:url.includes('april')?'2026-04-01':data.target_date})})};
 await vm.runInNewContext(fs.readFileSync('dist/snow.js','utf8'),sandbox);
 assert(walk(figure).some(n=>n.tag==='time'&&n.dateTime===data.target_date));
 let toggle=figure.querySelector('.snow-toggle');
 if(!available){assert(!toggle);return}
 assert.equal(toggle.textContent,'See previous April 1 snow depth');toggle.handlers.click();
 assert(walk(figure).some(n=>n.tag==='time'&&n.dateTime==='2026-04-01'));
 assert(walk(figure).some(n=>n.tag==='img'&&n.src.includes('april-2026')));
 toggle=figure.querySelector('.snow-toggle');assert.equal(toggle.textContent,'See latest snow depth');toggle.handlers.click();
 assert(walk(figure).some(n=>n.tag==='time'&&n.dateTime===data.target_date));
}
(async()=>{await check(true);await check(false);console.log('Map toggle and missing archive checks passed')})().catch(e=>{console.error(e);process.exit(1)});
