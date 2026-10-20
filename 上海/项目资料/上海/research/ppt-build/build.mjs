import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const ROOT='D:/web3/code_project/旅游规划/上海';
const BUILD=path.join(ROOT,'research/ppt-build');
const SKILL='C:/Users/Administrator/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
const RUNTIME='C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=path.join(RUNTIME,'node/node_modules');
process.env.RUNTIME_NODE=path.join(RUNTIME,'node/bin/node.exe');
const FONT='Microsoft YaHei';
const C={bg:'#FAF7EF',ink:'#183A33',green:'#24745E',muted:'#587066',line:'#C4D3C9',light:'#E1EBE3',gold:'#B97B38',white:'#FFFFFF'};
const p=Presentation.create({slideSize:{width:1280,height:720}});
const md=await fs.readFile(path.join(ROOT,'上海10月下旬轻松旅行攻略.md'),'utf8');
const sources=await fs.readFile(path.join(ROOT,'攻略来源索引.md'),'utf8');
const xhs=JSON.parse(await fs.readFile(path.join(ROOT,'research/xhs-reviewed.json'),'utf8'));
const URL={
 disney:'https://www.shanghaidisneyresort.com/zh-cn/',
 tickets:'https://www.shanghaidisneyresort.com/zh-cn/commerce/product?id=ThemePark',
 rules:'https://www.shanghaidisneyresort.com/zh-cn/legal/park-rules/',
 metro:'https://www.shmetro.com/',
 bund:'https://goasia.cc/cn/article/the-bund-shanghai',
 french:'https://www.chinahighlights.com/shanghai/attraction/french-concession.htm',
 lu:'https://www.travelchinaguide.com/attraction/shanghai/lujiazui.htm',
 yu:'https://www.chinahighlights.com/shanghai/attraction/yuyuan-garden.htm',
 nan:'https://www.travelchinaguide.com/attraction/shanghai/nanjing_road.htm',
 X:n=>'https://www.xiaohongshu.com/explore/'+({2:'69eb7365000000003502b572',3:'6aabd8480000000026014835',4:'6a90107e000000001f005d77',5:'696cd4ab000000000a029ccf',6:'6ac62f1b000000001800788e',7:'6a05df83000000003601d7ca',8:'6abd23a30000000001008123',9:'6a3d11cf0000000007024595',10:'69fed3b00000000037034cd9'}[n])
};
const amap=q=>'https://uri.amap.com/search?keyword='+encodeURIComponent(q)+'&city='+encodeURIComponent('上海')+'&view=map';
function txt(s,text,x,y,w,h,size=25,color=C.ink,bold=false){
 const sh=s.shapes.add({geometry:'textbox',name:text.slice(0,32),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=text;sh.text.style={fontSize:size,typeface:FONT,color,bold,insets:0,autoFit:'none',wrap:'square',verticalAlignment:'top'};return sh;
}
function link(s,text,url,x,y,w=1000,size=23){const sh=txt(s,text,x,y,w,42,size,C.green);sh.text.get(text).link={uri:url,isExternal:true};sh.text.get(text).underline='sng';return sh;}
function line(s,x,y,w){s.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:0},fill:'none',line:{fill:C.line,width:1}});}
function slide(title,sub='',dark=false){const s=p.slides.add();s.background.fill=dark?C.ink:C.bg;const col=dark?C.bg:C.ink;txt(s,title,64,44,1152,70,43,col,true);if(sub)txt(s,sub,66,122,1148,55,24,dark?'#CADCCF':C.muted);txt(s,String(p.slides.items.length),1190,678,40,24,16,dark?'#CADCCF':C.muted);return s;}
function note(s,section,urls=[]){
 let excerpt='';if(section){const a=md.indexOf(section);if(a>=0){let end=md.indexOf('\n## ',a+section.length);if(section.startsWith('### ')){let b=md.indexOf('\n### ',a+section.length);if(b>=0&&(end<0||b<end))end=b;}excerpt=md.slice(a,end<0?md.length:end);}}
 s.speakerNotes.text='资料审读：2026-10-13。示例日期：2026-10-23至29，可整体平移。\n'+excerpt+'\n\n依据：\n'+urls.join('\n');
}
function foot(s,text){txt(s,text,66,623,1148,44,21,C.muted);}
function block(s,title,body,x,y,w=530){txt(s,title,x,y,w,48,30,C.green,true);txt(s,body,x,y+61,w,188,25,C.ink);}
function table(s,values,widths,x=64,y=210,rowH=67,size=25){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:widths.reduce((a,b)=>a+b,0),height:rowH*values.length,columnWidths:widths,values});
 t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({textStyle:{fontSize:size,typeface:FONT,color:C.ink},margins:{left:13,right:13,top:11,bottom:9},anchor:'center'});
 for(let r=0;r<values.length;r++){t.rows[r].height=r===0?rowH-7:rowH;for(let c=0;c<values[0].length;c++){const ce=t.getCell(r,c);ce.fill=r===0?C.light:C.bg;if(r===0)ce.text.style={fontSize:size,typeface:FONT,color:C.ink,bold:true};}}
 t.borders.assign({fill:C.line,width:0.8,style:'solid'});return t;
}
function route(s,nodes,labels,y=254){
 const n=nodes.length,gap=38,total=1150,w=(total-gap*(n-1))/n;const shapes=[];
 nodes.forEach((v,i)=>{const x=65+i*(w+gap);txt(s,String(i+1).padStart(2,'0'),x,y-55,w,42,30,C.gold,true);const a=txt(s,v.title,x,y,w,88,29,C.green,true);shapes.push(a);txt(s,v.body,x,y+124,w,164,24,C.ink);if(v.url)link(s,'地图搜索',v.url,x,y+305,w,21);});
 for(let i=0;i<n-1;i++){s.shapes.connect(shapes[i],shapes[i+1],{kind:'straight',fromSide:'right',toSide:'left',line:{fill:C.green,width:2},tail:{type:'arrow',width:'sm',length:'sm'}});if(labels?.[i]){const sh=txt(s,labels[i],65+(i+1)*(w+gap)-gap-27,y+78,gap+54,36,18,C.muted);sh.text.alignment='center';}}
 foot(s,'路线为非比例顺序示意，真实步行入口与交通以地图 App／现场为准。');
}

