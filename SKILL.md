---
name: sfg-skills-agnes
description: |
  Agnes AI 图像与视频生成技能。当用户需要生成图片（文生图、图生图）或视频（文生视频、图生视频、多图视频、关键帧动画）时使用此技能。
  触发关键词：生成图片、绘图、画图、AI画图、文生图、图生图、生成视频、做视频、AI视频、文生视频、图生视频、关键帧动画、Agnes、agnes-image、agnes-video。
  安装后需配置 API Key 才能使用，首次使用时引导用户设置。
license: Apache-2.0
compatibility: 需要 Python 3.8+ 和 curl，需要网络访问 apihub.agnes-ai.com
metadata:
  author: sfg-studio
  version: "1.0.0"
  category: creative
  models:
    - agnes-image-2.1-flash
    - agnes-video-v2.0
allowed-tools: Bash(python3:*) Bash(curl:*) Read Write
---

# Agnes AI 图像与视频生成技能

通过 Agnes AI API 生成高质量图片和视频。支持文生图、图生图、文生视频、图生视频、多图视频和关键帧动画。

## 首次使用：配置 API Key

安装技能后，必须先配置 API Key：

```bash
python3 "{SKILL_DIR}/scripts/agnes_config.py" set --api-key YOUR_API_KEY
```

查看当前配置：

```bash
python3 "{SKILL_DIR}/scripts/agnes_config.py" show
```

> ⚠️ API Key 仅保存在本地 `~/.agnes/config.json`，不会被提交到版本控制。

---

## 一、图像生成（agnes-image-2.1-flash）

### 1.1 文生图

根据文本提示词生成图片：

```bash
python3 "{SKILL_DIR}/scripts/agnes_image.py" \
  --prompt "A luminous floating city above a misty canyon at sunrise, cinematic realism" \
  --size "1024x768"
```

### 1.2 图生图

基于已有图片进行风格转换或编辑：

```bash
python3 "{SKILL_DIR}/scripts/agnes_image.py" \
  --prompt "Transform the scene into a rain-soaked cyberpunk night with neon reflections while preserving the original composition" \
  --size "1024x768" \
  --image "https://example.com/input-image.png"
```

也支持本地图片（自动转 Base64）：

```bash
python3 "{SKILL_DIR}/scripts/agnes_image.py" \
  --prompt "Make the object orange while preserving the original composition" \
  --size "1024x768" \
  --image "/path/to/local/image.png"
```

### 1.3 图像参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--size` | 1024x768 | 输出图片尺寸 |
| `--output-format` | url | 输出格式：`url` 或 `b64_json` |
| `--output-dir` | 当前目录 | 图片保存目录（url 模式自动下载） |
| `--no-download` | false | 仅返回 URL 不下载图片 |

### 1.4 提示词优化

生成图像前，**必须帮助用户优化提示词**：

**文生图推荐结构**：
```
[主体] + [场景/环境] + [风格] + [光照] + [构图] + [质量要求]
```

**图生图推荐结构**：
```
[修改要求] + [新风格/新场景] + [添加/移除的元素] + [需要保留的元素]
```

如果用户提供的提示词过于简单，主动扩展为更完整的描述后再调用 API。

### 1.5 结果展示

图像生成成功后，使用 Markdown 图片格式展示：

```markdown
![生成的图片](https://storage.googleapis.com/agnes-aigc/xxx.png)
```

---

## 二、视频生成（agnes-video-v2.0）

视频生成是**异步任务**，需要先创建任务再轮询查询结果。

### 2.1 文生视频

根据文本提示词生成视频：

```bash
python3 "{SKILL_DIR}/scripts/agnes_video.py" \
  --prompt "A cinematic shot of a cat walking on the beach at sunset, soft ocean waves, warm golden lighting, realistic motion" \
  --width 1152 --height 768 \
  --num-frames 121 --frame-rate 24
```

### 2.2 图生视频

将静态图片动画化：

```bash
python3 "{SKILL_DIR}/scripts/agnes_video.py" \
  --prompt "The woman slowly turns around and looks back at the camera, natural facial expression, cinematic camera movement" \
  --image "https://example.com/image.png" \
  --num-frames 121 --frame-rate 24
```

### 2.3 多图视频生成

使用多张参考图片生成视频：

```bash
python3 "{SKILL_DIR}/scripts/agnes_video.py" \
  --prompt "Create a smooth transformation scene between the two reference images, cinematic lighting, consistent character identity" \
  --images "https://example.com/image1.png,https://example.com/image2.png" \
  --num-frames 121 --frame-rate 24
```

### 2.4 关键帧动画

在关键帧之间生成平滑过渡：

```bash
python3 "{SKILL_DIR}/scripts/agnes_video.py" \
  --prompt "Generate a smooth cinematic transition between the keyframes, maintaining visual consistency and natural camera movement" \
  --images "https://example.com/keyframe1.png,https://example.com/keyframe2.png" \
  --mode keyframes \
  --num-frames 121 --frame-rate 24
```

