import fs from 'node:fs/promises';
import path from 'node:path';
import { PresentationFile, FileBlob } from '@oai/artifact-tool';
const build='D:/web3/code_project/旅游规划/上海/research/ppt-build';
const file='D:/web3/code_project/旅游规划/上海/PPT/上海10月下旬轻松旅行攻略（完整版）.pptx';
const p=await PresentationFile.importPptx(await FileBlob.load(file));
const output=path.join(build,'final-renders');
await fs.mkdir(output,{recursive:true});
for(const [i,s] of p.slides.items.entries()){
 await fs.writeFile(path.join(output,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await (await p.export({slide:s,format:'png',scale:1})).arrayBuffer()));
}
console.log(JSON.stringify({file,slides:p.slides.items.length,size:(await fs.stat(file)).size}));
