import fs from 'node:fs/promises';
import { Presentation, PresentationFile } from '@oai/artifact-tool';
const p = Presentation.create({slideSize:{width:1280,height:720}});
const s=p.slides.add();s.background.fill='#FAF7EF';
const sh=s.shapes.add({geometry:'textbox',position:{left:60,top:50,width:1000,height:100},fill:'none',line:{fill:'none',width:0}});
sh.text='上海十月旅行';sh.text.style={fontSize:56,typeface:'Microsoft YaHei',color:'#183A33',bold:true,insets:0,autoFit:'none'};
const t=s.tables.add({rows:3,columns:2,left:60,top:250,width:1000,height:220,values:[['日期','目的地'],['D1','市区酒店'],['D2','豫园与外滩']]});
t.cells.block({row:0,column:0,rowCount:3,columnCount:2}).assign({textStyle:{fontSize:26,typeface:'Microsoft YaHei',color:'#183A33'},margins:{left:12,right:12,top:12,bottom:12},anchor:'center'});
for(let i=0;i<3;i++){t.rows[i].height=i===0?60:80;for(let j=0;j<2;j++){t.getCell(i,j).fill=i===0?'#DCE8DE':'#FAF7EF'}}
t.borders.assign({fill:'#C6D4C9',width:1,style:'solid'});
await fs.writeFile('smoke.png',new Uint8Array(await (await p.export({slide:s,format:'png',scale:1})).arrayBuffer()));
await (await PresentationFile.exportPptx(p)).save('smoke.pptx');
console.log('rendered');
