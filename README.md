# 《代码中的中国：1024航迹云》

> 华中科技大学 计算机学院 创新2401班 8人小组项目
>
> 基于 WebGAL 引擎制作的思政教育视觉小说（Galgame）

**[在线游玩 →](https://felixlovejj.github.io/WebGAL/)**

---

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

### 全组都用 PR（Pull Request）

每个人 Fork 仓库 → 上传文件 → 提 PR。不需要加协作者，不需要学分支。

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

## 部署到 GitHub Pages

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


## 引擎说明

本项目基于 [WebGAL](https://github.com/OpenWebGAL/WebGAL) 引擎 v4.5，MPL-2.0 开源协议。

原引擎 README 见 [README_old.md](README_old.md)。
