#!/usr/bin/env python3
"""
WebGAL HUST Voice Generation — MiniMax speech-2.8-hd
Custom voice_design voices, per-line emotion/speed/pitch/pause/tone-tags.
Usage:
  python generate_all.py          # generate all lines
  python generate_all.py --sample # generate one sample per speaker only
"""

import os, re, time, sys, requests, json
from pathlib import Path
from collections import defaultdict

# ============================================================
# CONFIGURATION
# ============================================================
API_KEY = "sk-api-9gkTfEnMqQbgoF5x6hhRnkT4a0hzwG78ygoDj_K__TZ3lfCkZ4B25K7Iu1PtvKAd1YHMFUg3lyq-p7azIsicMDGqOHHSLPDXfXNg4EaFKIi36SwfQxXE1_A"
API_URL = "https://api.minimaxi.com/v1/t2a_v2"
MODEL = "speech-2.8-hd"

SCENE_DIR = Path("d:/project/WebGAL/packages/webgal/public/game/scene")
SCENE_FILES = ["hust_ch1.txt", "hust_ch1_1950s.txt", "hust_ch2.txt", "hust_ch3.txt"]
OUTPUT_DIR = Path("d:/project/WebGAL/packages/webgal/public/game/vocal")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# SPEAKER CONFIG — system voice IDs + per-character base settings
# ============================================================
SPEAKER_CONFIG = {
    "林知远": {
        "voice_id": "Chinese (Mandarin)_Straightforward_Boy",
        "alias": "lin", "speed": 1.04, "pitch": 0, "default_emotion": "calm",
    },
    "1024": {
        "voice_id": "Arrogant_Miss",
        "alias": "s1024", "speed": 1.07, "pitch": 0, "default_emotion": "calm",
    },
    "陈老师": {
        "voice_id": "hunyin_6",
        "alias": "chen", "speed": 1.02, "pitch": 0, "default_emotion": "calm",
    },
    "张江陵": {
        "voice_id": "Chinese_gravelly_storyteller_vv2",
        "alias": "zhangjl", "speed": 1.00, "pitch": 0, "default_emotion": "calm",
    },
    "张工": {
        "voice_id": "Chinese_kind_uncle_vv1",
        "alias": "zhangg", "speed": 1.00, "pitch": 0, "default_emotion": "calm",
    },
    "李教授": {
        "voice_id": "Chinese_calm_streamer_vv1",
        "alias": "li", "speed": 0.99, "pitch": 0, "default_emotion": "calm",
    },
    "周师兄": {
        "voice_id": "Chinese (Mandarin)_Gentle_Youth",
        "alias": "zhou", "speed": 1.12, "pitch": 0, "default_emotion": "calm",
    },
    "苏师姐": {
        "voice_id": "Chinese_crisp_podcaster_vv1",
        "alias": "su", "speed": 1.12, "pitch": 0, "default_emotion": "calm",
    },
    "王学长": {
        "voice_id": "Chinese (Mandarin)_Stubborn_Friend",
        "alias": "wang", "speed": 1.02, "pitch": 0, "default_emotion": "calm",
    },
}

# ============================================================
# PER-LINE MANUAL TONE — emotion, speed, pitch, text override
# text override contains <#x#> pause tags and (tone) tags
# ============================================================
# Total entries: 105