### 2.5 视频参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--width` | 1152 | 视频宽度 |
| `--height` | 768 | 视频高度 |
| `--num-frames` | 121 | 视频帧数（必须 ≤ 441 且满足 8n+1） |
| `--frame-rate` | 24 | 视频 FPS（1-60） |
| `--seed` | 随机 | 随机种子，用于可复现结果 |
| `--negative-prompt` | 无 | 负向提示词 |
| `--mode` | ti2vid | 生成模式（ti2vid / keyframes） |
| `--poll-interval` | 10 | 轮询间隔秒数 |
| `--timeout` | 600 | 最大等待秒数 |

### 2.6 常用时长参数

| 目标时长 | 推荐参数 |
|----------|----------|
| 约 3 秒 | --num-frames 81 --frame-rate 24 |
| 约 5 秒 | --num-frames 121 --frame-rate 24 |
| 约 10 秒 | --num-frames 241 --frame-rate 24 |
| 约 18 秒 | --num-frames 441 --frame-rate 24 |

### 2.7 提示词优化

**文生视频推荐结构**：
```
[主体] + [动作] + [场景] + [镜头运动] + [光照] + [风格]
```

**图生视频推荐结构**：
```
描述哪些内容需要运动 + 哪些主体元素需要保持稳定
```

如果用户提供的提示词过于简单，主动扩展为更完整的描述后再调用 API。

### 2.8 视频生成等待过程

视频生成通常需要 **1-5 分钟**。创建任务后脚本会自动轮询等待，并在等待期间展示进度：

```
🎬 视频生成任务已创建
   任务 ID: video_xxxxxx
   状态: queued → in_progress
   进度: ████████░░ 80%
   预计等待: ~2 分钟
```

### 2.9 结果展示

视频生成成功后，直接提供视频链接：

```
🎬 视频已生成完成！

🔗 视频链接: https://storage.googleapis.com/agnes-aigc/aigc/videos/xxx.mp4
📏 分辨率: 1280x768
⏱️ 时长: 10.0 秒
```

### 2.10 仅创建任务（不等待）

如果不想阻塞等待，可以使用 `--no-wait` 参数：

```bash
python3 "{SKILL_DIR}/scripts/agnes_video.py" \
  --prompt "..." \
  --no-wait
```

稍后手动查询：

```bash
python3 "{SKILL_DIR}/scripts/agnes_video.py" \
  --query "video_xxxxxx"
```

---

## 三、分辨率与宽高比

### 图像

推荐尺寸：`1024x768`（4:3）、`768x1024`（3:4）、`1024x576`（16:9）、`576x1024`（9:16）、`1024x1024`（1:1）

### 视频

系统会自动标准化到最接近的标准规格：

| 宽高比 | 推荐场景 | 推荐尺寸 |
|--------|----------|----------|
| 16:9 | 横屏视频、YouTube | 1152x768 |
| 9:16 | 竖屏短视频、TikTok | 768x1152 |
| 1:1 | 方形视频、社交媒体 | 768x768 |
| 4:3 | 通用展示 | 1152x768 |
| 3:4 | 竖向展示 | 768x1152 |

---

## 四、完整工作流

1. **检查配置**：确认 API Key 已设置
2. **优化提示词**：将用户简单的描述扩展为完整的专业提示词
3. **调用 API**：执行生成脚本
4. **等待结果**：视频需轮询等待，图像直接返回
5. **展示结果**：图像用 `![]()` 格式，视频用链接格式

---

## Gotchas

- ⚠️ **API Key 必须先配置**：未配置时所有请求都会失败，先运行 `agnes_config.py set --api-key`
- ⚠️ **图像 `response_format` 必须放在 `extra_body` 中**：放顶层会报 400 错误
- ⚠️ **图生图的输入图片放在顶层 `image` 数组**，不是 `extra_body.image`
- ⚠️ **图生图不需要 `tags: ["img2img"]`**
- ⚠️ **视频 `num_frames` 必须 ≤ 441 且满足 8n+1**（如 81/121/161/241/441）
- ⚠️ **视频是异步任务**：创建后需要轮询，建议间隔 5 秒
- ⚠️ **视频 URL 在 `remixed_from_video_id` 字段**，不是 `video_url`
- ⚠️ **图像输入 URL 必须公网可访问**：如无法公网访问，使用本地文件路径（脚本自动转 Base64）
- ⚠️ **不要将 API Key 提交到版本控制**

---

## 错误处理

| 状态码 | 原因 | 处理方式 |
|--------|------|----------|
| 400 | 请求参数无效 | 检查参数格式，特别关注 `response_format` 位置 |
| 401 | API Key 无效 | 检查 Key 是否正确，运行 `agnes_config.py show` 确认 |
| 404 | 任务或视频不存在 | 确认 video_id 或 task_id 是否正确 |
| 500 | 服务器错误 | 稍后重试 |
| 503 | 服务繁忙 | 等待后重试 |

---

## 参考文档

- `references/agnes-image-api.md` — Agnes Image 2.1 Flash API 完整文档
- `references/agnes-video-api.md` — Agnes Video V2.0 API 完整文档
