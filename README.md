# sfg-skills-agnes

Agnes AI 图像与视频生成技能，兼容 Agent Skills 开放标准。

## 功能

- **文生图**：根据文本提示词生成高质量图片
- **图生图**：基于已有图片进行风格转换、编辑或优化
- **文生视频**：根据文本提示词生成视频
- **图生视频**：将静态图片动画化
- **多图视频生成**：使用多张参考图片指导视频生成
- **关键帧动画**：在关键帧之间生成平滑过渡

## 支持模型

| 模型 | 用途 |
|------|------|
| `agnes-image-2.1-flash` | 图像生成 |
| `agnes-video-v2.0` | 视频生成 |

## 安装

### OpenClaw

```bash
cp -r sfg-skills-agnes ~/.qclaw/skills/
```

### Claude Code

```bash
cp -r sfg-skills-agnes ~/.claude/skills/
```

### GitHub Copilot

```bash
cp -r sfg-skills-agnes .agents/skills/
```

## 首次使用

安装后需配置 API Key：

```bash
python3 scripts/agnes_config.py set --api-key YOUR_API_KEY
```

> API Key 仅保存在本地 `~/.agnes/config.json`，不会被提交到版本控制。

## 使用示例

### 生成图片

```bash
# 文生图
python3 scripts/agnes_image.py \
  --prompt "A luminous floating city above a misty canyon at sunrise, cinematic realism" \
  --size "1024x768"

# 图生图
python3 scripts/agnes_image.py \
  --prompt "Transform the scene into a cyberpunk night with neon reflections while preserving the original composition" \
  --size "1024x768" \
  --image "https://example.com/input-image.png"
```

### 生成视频

```bash
# 文生视频
python3 scripts/agnes_video.py \
  --prompt "A cinematic shot of a cat walking on the beach at sunset" \
  --width 1152 --height 768 \
  --num-frames 121 --frame-rate 24

# 图生视频
python3 scripts/agnes_video.py \
  --prompt "The woman slowly turns around and looks back at the camera" \
  --image "https://example.com/image.png"

# 关键帧动画
python3 scripts/agnes_video.py \
  --prompt "Smooth cinematic transition between keyframes" \
  --images "https://example.com/keyframe1.png,https://example.com/keyframe2.png" \
  --mode keyframes
```

## 项目结构

```
sfg-skills-agnes/
├── SKILL.md                          # 技能入口（元数据 + 指令）
├── scripts/
│   ├── agnes_config.py               # API Key 配置管理
│   ├── agnes_image.py                # 图像生成脚本
│   └── agnes_video.py                # 视频生成脚本
├── references/
│   ├── agnes-image-api.md            # Agnes Image API 参考文档
│   └── agnes-video-api.md            # Agnes Video API 参考文档
├── .gitignore
├── LICENSE
└── README.md
```

## 许可证

Apache-2.0