MANUAL_TONE = {

    # hust_ch1_1950s.txt (拓荒期)
    "ch1_1950s_chen_0001": {
        "emotion": "happy",
        "text": "新同学？快进来。今天的课在草棚里上<#0.2#>教学楼还没盖完。",
    },
    "ch1_1950s_chen_0002": {
        "emotion": "calm",
        "text": "纸，和笔。(breath)这是我昨晚写的程序<#0.2#>47条指令，每一条都手写。写完还得在纸上推演<#0.2#>寄存器里存什么，地址指到哪，全部手算。",
    },
    "ch1_1950s_chen_0003": {
        "emotion": "calm",
        "text": "今天王老师没来，他的时间段空出来了。加上我的，我们有12分钟。(breath)在那个年代，上机时间是比黄金还珍贵的资源。",
    },
    "ch1_1950s_chen_0004": {
        "emotion": "happy",
        "text": "(chuckle)你确定？你的bug还没调完呢。",
    },
    "ch1_1950s_chen_0005": {
        "emotion": "calm",
        "text": "好小子。(breath)你知道我们那个年代最怕什么？不是技术落后，最怕人心散了。(breath)技术落后可以追，人心散了什么都做不成。",
    },
    "ch1_1950s_chen_0006": {
        "emotion": "happy",
        "text": "那位学弟后来成了我们国家第一个自主CAD软件的主程。(breath)你刚才这个决定<#0.2#>帮了一个后来改变了行业的人。",
    },
    "ch1_1950s_chen_0007": {
        "emotion": "calm",
        "text": "行。搞技术，该专注的时候就专注。(breath)来，我帮你一起看<#0.2#>循环里有个变量初始值没清零，边界条件漏了。",
    },
    "ch1_1950s_chen_0008": {
        "emotion": "calm",
        "text": "不低级。苏联专家撤走时连M-3的手册都没留下。(breath)你这个边界错误，我们当年踩了三个月的坑。(breath)珍惜每一次debug的机会<#0.2#>每个bug背后，都有人替你探过路。",
    },
    "ch1_1950s_lin_0003": {
        "emotion": "calm",
        "text": "陈老师，门口那个学弟等好久了，要不把时间给他？",
    },
    "ch1_1950s_lin_0004": {
        "emotion": "calm",
        "text": "我的不急。(breath)他的程序是帮机械系算材料应力用的，关系到下周实验<#0.2#>比我这个重要。",
    },
    "ch1_1950s_lin_0005": {
        "emotion": "sad",
        "text": "陈老师，我还差一个bug没找到，想抓紧时间跑通。",
    },
    "ch1_1950s_lin_0006": {
        "emotion": "happy",
        "text": "就是这个！！(breath)低级错误<#0.2#>",
    },
    "ch1_1950s_lin_0007": {
        "emotion": "calm",
        "text": "debug好像<#0.15#>也没那么痛苦了。",
    },
    "ch1_1950s_lin_0008": {
        "emotion": "calm",
        "text": "不是做不出来<#0.15#>而是还没开始做。",
    },
    "ch1_1950s_lin_0009": {
        "emotion": "surprised",
        "text": "全自主？！(breath)在80年代？！",
    },
    "ch1_1950s_lin_0010": {
        "emotion": "angry",
        "text": "这不就是<#0.15#>技术殖民？",
    },
    "ch1_1950s_lin_0011": {
        "emotion": "calm",
        "text": "应该先展示。酒香也怕巷子深，做出东西要让人看到。",
    },
    "ch1_1950s_lin_0012": {
        "emotion": "sad",
        "text": "贴牌？！(sighs)这句话现在听也很耳熟。",
    },
    "ch1_1950s_lin_0013": {
        "emotion": "calm",
        "text": "应该沉下来攻关核心技术。(breath)展示再好，内核不是自己的，就是组装厂。",
    },
    "ch1_1950s_lin_0014": {
        "emotion": "happy",
        "text": "那我们就做第一个。",
    },
    "ch1_1950s_s1024_0004": {
        "emotion": "calm",
        "text": "全校没有一台电子计算机。(breath)但全国急需计算机人才，这个专业还是办了起来。",
    },
    "ch1_1950s_s1024_0005": {
        "emotion": "calm",
        "text": "拓荒者的故事都在告诉你一件事<#0.2#>真正的爱国，是每一个具体的选择。",
    },
    "ch1_1950s_s1024_0006": {
        "emotion": "calm",
        "text": "下一站<#0.2#>当所有中国人的数据都存在外国人造的设备上，你会怎么做？",
    },
    "ch1_1950s_zhangg_0001": {
        "emotion": "calm",
        "text": "我们正在搞国产微型计算机。(breath)主板自己设计，操作系统自己写<#0.2#>全套自主。",
    },
    "ch1_1950s_zhangg_0002": {
        "emotion": "calm",
        "text": "对，技术殖民。(breath)所以我们才要自己干。(breath)我们写了操作系统叫HUST-DOS，存储模块64KB<#0.2#>芯片从香港辗转买回，一颗等于普通人一个月工资。(breath)但现在到了一个关口<#0.2#>经费有限。是亮剑还是磨剑？完善系统出去展示，还是沉下心攻关32位架构？",
    },
    "ch1_1950s_zhangg_0003": {
        "emotion": "happy",
        "text": "好，全力备战明年展览。(breath)系统里有一千多行汇编bug，你得帮忙。",
    },
    "ch1_1950s_zhangg_0004": {
        "emotion": "angry",
        "text": "HUST-DOS引起了轰动，科学院当场批了经费。(breath)但有家美国公司说可以合作<#0.2#>用他们的芯片和系统，我们贴牌。(breath)我拒绝了。对方走时说：没有我们的芯片，你们什么都做不出来。",
    },
    "ch1_1950s_zhangg_0005": {
        "emotion": "calm",
        "text": "所以你知道为什么要敢于竞争了<#0.2#>不是为了赢谁，是为了有一天没人能用技术卡我们的脖子。",
    },
    "ch1_1950s_zhangg_0006": {
        "emotion": "happy",
        "text": "说得好！(breath)朱九思老校长也说过<#0.2#>华工要做别人做不了的事。(breath)32位从指令集到内存管理，全是无人区。这有一本刚从国外复印回来的架构白皮书<#0.2#>用最简洁的设计实现最高效的计算。",
    },
    "ch1_1950s_zhangg_0007": {
        "emotion": "sad",
        "text": "可惜后来经费断了，人才流失了。(sighs)那时候我们连知识产权都不太清楚，等回过神来，路已经被别人占了。",
    },
    "ch1_1950s_zhangjl_0001": {
        "emotion": "calm",
        "text": "我是张江陵，1974年开始做外部存储。(breath)这是我们的DJS-112<#0.2#>全自主，CPU、内存、外设接口全部自己设计，全国第一个用海明码纠错的。(breath)1978年拿了全国科学大会重大贡献奖。",
    },

    # hust_ch1.txt (序章)
    "ch1_lin_0001": {
        "emotion": "sad",
        "text": "(sighs)不是吧<#0.2#>这红黑树的旋转逻辑明明是对的啊，怎么还是段错误<#0.2#>",
    },
    "ch1_lin_0002": {
        "emotion": "surprised",
        "text": "<#0.15#>什么情况？(breath)我是不是赶作业出现幻觉了？",
    },
    "ch1_s1024_0001": {
        "emotion": "happy",
        "text": "叮！检测到一名正在debug的计算机学子。(breath)我是1024，你的历史编译助手。",
    },
    "ch1_s1024_0002": {
        "emotion": "calm",
        "text": "不是幻觉哦。你现在接入的是专业历史编译系统<#0.2#>简单来说，我会带你看看，你现在写的每一行代码，背后站着多少前辈。",
    },
    "ch1_s1024_0003": {
        "emotion": "happy",
        "text": "准备好了吗？(breath)我们从最早的那一行代码开始<#0.2#>",
    },

    # hust_ch2.txt (突围期)
    "ch2_li_0001": {
        "emotion": "calm",
        "text": "帮我把这组存储校验测试跑一下。(breath)10万次读写，给银行存储系统用的<#0.2#>一个字都不能错。",
    },
    "ch2_li_0002": {
        "emotion": "calm",
        "text": "国外的方案，像别人给的鱼竿。(breath)看着好用，但鱼线多长、鱼钩多大<#0.2#>全捏在人家手里。(breath)华科要做的事<#0.2#>不是用别人的鱼竿，是造自己的渔船。",
    },
    "ch2_li_0003": {
        "emotion": "calm",
        "text": "我认识一位师姐。她读博时发现<#0.2#>国内所有的存储设备，全是进口的，没有一件Made in China。(breath)毕业后她留校，拒绝了国外高薪，从零开始做。二十年。(breath)从一个人到一个国家实验室，国产存储从不到5%做到60%以上。(breath)她的名字叫冯丹<#0.2#>现在是我们华科计算机学院的院长。",
    },
    "ch2_li_0004": {
        "emotion": "calm",
        "text": "我一个学生王浩，在硅谷顶级存储公司，年薪很高。(breath)最近想回国，但家里人都劝他留下。(breath)你怎么看？",
    },
    "ch2_li_0005": {
        "emotion": "happy",
        "text": "(chuckle)你跟我想的一样。(breath)但爱国这件事不能靠讲道理<#0.2#>得自己想通。",
    },
    "ch2_li_0006": {
        "emotion": "calm",
        "text": "我当年在德国做访问学者，导师留我读博，帮我申了洪堡奖学金<#0.2#>简直是科研人的天堂。",
    },
    "ch2_li_0007": {
        "emotion": "calm",
        "text": "有一天读到美国国防部的可信计算机系统评估标准，里面说：计算机安全标准，应由技术领先国家制定。(breath)我突然明白<#0.2#>标准不只是技术问题，是话语权，是规则制定权。(breath)如果我们永远跟在别人后面，就永远只能做规则的服从者。",
    },
    "ch2_li_0008": {
        "emotion": "calm",
        "text": "第二天，我回复导师<#0.2#>我要回中国。",
    },
    "ch2_li_0009": {
        "emotion": "calm",
        "text": "有道理。但你知道最大的风险吗？(breath)等一等容易变成回不来。(breath)硅谷那地方<#0.2#>高薪、好房、好学区。待得越久，回来的阻力越大。(breath)到那时候，不是不想回来，是回不来了。",
    },
    "ch2_li_0010": {
        "emotion": "calm",
        "text": "有些决定，看起来是选更好的条件，实际上<#0.2#>是放弃选择的权利。",
    },
    "ch2_li_0011": {
        "emotion": "calm",
        "text": "现在国际上在推新标准。(breath)兼容它能进国际市场，但要放弃一些我们自己的技术特色。(breath)跟随标准降低迁移成本，还是坚持自己的路争夺话语权？",
    },
    "ch2_li_0012": {
        "emotion": "calm",
        "text": "务实。(breath)但兼容做久了，创新动力会退化。(breath)我的方案是：核心架构兼容，在数据保护、缓存、能耗这些非标准化的地方全力做出差异化。(breath)好比<#0.2#>别人规定了路宽和限速，但没规定你用什么发动机。",
    },
    "ch2_li_0013": {
        "emotion": "happy",
        "text": "这就是善于转化。",
    },
    "ch2_li_0014": {
        "emotion": "calm",
        "text": "说得对。(breath)但前几代产品可能卖不出去<#0.2#>不兼容主流生态，客户不买账。",
    },
    "ch2_li_0015": {
        "emotion": "calm",
        "text": "选了，而且对了。(breath)2015年国家启动自主可控战略，要求关键基础设施逐步替换国外设备。(breath)那些兼容路线的企业<#0.2#>核心不在手里，转型不了。华光架构全自主，直接就能用。",
    },
    "ch2_li_0016": {
        "emotion": "calm",
        "text": "做技术决策，不能只看短期市场得失，要看长期的战略方向。",
    },
    "ch2_li_0017": {
        "emotion": "happy",
        "text": "2023年，华科并行数据存储实验室在IO500 10节点榜单上，拿了总成绩世界第一。",
    },
    "ch2_li_0018": {
        "emotion": "calm",
        "text": "世界纪录被我们刷新了15倍。(breath)记住，不是跟在别人后面<#0.2#>是领先。",
    },
    "ch2_lin_0015": {
        "emotion": "calm",
        "text": "老师，既然国外已有成熟方案了，为什么还要从零做？",
    },
    "ch2_lin_0016": {
        "emotion": "calm",
        "text": "应该回来。(breath)核心技术必须在自己人手里。",
    },
    "ch2_lin_0017": {
        "emotion": "surprised",
        "text": "那您为什么回来？",
    },
    "ch2_lin_0018": {
        "emotion": "calm",
        "text": "计服报国这四个字<#0.2#>原来是这样写的。",
    },
    "ch2_lin_0019": {
        "emotion": "calm",
        "text": "可以再留几年。(breath)硅谷是技术最前沿，积累够了回来更有用。",
    },
    "ch2_lin_0020": {
        "emotion": "sad",
        "text": "<#0.35#>(sighs)<#0.2#>",
    },
    "ch2_lin_0021": {
        "emotion": "calm",
        "text": "不是要不要回来的问题<#0.2#>是什么时候、以什么方式回来。",
    },
    "ch2_lin_0022": {
        "emotion": "calm",
        "text": "应该先兼容。(breath)迁移成本太高没人用，活下来才能谈引领。",
    },
    "ch2_lin_0023": {
        "emotion": "calm",
        "text": "既在规则内竞争，又在规则外超越。",
    },
    "ch2_lin_0024": {
        "emotion": "calm",
        "text": "应该走自己的路。(breath)标准是技术强的人定的。",
    },
    "ch2_lin_0025": {
        "emotion": "surprised",
        "text": "那您还选这条路？",
    },
    "ch2_lin_0026": {
        "emotion": "calm",
        "text": "敢于竞争<#0.2#>不是口号，是真金白银的长期投入。",
    },
    "ch2_s1024_0007": {
        "emotion": "calm",
        "text": "中国存储市场100%被国外垄断。(breath)银行交易、政府文件、科研数据<#0.2#>全存在外国人造的设备上。(breath)这不是商业问题，是国家安全。",
    },
    "ch2_s1024_0008": {
        "emotion": "calm",
        "text": "爱国不是非此即彼的选择题。(breath)是在任何环境下，都保持回来的能力和意愿。",
    },
    "ch2_s1024_0009": {
        "emotion": "calm",
        "text": "技术从来不只是技术。(breath)是安全，是话语权，是一个国家的底气。",
    },

    # hust_ch3.txt (领航期)
    "ch3_li_0019": {
        "emotion": "calm",
        "text": "你们面对的是新的仗<#0.2#>AI霸权、算力霸权。(breath)但答案一样<#0.2#>计服报国。(breath)不是口号，是选择。",
    },
    "ch3_lin_0027": {
        "emotion": "calm",
        "text": "所以我们缺的不是一个点<#0.15#>是整个生态？",
    },
    "ch3_lin_0028": {
        "emotion": "calm",
        "text": "想做AI应用方向。(breath)AI是这十年最大的变量，不想三十岁才发现自己错过了。",
    },
    "ch3_lin_0029": {
        "emotion": "calm",
        "text": "做AI不是目的，解决真问题是目的。",
    },
    "ch3_lin_0030": {
        "emotion": "calm",
        "text": "想做底层基础软件。(breath)AI虽然热，但编译器、操作系统、数据库<#0.2#>这些才是根基。",
    },
    "ch3_lin_0031": {
        "emotion": "calm",
        "text": "没事。(breath)调页表再苦，也比用LED灯看寄存器幸福。",
    },
    "ch3_lin_0032": {
        "emotion": "calm",
        "text": "我选择创业。(breath)第一章，前辈在草棚里办计算机专业。第二章，冯丹老师用二十年把中国存储从5%做到60%。(breath)第三章<#0.2#>轮到我了。",
    },
    "ch3_lin_0033": {
        "emotion": "calm",
        "text": "我选择加入国家队。(breath)不是进体制混日子<#0.2#>是接触最核心的基础设施。之江实验室、鹏城实验室、武汉超算中心<#0.2#>需要既懂AI又懂系统的人。",
    },
    "ch3_lin_0034": {
        "emotion": "calm",
        "text": "跨地域调度要解决不稳定延迟下的同步训练吧？(breath)全球都没有完美方案。",
    },
    "ch3_lin_0035": {
        "emotion": "calm",
        "text": "我选择读博。(breath)不是因为逃避就业<#0.2#>是因为存算一体。",
    },
    "ch3_lin_0036": {
        "emotion": "calm",
        "text": "现在的计算机，计算和存储是分开的。(breath)数据在处理器和存储器之间搬来搬去<#0.2#>功耗的七成浪费在路上。(breath)如果把计算直接做在存储芯片上，效率能提升几十上百倍。",
    },
    "ch3_lin_0037": {
        "emotion": "calm",
        "text": "没关系。(breath)李教授说过：有些决定，看起来是选更好的条件，实际是放弃选择的权利。",
    },
    "ch3_lin_0038": {
        "emotion": "calm",
        "text": "我曾经觉得爱国是很遥远的词<#0.2#>直到我看见了草棚教室、DJS-112、牛棚外等人的朱九思、冯丹老师二十年的坚持。(breath)我才真正明白<#0.2#>爱国，就是把你写的每一行代码，都当成国家未来的一部分。",
    },
    "ch3_lin_0039": {
        "emotion": "calm",
        "text": "每一位计算机人，都是这个国家1024字节中的一个比特。(breath)单个的0或1没有意义<#0.2#>但连在一起，就是一个时代。",
    },
    "ch3_s1024_0010": {
        "emotion": "calm",
        "text": "林知远<#0.2#>你从1958年走到了现在。纸上写代码、DJS-112、存储国家队、IO500。(breath)现在，轮到你的时代了。",
    },
    "ch3_s1024_0011": {
        "emotion": "calm",
        "text": "你经历了三个时代<#0.2#>拓荒者的信仰、突围者的抉择、领航者的机遇。(breath)现在，轮到你自己了。三条路<#0.2#>",
    },
    "ch3_s1024_0012": {
        "emotion": "calm",
        "text": "还有第三条<#0.2#>",
    },
    "ch3_s1024_0013": {
        "emotion": "calm",
        "text": "林知远<#0.2#>你的选择是什么？",
    },
    "ch3_s1024_0014": {
        "emotion": "calm",
        "text": "四十年前，华科计算机系也是这样开始的<#0.2#>一间屋子，一群人，一股不甘心的劲儿。(breath)你没选安逸<#0.2#>你选了一条难的路。",
    },
    "ch3_s1024_0015": {
        "emotion": "calm",
        "text": "选择国家队<#0.2#>不是去追风口，是去建设支撑风口的底座。(breath)若干年后，当有人问中国为什么能做到AI普惠<#0.2#>答案里，有你写的算力调度代码。",
    },
    "ch3_s1024_0016": {
        "emotion": "calm",
        "text": "你选的不是学位。(breath)是国家未来技术突破的种子。",
    },
    "ch3_s1024_0017": {
        "emotion": "calm",
        "text": "无论你选了哪条路<#0.2#>你都做出了自己的回答。(breath)就像朱九思用广积人回答了人才从哪里来，就像冯丹用二十年回答了中国能不能做自己的存储。",
    },
    "ch3_s1024_0018": {
        "emotion": "calm",
        "text": "代码为谁而写？<#0.35#>",
    },
    "ch3_su_0001": {
        "emotion": "calm",
        "text": "别被卡脖子吓到。(breath)正因为他们不给，你才要自己造。(breath)这是危和机并存的时代。",
    },
    "ch3_su_0002": {
        "emotion": "happy",
        "text": "有眼光！(breath)过去十年大家都搞AI，做系统的人严重断代。(breath)国家推自主可控，突然发现<#0.2#>人呢？开源RISC-V要人移植内核，国产数据库要人优化查询引擎，哪里都缺人。",
    },
    "ch3_su_0003": {
        "emotion": "calm",
        "text": "第一条：留在这里创业。(breath)做AI训练的分布式文件系统，全部核心代码自主。(breath)很难<#0.2#>但冯丹老师当年不也这样开始的？",
    },
    "ch3_su_0004": {
        "emotion": "happy",
        "text": "欢迎。(breath)东九楼楼下24小时奶茶店<#0.2#>以后是我们的第二办公室。(chuckle)奶茶算公司福利，但你得搞定第一个客户。我已经约了武汉超算中心负责人，下周三面谈。",
    },
    "ch3_wang_0001": {
        "emotion": "calm",
        "text": "2024年，我们做出了全球最大容量的MRAM存算一体芯片<#0.2#>64兆比特，28纳米全自主。(breath)叫喻家山1号。(breath)童薇老师说：我们不敢停，也不能停。(breath)喻家山2号已经进入流片阶段了。",
    },
    "ch3_wang_0002": {
        "emotion": "calm",
        "text": "你要动计算机体系结构的根基啊。(breath)但是真正的卡脖子破局点<#0.2#>芯片制造我们短期追不上，如果在新架构上换道超车，局面就不一样了。(breath)华科是这个方向全国最好的<#0.2#>喻家山1号已经证明我们能做出来。",
    },
    "ch3_wang_0003": {
        "emotion": "calm",
        "text": "不过这是冷板凳中的冷板凳<#0.2#>可能五年出不了大成果。",
    },
    "ch3_zhou_0001": {
        "emotion": "calm",
        "text": "你们想过没有<#0.2#>为什么ChatGPT不是中国公司做出来的？(breath)从芯片到AI框架，每一层都有卡脖子。(breath)底层全捏在别人手里，你在上面写再多应用，不是沙上建塔吗？",
    },
    "ch3_zhou_0002": {
        "emotion": "calm",
        "text": "大致两个方向：一是AI应用<#0.2#>大模型、多模态，热门，好发论文；二是底层基础软件<#0.2#>操作系统、编译器、数据库，冷，苦，但缺人。",
    },
    "ch3_zhou_0003": {
        "emotion": "happy",
        "text": "说到真问题<#0.2#>光电学院用AI做光刻机晶圆缺陷检测，精度99.99%。(breath)AI用在了最卡脖子的地方<#0.2#>这才是好方向。",
    },
    "ch3_zhou_0004": {
        "emotion": "calm",
        "text": "第二条：加入国家队。(breath)去之江实验室做AI算力调度<#0.2#>为中国的大模型提供水电煤一样的基础设施。",
    },
    "ch3_zhou_0005": {
        "emotion": "happy",
        "text": "你来负责算力调度<#0.2#>让GPU之间走高速通道，支持弹性伸缩，跨超算中心统一调度。(breath)武汉、深圳、杭州的GPU当成一台机器用。",
    },
    "ch3_zhou_0006": {
        "emotion": "happy",
        "text": "对，这就是最有意思的挑战。",
    },
}

