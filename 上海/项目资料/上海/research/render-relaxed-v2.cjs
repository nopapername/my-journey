const fs = require('node:fs');
const path = require('node:path');
const {createCanvas,loadImage} = require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@napi-rs/canvas');
const root=path.resolve(__dirname,'../武康路轻松版');
(async()=>{
  const files=[path.join(root,'00-全程地理路线.svg'),...fs.readdirSync(path.join(root,'每日地图')).filter(x=>x.endsWith('.svg')).map(x=>path.join(root,'每日地图',x))];
  for(const file of files){const canvas=createCanvas(1600,1050);const ctx=canvas.getContext('2d');const image=await loadImage(fs.readFileSync(file));ctx.drawImage(image,0,0);fs.writeFileSync(file.replace(/\.svg$/,'.png'),canvas.toBuffer('image/png'));}
  console.log(JSON.stringify({pngCount:files.length}));
})().catch(e=>{console.error(e);process.exitCode=1;});
