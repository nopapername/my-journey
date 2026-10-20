$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$travelOutput = 'D:\web3\code_project\旅游规划\上海\路线图'
New-Item -ItemType Directory -Path $travelOutput -Force | Out-Null
$travelInk = [System.Drawing.ColorTranslator]::FromHtml('#173238')
$travelMuted = [System.Drawing.ColorTranslator]::FromHtml('#50666B')
$travelGreen = [System.Drawing.ColorTranslator]::FromHtml('#17665A')
$travelBg = [System.Drawing.ColorTranslator]::FromHtml('#FAF8F2')
$travelSoft = [System.Drawing.ColorTranslator]::FromHtml('#E6F0EB')
$travelLine = [System.Drawing.ColorTranslator]::FromHtml('#C6D4CB')
$travelFont = [System.Drawing.Font]::new('Microsoft YaHei', 27, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
$travelSmall = [System.Drawing.Font]::new('Microsoft YaHei', 23, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
$travelTitle = [System.Drawing.Font]::new('Microsoft YaHei', 46, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
$travelBold = [System.Drawing.Font]::new('Microsoft YaHei', 30, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)

function PutText($gfx, [string]$value, $font, $color, [single]$x, [single]$y, [single]$w, [single]$h) {
    $brush = [System.Drawing.SolidBrush]::new($color)
    $rect = [System.Drawing.RectangleF]::new($x,$y,$w,$h)
    $gfx.DrawString($value,$font,$brush,$rect)
    $brush.Dispose()
}
function DrawBox($gfx, [single]$x,[single]$y,[single]$w,[single]$h,$fill) {
    $brush=[System.Drawing.SolidBrush]::new($fill)
    $gfx.FillRectangle($brush,$x,$y,$w,$h)
    $brush.Dispose()
}
function RouteArrow($gfx,[single]$x1,[single]$y1,[single]$x2,[single]$y2) {
    $pen=[System.Drawing.Pen]::new($travelGreen,3)
    $cap=[System.Drawing.Drawing2D.AdjustableArrowCap]::new(5,6)
    $pen.CustomEndCap=$cap
    $gfx.DrawLine($pen,$x1,$y1,$x2,$y2)
    $pen.Dispose();$cap.Dispose()
}
function Canvas($height) {
    $bmp=[System.Drawing.Bitmap]::new(1600,$height)
    $gfx=[System.Drawing.Graphics]::FromImage($bmp)
    $gfx.Clear($travelBg)
    $gfx.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $gfx.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    return @($bmp,$gfx)
}
function SaveCanvas($pair,$name) {
    $pair[0].Save((Join-Path $travelOutput $name),[System.Drawing.Imaging.ImageFormat]::Png)
    $pair[1].Dispose();$pair[0].Dispose()
}

$pair=Canvas 1200
$gfx=$pair[1]
PutText $gfx '上海 7 天：市区慢游 + 迪士尼' $travelTitle $travelInk 70 45 1440 75
PutText $gfx '2 位成年人 · 示例 2026/10/23–10/29 · A 连住 4 晚，B 连住 2 晚' $travelFont $travelMuted 70 130 1440 50
$days=@(
    @('D1 10/23 周五','成都 → 上海 → 酒店附近晚餐','抵达日休息','A 第 1 晚'),
    @('D2 10/24 周六','豫园片区 → 午休 → 外滩 → 南京东路','老城与江景','A 第 2 晚'),
    @('D3 10/25 周日','武康大楼 → 武康路 → 安福路','买手店与茶饮','A 第 3 晚'),
    @('D4 10/26 周一','陆家嘴商场 → 高楼外观 → 浦东滨江','地铁过江','A 第 4 晚'),
    @('D5 10/27 周二','淮海 / 新天地 → 回 A 取行李 → B','唯一搬酒店日','B 第 1 晚'),
    @('D6 10/28 周三','迪士尼：3 个主要目标 + 看秀 + 午休','乐园 1 天','B 第 2 晚'),
    @('D7 10/29 周四','睡到自然醒 → 机场 → 成都','返程留缓冲','不住宿')
)
for($i=0;$i -lt $days.Count;$i++) {
    $y=210+$i*115
    DrawBox $gfx 70 $y 220 94 $travelSoft
    $travelDayLabel=$days[$i][0] -split ' ',3
    PutText $gfx ($travelDayLabel[0]+' '+$travelDayLabel[1]) $travelBold $travelGreen 85 ($y+10) 205 42
    PutText $gfx $travelDayLabel[2] $travelSmall $travelGreen 85 ($y+54) 205 37
    PutText $gfx $days[$i][1] $travelBold $travelInk 330 ($y+8) 940 47
    PutText $gfx $days[$i][2] $travelSmall $travelMuted 330 ($y+55) 940 40
    PutText $gfx $days[$i][3] $travelBold $travelGreen 1320 ($y+25) 220 55
    if($i -lt 6){RouteArrow $gfx 170 ($y+96) 170 ($y+113)}
}
PutText $gfx '8 天版：D7 再玩 1 天乐园，D8 10/30 返程；B 连住 3 晚。' $travelFont $travelInk 70 1045 1450 50
PutText $gfx '行程顺序示意，非比例地图。具体酒店与下一站路线以实时导航为准。' $travelSmall $travelMuted 70 1110 1450 50
SaveCanvas $pair '00-行程总览.png'

function DetailRoute($name,$title,$subtitle,$steps,$footer) {
    $height=265+$steps.Count*124+100
    $pair=Canvas $height
    $gfx=$pair[1]
    PutText $gfx $title $travelTitle $travelInk 70 45 1450 75
    PutText $gfx $subtitle $travelFont $travelMuted 70 125 1450 75
    for($i=0;$i -lt $steps.Count;$i++) {
        $y=230+$i*124
        DrawBox $gfx 70 $y 120 92 $travelSoft
        PutText $gfx ([string]($i+1)).PadLeft(2,'0') $travelTitle $travelGreen 95 ($y+13) 90 70
        PutText $gfx $steps[$i][0] $travelBold $travelInk 230 ($y+4) 1260 45
        PutText $gfx $steps[$i][1] $travelSmall $travelMuted 230 ($y+48) 1260 48
        if($i -lt $steps.Count-1){RouteArrow $gfx 130 ($y+94) 130 ($y+122)}
    }
    PutText $gfx $footer $travelSmall $travelMuted 70 ($height-92) 1450 78
    SaveCanvas $pair $name
}

DetailRoute '01-外滩老城.png' 'D2：豫园、外滩与南京东路' '10 点左右出门；酒店近时回去午休，16 点前后再看外滩。' @(
    @('酒店 A → 豫园站','大世界乘 14 号线；老西门乘 10 号线。园林入内先核对开放与票务。'),
    @('园林 / 商城择一 → 南翔小笼或大壶春生煎','园林与商城不同；两家午餐二选一，排队过久换店。裕莲奶茶可选。'),
    @('回 A 午休，或找商场 / 茶馆坐下','保留 60–90 分钟恢复体力，不拖着疲劳走全程。'),
    @('南京东路站 → 外滩江边','沿南京东路向东走至中山东一路；先看建筑，再看江景。'),
    @('外滩主段 → 黄浦公园附近（外白渡桥可选）','日落前到达，停留至天色变暗；不承诺固定亮灯时刻。'),
    @('南京东路向西 → 晚餐 / 沈大成糕团 → A','条头糕、双酿团少量尝鲜。全天约 3–5 公里，准确分店用地图确认。')
) '路线顺序示意，非地理底图；景点开放、店铺、出口和步行分钟以当天查询为准。'

DetailRoute '02-武康安福.png' 'D3：武康路与安福路慢逛' '主方向：从武康路南端进入，向北接安福路，再向东逛。' @(
    @('酒店 A → 交通大学站','从老西门上 10 号线；大世界可先乘 8 号线到老西门换乘。'),
    @('交通大学站 → 武康大楼','约 10–20 分钟步行；拍照站人行道，不在路口车道停留。'),
    @('武康路向北 → 建筑 / 商业空间','沿路慢走，只进喜欢的店；不要把住宅当作开放场馆。'),
    @('安福路午餐 → in the PARK（安福路 322 号）','小红书 X03：6 号楼 1 楼，先核当天营业与入口；不是六楼。'),
    @('向东 → RONIN MADE Lounge（可选）','安福路 275 号 5 弄 1 楼；X04 / X06 均强调提前预约，不顺路就跳过。'),
    @('继续向东 → CSYSeLECTED','安福路 234 号 2 楼，X05 店方自述；三家中重点选两家，留 2–3 小时。'),
    @('乌鲁木齐中路 → 茶饮 / 咖啡休息','至少坐下 45–60 分钟；本溪路阿姨奶茶在杨浦，不加进这条线。'),
    @('按终点选常熟路 / 上海图书馆站，或打车回 A','武康路与新天地相隔约 4 公里，不作为顺手步行延伸。')
) '本图是步行方向与交通顺序示意，非比例地图；商家可迁址，导航以准确 POI 为准。'

DetailRoute '03-陆家嘴.png' 'D4：陆家嘴商场与浦东滨江' '默认地面慢游；上海中心 / 东方明珠 / 金茂登高任选一个替换。' @(
    @('酒店 A → 陆家嘴站','大世界 / 豫园上 14 号线；这是乘地铁过江。'),
    @('国金中心商场 / 正大广场择一','逛街、午餐和坐下休息；不用两个商场都逛。'),
    @('上海中心 → 金茂 / 环球金融中心外观','三件套相邻，走人行道和过街设施；环球金融仅列外观。'),
    @('陆家嘴滨江大道 → 看浦西外滩','挑有座位的短段，天气好时看黄昏；下午累了先在室内坐下。'),
    @('晚餐 → 14 号线回 A','默认步行约 2–4 公里；不为同晚两岸夜景反复过江。')
) '陆家嘴在浦东，外滩在浦西，不能直接步行跨江。本图非地理底图，路线与开放以实时查询为准。'

DetailRoute '04-转场日.png' 'D5：短逛与唯一一次酒店转场' 'A 4 晚结束；B 连住 2 晚，8 天版 B 连住 3 晚。' @(
    @('A 退房 → 寄存行李','先确认寄存与 B 入住时间；不拉着箱子逛街。'),
    @('淮海中路局部 → 新天地北里 / ALTER 可选','约 10:30–12:30；ALTER 线索：马当路 245 号新天地 L116，先核营业。'),
    @('午餐 → 回 A 取行李','约 14 点取箱；买手店优先者可用富民路局部替换上述街区。'),
    @('A → 酒店 B（优先比较网约车）','地铁到 11 号线酒店：8 号线 → 东方体育中心 → 11 号线。'),
    @('若选川沙 B：落实乐园接驳','川沙为 2 号线；迪士尼为 11 号线，二者不是同一交通节点。'),
    @('B 入住 → 附近吃饭 → 早休息','转场预留 60–120 分钟门到门；小镇只在交通方便、有余力时选。')
) '交通顺序示意，非比例地图。酒店实际地址、接驳首末班、收费预约和夜间接回须在预订时确认。'

DetailRoute '05-迪士尼.png' 'D6：迪士尼东侧为主，3 个目标' '按当天开放和 App 排队调整先后；以下是分区游玩顺序示意，不是地理底图。' @(
    @('酒店 B → 11 号线迪士尼站 / 已确认接驳 → 安检','按当日开园时间倒推；提前 45–60 分钟到安检区是规划建议，不是早享权益。'),
    @('东侧主目标：飞越地平线','有悬空感，晕动或不喜欢就换温和项目；不跑步抢项目。'),
    @('东侧邻近区域：加勒比海盗 / 相邻项目','随 App 当天队列调整先后，不为了几分钟差异横穿乐园。'),
    @('11:30–13:00：午餐 + 坐下 60–90 分钟','先恢复体力；看秀不能完全代替安静休息。'),
    @('疯狂动物城：热力追踪 → 邻近节目 / 城堡拍照','默认第 3 个目标；巡游和剧场场次以当天 App 为准。'),
    @('刺激偏好替换：明日世界创极速光轮','需要前往西侧时集中安排一次；替换上述目标，不再叠加全部热门。'),
    @('夜间演出可选 → 留出园步行 / 集合余量 → B','演出不保证举办；确认末班或接回时间，两天版第二天降低强度。')
) '证件、票务条件与时刻以官方为准。行李箱留酒店；食品、摄影装备携带规则见主文已读官方须知。'

$travelFont.Dispose();$travelSmall.Dispose();$travelTitle.Dispose();$travelBold.Dispose()
Get-ChildItem -LiteralPath $travelOutput | Select-Object Name,Length