# Total: 105 entries

# ============================================================
# TEXT PROCESSING
# ============================================================
def process_tts_text(text):
    """Clean text for TTS. Pause/tone tags are handled via MANUAL_TONE text override."""
    # Strip leftover mp3 references
    text = re.sub(r'\s+-[a-zA-Z][a-zA-Z0-9_]*\.mp3', '', text)
    # Remove （...） parentheticals
    text = re.sub(r'[（(][^）)]*[）)]', '', text)
    # Replace em-dashes with pause-tagged comma
    text = text.replace('——', '，<#0.25#>')
    text = text.replace('—', '，<#0.2#>')
    # Replace ellipsis with pause
    text = text.replace('……', '<#0.3#>')
    text = text.replace('…', '<#0.2#>')
    # Clean up
    text = re.sub(r'，+', '，', text)
    text = re.sub(r'\s+', '', text)
    return text.strip()

DIALOGUE_RE = re.compile(r'^([^:]+):(.+)$')

def detect_action_text(text):
    """Extract parenthetical action from text."""
    m = re.match(r'^[（(]([^）)]*)[）)]', text)
    if m:
        return m.group(1), text[m.end():].strip()
    return None, text

# ============================================================
# PARSING
# ============================================================
def parse_scene_files():
    dialogues = []
    speaker_seq = defaultdict(int)

    for filename in SCENE_FILES:
        filepath = SCENE_DIR / filename
        if not filepath.exists():
            continue

        stem = filepath.stem
        ch_prefix = "_".join(stem.split("_")[1:]) if "_" in stem else stem

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            line_text = line.rstrip("\n").rstrip("\r")
            if not line_text.strip() or line_text.strip().startswith(";"):
                continue

            m = DIALOGUE_RE.match(line_text.strip())
            if not m:
                continue

            speaker = m.group(1).strip()
            if speaker not in SPEAKER_CONFIG:
                continue

            raw_text = m.group(2).strip()
            if not raw_text:
                continue

            action_text, _ = detect_action_text(raw_text)
            alias = SPEAKER_CONFIG[speaker]["alias"]
            speaker_seq[alias] += 1
            seq = speaker_seq[alias]
            audio_fn = f"{ch_prefix}_{alias}_{seq:04d}.mp3"

            # Get tone override
            tone = MANUAL_TONE.get(audio_fn.replace('.mp3', ''), {})
            emotion = tone.get("emotion", SPEAKER_CONFIG[speaker]["default_emotion"])

            # Use manual text override if available, else auto-process
            if "text" in tone:
                clean_text = tone["text"]
            else:
                clean_text = process_tts_text(raw_text)

            dialogues.append({
                "file": filepath, "filename": filename,
                "line_num": i, "original_line": line_text.strip(),
                "speaker": speaker, "alias": alias,
                "raw_text": raw_text, "clean_text": clean_text,
                "action": action_text, "emotion": emotion,
                "audio_filename": audio_fn, "seq": seq,
                "tone": tone,
            })

    return dialogues