// 01 封面
{
 const s=p.slides.add();s.background.fill=C.ink;
 txt(s,'上海',70,108,900,130,92,C.bg,true);
 txt(s,'十月下旬轻松旅行',73,267,1080,95,53,C.bg,true);
 txt(s,'成都出发，两人同行',76,401,1000,48,29,'#D6E5D9');
 txt(s,'7 天主方案，8 天可玩两日迪士尼',76,464,1080,58,29,'#D6E5D9');
 txt(s,'示例日期 2026.10.23–10.29',76,593,1000,35,22,'#BFD1C5');
 note(s,'## 一、先看行程与路线总览',[URL.disney]);
}
// 02
{
 const s=slide('两段住宿，一次搬家','每天一个主要街区，通常 10 点左右出门，迪士尼日单独调整');
 txt(s,'A  市区连住 4 晚',65,221,535,59,40,C.green,true);
 txt(s,'10/23 入住，10/27 退房\n大世界／老西门优先\n地标、街区购物与上海小吃',67,310,530,170,29);
 txt(s,'B  乐园周边 2–3 晚',684,221,535,59,40,C.green,true);
 txt(s,'7 天版：10/27 入住，10/29 退房\n8 天版：延长至 10/30 退房\n康新公路／秀沿路近 11 号线',686,310,530,170,29);
 txt(s,'D5 下午转场',68,536,1144,50,32,C.gold,true);
 foot(s,'午后安排 45–90 分钟休息，购物和小吃按体力删减。');note(s,'## 二、住哪里最方便',[URL.X(2),URL.metro]);
}
// 03
{
 const s=slide('7 天行程总览','示例 10/23 出发，实际日期可整体平移');
 table(s,[['日期','当天重点','住哪里'],['D1  10/23 周五','抵达上海，酒店附近吃饭','A'],['D2  10/24 周六','豫园、外滩黄昏、南京东路','A'],['D3  10/25 周日','武康路、安福路与买手店','A'],['D4  10/26 周一','陆家嘴商场、三件套外观、滨江','A'],['D5  10/27 周二','淮海／新天地短逛，取行李转场','B'],['D6  10/28 周三','迪士尼 3 个目标，加看秀和午休','B'],['D7  10/29 周四','睡醒后返程','无']],[252,720,180],64,185,53,24);
 txt(s,'8 天版：D7 再入园，D8 返程。D5 仍是唯一搬酒店日。',66,646,1100,28,21,C.muted);note(s,'## 一、先看行程与路线总览');
}
// 04
{
 const s=slide('市区 A：大世界／老西门优先','先筛 300–450 元／间／晚，再看整段 4 晚总价');
 block(s,'大世界站附近','8、14 号线\n去豫园、陆家嘴、淮海路方便\n适合把老城与市区购物放在前半程',66,213);
 block(s,'老西门站附近','8、10 号线\n10 号线接武康路入口交通大学站\n虹桥抵达时交通便利',681,213);
 txt(s,'筛选条件',66,492,240,43,30,C.green,true);
 txt(s,'地铁口实际步行尽量 600 米内，有外窗、电梯、独立卫浴。\n看近月卫生与隔音差评，确认取消条件和退房后寄存。',66,548,1138,75,25);
 foot(s,'预算外再扩大至豫园／陆家浜路。白玉兰南京东路外滩店仅作比较候选，实时房价未核。');
 note(s,'### 市区 A：首选大世界／老西门，其次豫园／陆家浜路',[URL.X(2),URL.metro]);
}
// 05
{
 const s=slide('乐园 B：近 11 号线更自主','筛选目标 250–400 元／间／晚，连续住 2 晚或 3 晚');
 table(s,[['比较顺序','优点','必须确认'],['康新公路／秀沿路','11 号线直达迪士尼','酒店到地铁口实走距离'],['御桥附近','11／18 号线\n去乐园可乘 11 号线','完整分店位置与近月评价'],['川沙，接驳已落实','吃饭选择多，班车可省换乘','最早去程、夜间回程、收费、预约']],[330,352,470],64,200,80,25);
 txt(s,'川沙是 2 号线，迪士尼是 11 号线',65,550,1140,50,32,C.gold,true);
 foot(s,'酒店名含“迪士尼店”不代表位于乐园门口。如家御桥店仍须定位准确分店。');note(s,'### 迪士尼周边 B：近 11 号线优先，可靠接驳作备选',[URL.X(2),URL.metro]);
}
// 06
{
 const s=slide('D1 抵达：入住后在附近吃饭','成都 TFU／CTU，上海 SHA／PVG，比较含行李的往返总价');
 block(s,'虹桥抵达','10 号线到老西门／豫园\n住大世界可在老西门换 8 号线\n取行李后门到门预留 60–90 分钟',66,214);
 block(s,'浦东抵达','2 号线到陆家嘴，换 14 号线\n到豫园／大世界，再走到酒店\n取行李后门到门预留 90–120 分钟',681,214);
 txt(s,'附近晚餐',66,507,400,42,30,C.green,true);
 txt(s,'生煎配牛肉粉丝汤，或本帮小馆。大世界可搜云南南路。\n晚到或行李较多时，比较两人网约车费用，抵达日保留休息。',66,560,1140,80,26);
 note(s,'### D1｜成都到上海：入住后只在附近吃饭',[URL.metro]);
}
// 07
{
 const s=slide('D2 老城、外滩与南京东路','周六热门区域人多，园林／商城以一个为主');
 route(s,[{title:'豫园片区',body:'10:00–13:00\n园林或商城\n小笼／生煎午餐',url:amap('豫园')},{title:'A 休息',body:'13:30–15:30\n回酒店午休\n或就近坐 45–60 分钟'},{title:'外滩黄昏',body:'16:00–18:00\n南京东路站向东\n建筑与江边短段',url:amap('外滩')},{title:'南京东路',body:'18:00–20:00\n从江边向西夜逛\n吃晚饭、买少量糕团',url:amap('沈大成南京东路')}],['地铁','地铁','步行']);
 note(s,'### D2｜老城＋外滩＋南京东路：经典上海',[URL.bund,URL.nan,URL.yu,URL.X(2),URL.X(10)]);
}
// 08
{
 const s=slide('D2 吃喝：两家午餐二选一','所有金额为两人预留预算，具体菜单和营业以当天为准');
 table(s,[['店铺检索词','点单建议','两人预留'],['南翔馒头店 豫园','鲜肉小笼，一笼分享后再加','80–160 元'],['大壶春 豫园店','生煎配汤，替换小笼午餐','50–90 元'],['沈大成 南京东路','条头糕／双酿团，少量现买','20–50 元'],['裕莲茶楼 豫园','琥珀奶茶，蛋挞共享可选','40–90 元']],[355,567,230],64,199,72,26);
 link(s,'南翔地图',amap('南翔馒头店豫园'),66,571,250,23);link(s,'大壶春地图',amap('大壶春豫园店'),357,571,270,23);link(s,'裕莲茶楼地图',amap('裕莲茶楼豫园'),708,571,420,23);
 foot(s,'排队超过约 30 分钟就换店。裕莲是单篇候选，饮品与点心不要求全部尝完。');note(s,'### 小红书餐饮店单：按区域安排，选够一顿就停',[URL.X(2),URL.X(10),URL.yu,URL.nan]);
}
// 09
{
 const s=slide('D3 武康路与安福路慢逛','从武康路南端进入，向北接安福路，再向东逛');
 route(s,[{title:'交通大学站',body:'10:30 左右到达\n10 号线\n步行 10–20 分钟'},{title:'武康大楼',body:'街拍后沿武康路北行\n梧桐、洋房与街景\n午餐在邻近街区',url:amap('武康大楼')},{title:'安福路东行',body:'13:15–16:30\n三家重点选两家\n店址与预约见下一页',url:amap('in the PARK安福路322号')},{title:'乌中休息',body:'坐 45–60 分钟\n比较常熟路／图书馆站\n疲劳就打车回 A',url:amap('乌鲁木齐中路')}],['步行','步行','步行']);
 note(s,'### D3｜武康路＋安福路：买手店与奶茶慢逛',[URL.french,URL.X(3),URL.X(4),URL.X(5),URL.X(6)]);
}
// 10
{
 const s=slide('安福路买手店：重点选两家','按安福路向东慢逛，给购物与试穿留 2–3 小时');
 table(s,[['门店','笔记地址','逛什么／确认事项'],['in the PARK','安福路 322 号，6 号楼 1 楼','服装与生活方式，核入口'],['RONIN MADE Lounge','安福路 275 号 5 弄 1 楼','银饰配饰，提前预约'],['CSYSeLECTED','安福路 234 号 2 楼','成衣配饰，核当天营业']],[340,438,374],64,209,86,24);
 link(s,'in the PARK 地图',amap('in the PARK安福路322号'),66,570,350,23);link(s,'RML 地图',amap('RONIN MADE安福路275号5弄'),450,570,260,23);link(s,'CSY 地图',amap('CSYSeLECTED安福路234号'),783,570,300,23);
 foot(s,'“6 号楼 1 楼”请准确保存。地址已读，实时在营待核。RML 预约造成折返就略过。');note(s,'### 购物：把街区当主目的，具体门店作停靠点',[URL.X(3),URL.X(4),URL.X(5),URL.X(6)]);
}
// 11
{
 const s=slide('D4 陆家嘴：一个商场加滨江','默认地面慢游，全天步行规划约 2–4 公里');
 route(s,[{title:'陆家嘴站',body:'10:30 前后到达\n大世界／豫园乘 14\n老西门经豫园换乘'},{title:'商场择一',body:'国金中心或正大广场\n午餐后坐下休息\n不必两个都逛',url:amap('正大广场')},{title:'三件套外观',body:'上海中心、金茂\n环球金融中心\n沿人行与过街设施',url:amap('上海中心大厦')},{title:'浦东滨江',body:'15:30–18:00\n看浦西外滩\n地铁回 A',url:amap('陆家嘴滨江大道')}],['步行','步行','步行']);
 note(s,'### D4｜陆家嘴：商场、摩天楼与滨江',[URL.lu,URL.metro]);
}
// 12
{
 const s=slide('D5 短逛后二次入住','上午退房寄存，14 点左右回 A 取行李，下午转场到 B');
 block(s,'淮海东侧／新天地主线','一大会址·黄陂南路附近\n一个商场加新天地北里\nALTER：马当路 245 号，新天地 L116',66,222);
 block(s,'富民／长乐／巨鹿替换线','常熟路附近，只走一小段\n慢逛 1.5–2 小时后回 A\nLABELHOOD：富民路 184 号',681,222);
 link(s,'ALTER 地图',amap('ALTER马当路245号'),66,517,450);link(s,'蕾虎地图',amap('LABELHOOD富民路184号'),681,517,450);
 foot(s,'两条线二选一。味香斋／光明邨只在淮海西侧替换线顺路安排。门店地址仍需核在营。');note(s,'### D5｜淮海中路＋新天地：短逛后搬一次酒店',[URL.X(3),URL.X(2)]);
}
// 13
{
 const s=slide('唯一转场：A 取行李后去 B','两人带箱子，先比较网约车。门到门预留 60–120 分钟');
 route(s,[{title:'A 取行李',body:'先确认寄存和退房\n向 B 核入住时间\n避免拖箱逛街'},{title:'东方体育中心',body:'近大世界／老西门\n陆家浜路乘 8 号线\n在此换 11 号线'},{title:'B 对应车站',body:'秀沿路／康新公路\n御桥作备选\n最后一段按酒店导航'},{title:'入住休息',body:'附近吃饭、整理小包\n确认次日交通\n晚间尽早休息'}],['8 号线','11 号线','步行／车']);
 note(s,'### D5｜淮海中路＋新天地：短逛后搬一次酒店',[URL.metro]);
}
// 14
{
 const s=slide('迪士尼票务与日期选择','示例 10/28 周三入园，日期和在售产品以官方实际条件为准');
 txt(s,'1 天：7 天版\n2 天：8 天版',66,224,515,136,42,C.green,true);
 txt(s,'提前核对入园证件、有效期、退改。\nT₁ 为单人实际一日票费。\nT₂ 为单人满足两天入园的全部票费。',66,395,515,145,25);
 txt(s,'早鸟是提前购票优惠',681,224,530,48,32,C.gold,true);
 txt(s,'官方 10/13 列表：早鸟一日 449 元起，\n早鸟二日 798 元起。常规一日／二日\n列表均显示 475 元起，需进入产品核对。\n起价不能代替 10/28 指定日成交价。',681,296,530,192,25);
 txt(s,'早享是提前入园产品，需另看条件',681,520,530,72,28,C.green,true);
 foot(s,'早鸟列表写提前 10 天购票。10/28 入园可尽早在 10/18 前核条件，周三也不保证人少。');
 link(s,'官方门票产品',URL.tickets,66,569,430);note(s,'### 购票、证件与入园',[URL.tickets,URL.disney]);
}
// 15
{
 const s=slide('乐园随身小包与禁带物','据 2026-10-13 已读的官方游客须知，出发前仍需查看更新');
 block(s,'小包建议','证件、手机、充电宝、雨具\n本人食用的常温食品／饮料\n轻便好走的鞋，必要常用药',66,220);
 block(s,'官方限制','禁需加热、加工、冷藏、保温及强气味食品\n禁酒、罐装及玻璃容器\n禁三脚架、伸缩自拍／稳定器、折叠椅凳',681,220);
 txt(s,'箱包：超过 56 × 36 × 23 厘米不允许',66,520,1140,49,32,C.gold,true);
 foot(s,'任何带轮行李箱也不允许。充电宝另按航司／机场当前携带规定确认。');link(s,'官方游客须知',URL.rules,66,574,600);note(s,'### 官方携带规则补充',[URL.rules]);
}
// 16
{
 const s=slide('D6 迪士尼一日：东侧区域为主','3 个主要目标，加看秀与午间休息。小路按官方地图和现场通行');
 route(s,[{title:'探险岛',body:'翱翔·飞越地平线\n排队过长先看邻近秀\n开场以官方 App 为准'},{title:'宝藏湾',body:'加勒比海盗\n沉落宝藏之战\n在所在区域吃午饭'},{title:'疯狂动物城',body:'热力追踪与街景\n结合即时排队安排\n热度高时灵活调整'},{title:'休息与演出',body:'午休 60–90 分钟\n城堡／园景拍照\n夜秀按当日安排'}],['分区步行','分区步行','步行']);
 note(s,'### 1 天：东侧三个目标＋看秀＋午休',[URL.disney,URL.rules]);
}
// 17
{
 const s=slide('8 天版：第二天西侧与中部','D7 降低强度，补最想玩的体验，D8 再返程');
 route(s,[{title:'明日世界',body:'创极速光轮\n喜欢刺激者重点选\n物品按现场寄存要求'},{title:'梦幻世界',body:'矿山车／小飞侠等\n挑一个感兴趣项目\n不必把项目刷齐'},{title:'玩具总动员',body:'邻近小项目可选\n或删掉一段休息\n用 App 查看状态'},{title:'中心与购物',body:'角色合照、拍照\n下午再买周边\n避免一路抱着大件'}],['分区步行','分区步行','步行']);
 note(s,'### 2 天：D6 东侧区域，D7 西侧与中部',[URL.disney]);
}
// 18
{
 const s=slide('迪士尼现场节奏与餐饮','60 分钟排队上限是舒适偏好，客流与演出不能提前保证');
 block(s,'排队选择','超过心理上限，先吃饭、看秀或休息\n创极速光轮放在西侧，作为一日替换\n减少反复横穿乐园',66,219);
 block(s,'所在园区就近吃饭','巴波萨烧烤、星露台餐厅\n皮诺丘乡村厨房等查官方 App\n两人每日普通餐饮预留 240–400 元',681,219);
 txt(s,'付费加速与回酒店午睡',66,497,1120,44,32,C.green,true);
 txt(s,'只为一直排很久的必玩项目比较官方在售尊享。\n酒店往返方便且票务允许当日再入园，才考虑回酒店午睡。',66,553,1128,82,26);
 foot(s,'近 11 号线 B 到乐园安检预留 30–60 分钟，不含安检排队。末班与回程出发前确认。');
 note(s,'### 乐园餐饮与购物',[URL.disney,URL.rules]);
}
// 19
{
 const s=slide('上海街头奶茶：顺路尝 2–3 次','优先体验路线附近饮品，品牌起源与门店在售另行确认');
 table(s,[['候选','点单方向','放在哪天'],['裕莲茶楼 豫园','琥珀奶茶，蛋挞共享可选','D2 顺路，单篇线索'],['附近在营沪上阿姨','当季鲜果／鲜茶／谷物类','D3 或 D5 附近择一'],['阿姨奶茶 本溪路 272 号','血糯米奶茶，小杯少糖','杨浦半日替换，先核营业'],['桂源铺／桂桂茶','各按真实店名搜索港式奶茶','只选地图旁在营店']],[385,437,330],64,206,78,25);
 foot(s,'阿姨奶茶与沪上阿姨分别搜索。桂源铺／桂桂茶关系未证。阿嬷源于广西，顺路可喝。');note(s,'### 奶茶：上海街头体验，顺路选 2–3 次',[URL.X(7),URL.X(8),URL.X(9),URL.X(10)]);
}
// 20
{
 const s=slide('其他特色餐：附近就吃，不跨城追店','本帮菜先点一荤一素加主食，甜浓菜不必同餐多点');
 table(s,[['餐食','店铺候选','路线与预留预算／两人'],['本帮红烧肉／小排','上海老饭店／老正兴','顺路一餐，180–300 元'],['葱油拌面／点心','德兴馆，核附近分店','简便餐，50–100 元'],['麻酱拌面','味香斋','淮海西侧替换，50–100 元'],['鲜肉月饼／熟食','光明邨 淮海中路','淮海西侧替换，30–80 元']],[320,382,450],64,207,78,25);
 foot(s,'老饭店／老正兴证据较弱，作为候选。预算并非菜单价，月饼／熟食先问保存条件。');note(s,'### 小红书餐饮店单：按区域安排，选够一顿就停',[URL.X(2),URL.X(10)]);
}
// 21
{
 const s=slide('返程日：自然醒后去机场','7 天版 D7，8 天版 D8，优先下午或傍晚航班');
 block(s,'浦东机场','通常离迪士尼周边较近\n按 B 准确地址比较地铁／网约车\n时间、费用按当天导航与叫车页',66,221);
 block(s,'虹桥机场','11 号线到交通大学换 10 号线\n确认航站楼与地铁出口\n行李多或早班机优先比较打车',681,221);
 txt(s,'返程不加远处景点',66,499,1125,47,34,C.green,true);
 txt(s,'先核航班值机要求，再加市区／机场交通、取行李与步行余量。\n伴手礼少量买，不把乐园散场当晚接早航班。',66,564,1140,86,26);
 note(s,'### D7｜自然醒后返程',[URL.metro,URL.disney]);
}
// 22
{
 const s=slide('市区交通速查：以大世界 A 为例','门到门为规划估算，出口与末班车出门前查实时导航');
 table(s,[['目的地','主要线路','估算时间'],['豫园','14 号线到豫园','20–40 分钟'],['外滩／南京东路','8 到人民广场换 2，出站向东','30–50 分钟'],['武康大楼','8 到老西门换 10，到交通大学','45–65 分钟'],['陆家嘴','14 号线到陆家嘴','25–45 分钟'],['淮海东侧／新天地','14 到一大会址·黄陂南路','20–40 分钟']],[270,632,250],64,193,68,25);
 foot(s,'外滩在浦西，陆家嘴在浦东。合并游玩时乘地铁过江，不能直接步行跨黄浦江。');note(s,'### 市区路径：以大世界 A 为示例',[URL.metro]);
}
// 23
{
 const s=slide('5、6、8 天怎么调整','保留每家至少两晚，假期越短，城市游越需要取舍');
 table(s,[['天数','住宿分配','主要取舍'],['5 天 4 晚','A2 + B2','地标合并一天，街区短逛，乐园 1 天'],['6 天 5 晚','A3 + B2','陆家嘴／外滩合并，删豫园专门半日'],['7 天 6 晚','A4 + B2','当前主方案，城市区域分别安排'],['8 天 7 晚','A4 + B3','D6／D7 乐园分区玩，D8 返程']],[230,280,642],64,205,78,25);
 foot(s,'5 天版不建议再塞两日乐园。特别不想搬家可全程住 A，接受乐园日更长通勤。');note(s,'## 六、按假期长度调整');
}
// 24
{
 const s=slide('两人预算：基础费用与票机分开','人民币，一间房两人合住。全部为规划估算');
 table(s,[['项目','7 天，乐园 1 天','8 天，乐园 2 天'],['住宿，按 200–500／间／晚','1,200–3,000','1,400–3,500'],['非乐园正餐 + 园内餐饮','1,200–2,080','1,440–2,480'],['茶饮咖啡 + 市内机场交通','610–1,290','690–1,460'],['可选景点 + 机动余量','300–1,200','350–1,300'],['基础小计','3,310–7,570','3,880–8,740']],[472,340,340],64,193,60,24);
 txt(s,'总额另加 2 × T₁ 或 2 × T₂，加 2 × F 和自选消费',66,577,1140,48,28,C.green,true);
 foot(s,'T₁：单人一日票，T₂：单人两天全部票费，F：单人往返含行李机票。购物／早享／尊享自选。');note(s,'## 八、两人预算');
}
// 25
{
 const s=slide('天气、疲劳与出发前核对','十月下旬带防风外套与好走的鞋，天气以临近预报为准');
 block(s,'下雨或走累的删减顺序','D2 缩外滩延伸，保留短段\nD3 只走武康大楼与安福局部\nD4 一个商场加滨江短段\nD5 缩购物，提前入住 B',66,218);
 block(s,'行前核对','先确认门票，再落实机票与酒店\nB 地铁／接驳与散场回程\n买手店入口、楼层、预约与在营\n官方 App 开闭园、秀、项目状态',681,218);
 txt(s,'地图收藏夹按每天分组',66,522,1140,48,32,C.green,true);
 txt(s,'先收藏 A、B，再保存每一天 POI。出门只导航下一站。\n奶茶店和餐厅各备一间附近在营店，避免为排队打乱节奏。',66,576,1140,78,25);
 note(s,'## 九、下雨、疲劳与行前准备',[URL.disney,URL.metro]);
}
// 26
{
 const s=slide('资料依据与可点击入口','审读日期 2026-10-13，详细原文链接保存在本页备注');
 txt(s,'113 篇旅行指南\n10 篇小红书文字补充',66,212,550,136,40,C.green,true);
 txt(s,'小红书补充吃住经验、店址与预约。\n实游、店方推广、AI 整理分开看。\n具体房价、菜单、在营与指定日票价\n仍以预订时／出发前信息为准。',66,393,550,170,25);
 link(s,'上海迪士尼官网',URL.disney,718,222,475,28);
 link(s,'官方门票产品',URL.tickets,718,286,475,28);
 link(s,'官方游客须知',URL.rules,718,350,475,28);
 link(s,'上海地铁公告与线网',URL.metro,718,414,475,28);
 link(s,'小红书实游参考 X02',URL.X(2),718,478,475,28);
 foot(s,'路线为非比例顺序示意。店名搜索入口帮助定位，选匹配门牌 POI 后再点路线。');
 s.speakerNotes.text='完整来源索引，审读日期2026-10-13：\n'+sources+'\n\n小红书审读记录：\n'+JSON.stringify(xhs,null,2);
}

await fs.mkdir(path.join(BUILD,'renders'),{recursive:true});
const candidate=path.join(BUILD,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidate);
await fs.writeFile(path.join(BUILD,'slides.json'),JSON.stringify(p.toProto()));
for(const [i,s] of p.slides.items.entries()){
 const blob=await p.export({slide:s,format:'png',scale:1});
 await fs.writeFile(path.join(BUILD,'renders',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
 console.log(`rendered ${i+1}/${p.slides.items.length}`);
}
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const final=path.join(ROOT,'PPT/上海10月下旬轻松旅行攻略（完整版）.pptx');
await fs.mkdir(path.dirname(final),{recursive:true});
const tableOwners=[3,5,8,10,19,20,22,23,24];
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:final,pythonExecutable:path.join(RUNTIME,'python/python.exe'),integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:tableOwners,requiredNativeChartOwnerSlides:[],fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(BUILD,'validation-final.json')});
console.log(JSON.stringify({finalPath:result.finalPath,slideCount:p.slides.items.length,bytes:result.byteCount,layout:result.presentationLayout},null,2));
