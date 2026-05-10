# 《代码中的中国：1024航迹云》

> 华中科技大学 计算机学院 创新2401班 8人小组项目
>
> 基于 WebGAL 引擎制作的思政教育视觉小说（Galgame）

**[在线游玩 →](https://felixlovejj.github.io/WebGAL/)**


## 任务：

### 一、背景图（18张，16:9，2560×1440，jpg/png）

```
packages/webgal/public/game/background/
```

| 文件名                      | 场景               | AI 提示词（用于 Midjourney / DALL·E）                        |
| --------------------------- | ------------------ | ------------------------------------------------------------ |
| `bg_d9_night.jpg`           | 东九楼夜景         | chinese university teaching building at night, warm yellow lights from windows, a few windows still lit late at night, dark and quiet atmosphere, yu jiashan mountain silhouette in background, shinkai makoto style, 16:9 --ar 16:9 --style anime |
| `bg_system.jpg`             | 系统空间           | sci-fi digital space, deep blue background, flowing binary code and glowing data streams, translucent holographic interface at center, cyberpunk but bright, clean modern scifi aesthetic, 16:9 --ar 16:9 |
| `bg_hust_old.jpg`           | 1958年华中工学院   | 1950s chinese university campus, grey brick soviet-style buildings, dirt paths, young plane trees under blue sky, simple and austere architecture, warm nostalgic sunlight, anime style background, 16:9 --ar 16:9 --style anime |
| `bg_computer_room_old.jpg`  | 老旧机房           | 1960s computer room, one massive vacuum-tube computer filling whole room, tape drives, blinking indicator lights, grey metal cabinets, technician in white coat working, warm yellow lighting, anime style, 16:9 --ar 16:9 --style anime |
| `bg_hust_1970s.jpg`         | 1970年代华工       | 1970s chinese university campus after cultural revolution, overgrown grass on campus paths, old teaching buildings, autumn atmosphere, slightly desolate but with sprouts of hope, distant yu jiashan mountain, warm desaturated tones, anime style, 16:9 --ar 16:9 --style anime |
| `bg_lab_1970s.jpg`          | 1970年代存储实验室 | 1970s chinese electronics lab, workbenches with analog oscilloscopes, soldering irons, hand-drawn circuit diagrams on walls, open-reel tape drives, a minicomputer with front panel lights, dim warm lighting, dusty but authentic, anime style, 16:9 --ar 16:9 --style anime |
| `bg_lab_1980s.jpg`          | 1980年代实验室     | 1980s electronics laboratory in china, wooden workbench with breadboards, oscilloscope, multimeter, green CRT monitor, circuit diagrams and handwritten notes on wall, faint soldering smoke, warm nostalgic tones, anime style, 16:9 --ar 16:9 --style anime |
| `bg_hust_1980s.jpg`         | 1980年代华工       | 1980s chinese university campus, early reform-era teaching buildings, bicycle sheds, students in blue-white plaid shirts, mature plane trees, bright sunny day, reform and opening up atmosphere, anime style, 16:9 --ar 16:9 --style anime |
| `bg_hust_1990s.jpg`         | 1990年代华科       | 1990s chinese university campus, more modern buildings, students carrying canvas bags, windows 95 era desktop computers visible through windows, exposed network cables on ceiling, end-of-century atmosphere, anime style, 16:9 --ar 16:9 --style anime |
| `bg_storage_lab.jpg`        | 存储实验室         | 1990s computer storage lab, stacked RAID disk array cabinets, CRT monitors showing configuration interfaces, blue server room lighting, dense but orderly cables, serious professional atmosphere, anime style, 16:9 --ar 16:9 --style anime |
| `bg_storage_lab_modern.jpg` | 现代存储实验室     | 2010s modern data center style lab, neat server racks in rows, blue LED strip lights, glass partitions, large monitoring screens showing distributed storage topology, cool professional tones, anime style, 16:9 --ar 16:9 --style anime |
| `bg_hust_modern.jpg`        | 现代华科校园       | 2020s huazhong university of science and technology, modern glass curtain wall buildings, lush green campus, students walking through plaza, bright sunny day, fresh clean anime style, 16:9 --ar 16:9 --style anime |
| `bg_classroom_modern.jpg`   | 创新班教室         | modern university seminar room, smart blackboard or large screen, round-table seating, laptops and tablets on desks, green trees visible through window, relaxed academic atmosphere, anime style, 16:9 --ar 16:9 --style anime |
| `bg_hust_autumn.jpg`        | 华科秋景           | hust autumn scenery, golden ginkgo and plane tree leaves covering roads, warm sunset light, yu jiashan silhouette in distance, peaceful and slightly sentimental beauty, shinkai makoto style, 16:9 --ar 16:9 |
| `bg_startup_office.jpg`     | 创业办公室         | small startup office in optical valley, less than 40sqm, 6-person workspace, whiteboard with architecture diagrams, coffee cups and instant noodles on desks, modern buildings visible through window, messy but energetic, anime style, 16:9 --ar 16:9 --style anime |
| `bg_supercomputing.jpg`     | 超算中心           | national supercomputing center interior, rows of GPU server racks humming, blue cooling lights, massive monitoring screens showing distributed training tasks and data flows, sci-fi but real atmosphere, anime style, 16:9 --ar 16:9 --style anime |
| `bg_lab_future.jpg`         | 忆阻器实验室       | advanced nano device laboratory, precision probe station, oscilloscope showing memristor I-V curves, laser platform, cleanroom atmosphere, futuristic science, cool white and blue tones, anime style, 16:9 --ar 16:9 --style anime |
| `bg_hust_sunset.jpg`        | 华科日落           | hust evening panorama, warm golden sunset on teaching buildings and plane trees, orange-red clouds on horizon, yu jiashan silhouette, peaceful warm slightly emotional atmosphere, shinkai makoto style, 16:9 --ar 16:9 |

------

### 二、角色立绘（9人 + 9小头像，png 透明底）

```
packages/webgal/public/game/figure/
```

**立绘：1024×1536，半身像，png透明背景**

| 文件名            | 角色           | AI 提示词                                                    |
| ----------------- | -------------- | ------------------------------------------------------------ |
| `fig_chen.png`    | 陈老师         | 1950s young chinese teacher, 25-year-old male, white short-sleeve shirt tucked into dark blue trousers, black half-rim glasses, slim build, determined and gentle eyes, short black hair, simple zhongshan-style attire, anime style half-body portrait, transparent background |
| `fig_zhangjl.png` | 张江陵         | 1970s chinese computer scientist, 50-year-old male, simple dark blue jacket, thin and weathered face, deep-set intelligent eyes with crows feet, grey hair, worn hands, humble but authoritative presence, pioneer scientist, anime style half-body portrait, transparent background |
| `fig_zhang.png`   | 张工           | 1980s chinese engineer, 30-year-old male, blue work overalls, slightly thinning hair on top (programmer hair loss), slightly chubby, slightly tanned from long lab hours, honest expression but sharp eyes, sleeves rolled to elbows, anime style half-body portrait, transparent background |
| `fig_li.png`      | 李教授         | 1990-2010s chinese computer science professor, 45-year-old male, silver-rim glasses, greying short hair (scholarly), dark jacket or shirt, thin and upright posture, deep eyes with stories to tell, scholar-practitioner presence, anime style half-body portrait, transparent background |
| `fig_zhou.png`    | 周宇博士       | 2020s chinese PhD student, 26-year-old male, black frame glasses, grey hoodie under dark blue jacket, slightly messy short hair, holding laser pointer or tablet, sunny academic type, friendly smile, anime style half-body portrait, transparent background |
| `fig_su.png`      | 苏晴学姐       | 2020s chinese female entrepreneur, 24-year-old, short and neat hairstyle, white shirt + dark casual blazer (unbuttoned), jeans, one hand in pocket, confident smile, capable yet approachable, anime style half-body portrait, transparent background |
| `fig_wang.png`    | 王浩学长       | chinese returnee elite, 30-year-old male, dark blue polo shirt + khaki pants (silicon valley engineer style), black half-rim glasses, clean short hair, calm and mature expression, experienced-through-choices look, anime style half-body portrait, transparent background |
| `fig_1024.png`    | 1024系统精灵   | AI assistant digital lifeform, androgynous appearance (slightly feminine), semi-translucent glowing body, blue-white color scheme, pixel/data stream particle effects at body edges, glowing pupils, floating posture, sci-fi but not cold, slightly playful, anime style + light scifi, transparent background |
| `fig_lin.png`     | 林知远（主角） | 2020s chinese sophomore student, 20-year-old male, light-colored hoodie or HUST t-shirt, slightly messy short black hair, average university student look (not too handsome), glasses, slightly tired but earnest eyes, approachable senior student vibe, anime style half-body portrait, transparent background |

**小头像：256×256，面部特写**

| 文件名                 | 对应角色 |
| ---------------------- | -------- |
| `fig_chen_mini.png`    | 陈老师   |
| `fig_zhangjl_mini.png` | 张江陵   |
| `fig_zhang_mini.png`   | 张工     |
| `fig_li_mini.png`      | 李教授   |
| `fig_zhou_mini.png`    | 周宇     |
| `fig_wang_mini.png`    | 王浩     |
| `fig_lin_mini.png`     | 林知远   |

------

### 三、BGM（5首，mp3/ogg）

```
packages/webgal/public/game/bgm/
```

| 文件名            | 用途           | Suno AI 提示词                                               |
| ----------------- | -------------- | ------------------------------------------------------------ |
| `bgm_retro.mp3`   | 第一章拓荒期   | warm nostalgic chinese 1970s film score style, solo piano or small string ensemble, slightly weathered but not sad, reminiscent of classic chinese cinema, 65 BPM |
| `bgm_tense.mp3`   | 第二章技术封锁 | low string section with electronic textures, tense but not oppressive, sense of drive and urgency, minor key but with hope underneath, building momentum, 85 BPM |
| `bgm_hopeful.mp3` | 第二章技术突破 | orchestral crescendo from low strings to bright brass, gradual swell from darkness to light, triumphant but earned not bombastic, hope and breakthrough, 75 BPM |
| `bgm_modern.mp3`  | 第三章现代校园 | electronic beats with ambient synths, light and techy but warm, modern china university vibe, positive forward-looking energy, 95 BPM |
| `bgm_inspire.mp3` | 第三章高潮结局 | soaring orchestral with piano lead and full strings, uplifting and inspiring melody, patriotic but personal, cinematic climax, suitable for 2-3 minute loop, 85 BPM |

------

### 四、可选视频（1个）

```
packages/webgal/public/game/video/
```

| 文件名                     | 用途         | 建议                                                         |
| -------------------------- | ------------ | ------------------------------------------------------------ |
| `hust_cs_achievements.mp4` | 结尾字幕播放 | HUST CS学院成就混剪（可用素材来自学院官网/公众号），没有则保持脚本中该行注释 |
## 项目简介

主角林知远是创新2401班的大二学生，在东九楼赶作业时意外进入了"专业历史编译系统"，穿越中国计算机史的三个时代：

- **第一章 拓荒期（1950s-1980s）**：纸上写代码、排队上机、华工自研微机
- **第二章 突围期（1990s-2010s）**：存储国家队、技术封锁、守护数据安全
- **第三章 领航期（2020s-2026）**：新质生产力、AI浪潮、卡脖子与报国

---

## 快速开始

```bash
# 克隆项目
git clone https://github.com/felixlovejj/WebGAL.git
cd WebGAL

# 安装依赖（只需一次）
yarn install

# 启动本地预览
yarn dev
```

打开 `http://localhost:3000/`，修改文件后浏览器自动刷新。

---

## 协作方式

### 用 PR（Pull Request）

每个人 Fork 仓库 → 上传文件 → 提 PR。

### 第一步：Fork 仓库

打开 `https://github.com/felixlovejj/WebGAL` → 点右上角 **Fork** → 完成。

你就有了一个自己的副本：`https://github.com/你的用户名/WebGAL`

### 上传图片/音频：网页上传就够了

直接在 GitHub 网页操作：

1. 打开你 Fork 的仓库
2. 点进对应文件夹（如 `packages/webgal/public/game/background/`）
3. 点 **Add file → Upload files**
4. 拖入你的图片/音乐文件
5. 在提交信息里写 `添加 xxx 场景背景`
6. 点 **Commit changes**，选 `Create a new branch...`（分支名随便填，如 `add-bg-xxx`）
7. 点 **Propose changes** → 自动跳到 PR 页面
8. 点 **Create pull request**



### 剧本同学：需要本地操作

因为改剧本需要预览效果，所以必须 clone 到本地。

```bash
# 克隆你 Fork 的仓库（不是主仓库）
git clone https://github.com/你的用户名/WebGAL.git
cd WebGAL
yarn install

# 改剧本前先建一个分支（分支名比如 script/ch1-xxx）
git checkout -b script/ch1-xxx

# 改完提交
git add packages/webgal/public/game/scene/hust_ch1.txt
git commit -m "修改第一章：xxx"
git push origin script/ch1-xxx

# 去 GitHub 点 "Compare & pull request"
```

> **铁律：同一时间一个人只改一个 .txt 文件。改之前先在群里说一声。**

### 分工一览

```
角色          改什么目录        操作方式
────────────────────────────────────────
美术-背景     background/      网页上传 → PR
美术-立绘     figure/          网页上传 → PR
音频-BGM     bgm/              网页上传 → PR
剧本         scene/*.txt       本地分支 → PR
```


## 项目结构

```
packages/webgal/public/game/
├── background/          ← 背景图（2560×1440，jpg/png）
├── figure/              ← 角色立绘（1024×1536 透明底）+ 小头像（256×256）
├── bgm/                 ← 背景音乐（mp3/ogg）
├── scene/               ← ★ 剧本文件（.txt）
│   ├── hust_ch1.txt        第一章序章
│   ├── hust_ch1_1950s.txt  第一章正篇
│   ├── hust_ch2.txt        第二章
│   └── hust_ch3.txt        第三章
├── vocal/               ← 语音（可选）
├── config.txt           ← 游戏标题配置
└── template/            ← UI 模板
```

---

## 部署到 GitHub Pages(不用管)

```bash
# 1. 构建
yarn webgal:build

# 2. 推送到 gh-pages 分支
cd packages/webgal/dist
git init && git checkout -b gh-pages       # 仅首次
touch .nojekyll                            # 仅首次
git remote add origin https://github.com/felixlovejj/WebGAL.git  # 仅首次
git add -A
git commit -m "Deploy"
git push -f origin gh-pages
```

> 如果用代理，push 时加 `-c http.proxy=http://127.0.0.1:7890 -c https.proxy=http://127.0.0.1:7890`

---