# ============================================================
# API CALL
# ============================================================
def generate_audio(dialogue, max_retries=3):
    config = SPEAKER_CONFIG[dialogue["speaker"]]
    tone = dialogue.get("tone", {})
    emotion = tone.get("emotion", config["default_emotion"])
    speed = tone.get("speed", config["speed"])
    pitch = tone.get("pitch", config["pitch"])

    voice_setting = {
        "voice_id": config["voice_id"],
        "speed": speed,
        "vol": 1.0,
        "pitch": pitch,
        "emotion": emotion,
    }

    body = {
        "model": MODEL,
        "text": dialogue["clean_text"],
        "stream": False,
        "voice_setting": voice_setting,
        "audio_setting": {
            "sample_rate": 32000, "bitrate": 128000,
            "format": "mp3", "channel": 1,
        },
        "output_format": "hex",
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json=body, timeout=120,
            )
            if resp.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"    Rate limited (429), retry in {wait}s...", flush=True)
                time.sleep(wait); continue

            resp.raise_for_status()
            data = resp.json()
            sc = data.get("base_resp", {}).get("status_code", 0)

            if sc == 1002:
                wait = 3 * (attempt + 1)
                print(f"    RPM limit, retry in {wait}s...", flush=True)
                time.sleep(wait); continue

            if sc != 0:
                print(f"    API error {sc}: {data.get('base_resp',{}).get('status_msg','')}", flush=True)
                return None

            hex_audio = data.get("data", {}).get("audio", "")
            if not hex_audio:
                print(f"    No audio data", flush=True); return None

            return bytes.fromhex(hex_audio)

        except requests.exceptions.RequestException as e:
            print(f"    HTTP error: {e}", flush=True)
            if attempt < max_retries - 1:
                time.sleep(3 * (attempt + 1))
            else:
                return None
        except Exception as e:
            print(f"    Error: {e}", flush=True); return None
    return None

# ============================================================
# UPDATE SCENE FILES
# ============================================================
def update_scene_file(filepath, dialogues_in_file):
    if not dialogues_in_file:
        return
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    line_updates = {d["line_num"]: d["audio_filename"] for d in dialogues_in_file}

    for line_num in sorted(line_updates.keys(), reverse=True):
        line = lines[line_num].rstrip("\n").rstrip("\r")
        fn = line_updates[line_num]
        stripped = re.sub(r'\s+-[a-zA-Z][a-zA-Z0-9_]*\.mp3', '', line)
        if stripped.endswith(";"):
            stripped = stripped.rstrip(";").rstrip()
            lines[line_num] = f"{stripped} -{fn};\n"
        else:
            lines[line_num] = f"{stripped.rstrip()} -{fn}\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

# ============================================================
# MAIN
# ============================================================
def main():
    sample_mode = "--sample" in sys.argv

    print("=" * 60, flush=True)
    print(f"WebGAL HUST Voice Gen — {MODEL} {'(SAMPLES ONLY)' if sample_mode else '(FULL)'}", flush=True)
    print("=" * 60, flush=True)

    # Parse
    print("\n[1/3] Parsing...", flush=True)
    dialogues = parse_scene_files()
    print(f"  {len(dialogues)} dialogue lines", flush=True)

    # Sample mode: pick one per speaker
    if sample_mode:
        seen = set()
        samples = []
        for d in dialogues:
            if d["alias"] not in seen:
                seen.add(d["alias"])
                samples.append(d)
        dialogues = samples
        print(f"  Sample mode: {len(dialogues)} lines (one per speaker)", flush=True)

    # Preview tones
    print("\n[2/3] Preview:", flush=True)
    for d in dialogues[:15]:
        tone = d["tone"]
        cfg = SPEAKER_CONFIG[d["speaker"]]
        spd = tone.get("speed", cfg["speed"])
        em = tone.get("emotion", cfg["default_emotion"])
        print(f"  {d['speaker']}({d['alias']}) emo={em} spd={spd:.2f} -> {d['audio_filename']}", flush=True)
        print(f"    \"{d['clean_text'][:100]}\"", flush=True)

    # Generate
    print(f"\n[3/3] Generating {len(dialogues)} lines...", flush=True)
    success, fail = 0, 0
    CALL_DELAY = 3.5

    for idx, d in enumerate(dialogues):
        out = OUTPUT_DIR / d["audio_filename"]
        if out.exists() and out.stat().st_size > 100:
            print(f"  [{idx+1}/{len(dialogues)}] SKIP {d['audio_filename']}", flush=True)
            success += 1; continue
        elif out.exists():
            out.unlink()

        tone = d["tone"]
        cfg = SPEAKER_CONFIG[d["speaker"]]
        em = tone.get("emotion", cfg["default_emotion"])
        spd = tone.get("speed", cfg["speed"])
        print(f"  [{idx+1}/{len(dialogues)}] {d['speaker']}({em}, spd={spd:.2f}) "
              f"\"{d['clean_text'][:65]}\" -> {d['audio_filename']}", flush=True)

        audio = generate_audio(d)
        if audio:
            with open(out, "wb") as f:
                f.write(audio)
            print(f"    OK {len(audio)} bytes", flush=True)
            success += 1
        else:
            print(f"    FAILED", flush=True)
            fail += 1

        if idx < len(dialogues) - 1:
            time.sleep(CALL_DELAY)

    print(f"\n  {success} ok, {fail} failed", flush=True)

    # Update files
    if not sample_mode and fail == 0:
        print("\nUpdating scene files...", flush=True)
        by_file = defaultdict(list)
        for d in parse_scene_files():
            by_file[d["file"]].append(d)
        for fp, fds in by_file.items():
            update_scene_file(fp, fds)
            print(f"  {fp.name}: {len(fds)} refs", flush=True)

    print("\nDone.", flush=True)

if __name__ == "__main__":
    main()
