# Agnes Video V2.0 API 参考文档

## API 信息

| 项目 | 说明 |
|------|------|
| 创建任务 | `POST https://apihub.agnes-ai.com/v1/videos` |
| 查询结果（推荐） | `GET https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>` |
| 查询结果（兼容） | `GET https://apihub.agnes-ai.com/v1/videos/<TASK_ID>` |
| 模型名称 | `agnes-video-v2.0` |
| 认证方式 | Bearer Token |
| 当前价格 | $0/second（免费） |

## 创建任务请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 是 | 固定 `agnes-video-v2.0` |
| prompt | string | 是 | 视频内容文本描述 |
| image | string/array | 否 | 图片 URL 或图片 URL 数组 |
| mode | string | 否 | 生成模式：`ti2vid` 或 `keyframes` |
| width | integer | 否 | 视频宽度，默认 768 |
| height | integer | 否 | 视频高度，默认 1152 |
| num_frames | integer | 否 | 帧数，≤ 441，满足 8n+1 |
| frame_rate | number | 否 | FPS，1-60 |
| seed | integer | 否 | 随机种子 |
| negative_prompt | string | 否 | 负向提示词 |
| extra_body.image | array | 否 | 多图/关键帧模式的输入图片 URL |
| extra_body.mode | string | 否 | 额外模式，如 `keyframes` |

## 帧数约束

- `num_frames` ≤ 441
- `num_frames` 必须满足 `8n + 1`（如 81/121/161/241/441）
- 时长 = num_frames / frame_rate

## 常用时长参数

| 目标时长 | 参数 |
|----------|------|
| 约 3 秒 | num_frames: 81, frame_rate: 24 |
| 约 5 秒 | num_frames: 121, frame_rate: 24 |
| 约 10 秒 | num_frames: 241, frame_rate: 24 |
| 约 18 秒 | num_frames: 441, frame_rate: 24 |

## 分辨率与宽高比

系统会自动标准化到最接近的标准规格。

| 宽高比 | 推荐场景 | 推荐尺寸 |
|--------|----------|----------|
| 16:9 | 横屏、YouTube | 1152x768 |
| 9:16 | 竖屏、TikTok | 768x1152 |
| 1:1 | 方形、社交媒体 | 768x768 |
| 4:3 | 通用展示 | 1152x768 |
| 3:4 | 竖向展示 | 768x1152 |

## 创建任务响应

```json
{
  "id": "task_YOUR_TASK_ID",
  "task_id": "task_YOUR_TASK_ID",
  "video_id": "video_YOUR_VIDEO_ID",
  "object": "video",
  "model": "agnes-video-v2.0",
  "status": "queued",
  "progress": 0,
  "created_at": 1780457477,
  "seconds": "10.0",
  "size": "1280x768"
}
```

## 查询结果响应

### 生成完成

```json
{
  "id": "task_YOUR_TASK_ID",
  "video_id": "video_YOUR_VIDEO_ID",
  "model": "agnes-video-v2.0",
  "object": "video",
  "status": "completed",
  "progress": 100,
  "seconds": "10.0",
  "size": "1280x768",
  "remixed_from_video_id": "https://storage.googleapis.com/agnes-aigc/xxx.mp4",
  "error": null
}
```

> ⚠️ 视频 URL 在 `remixed_from_video_id` 字段中，不是 `video_url`。

## 任务状态

| 状态 | 说明 |
|------|------|
| queued | 排队中 |
| in_progress | 生成中 |
| completed | 已完成 |
| failed | 生成失败 |

## 四种生成模式

### 文生视频
```json
{
  "model": "agnes-video-v2.0",
  "prompt": "描述文本",
  "num_frames": 121,
  "frame_rate": 24
}
```

### 图生视频
```json
{
  "model": "agnes-video-v2.0",
  "prompt": "描述文本",
  "image": "https://example.com/image.png",
  "num_frames": 121,
  "frame_rate": 24
}
```

### 多图视频
```json
{
  "model": "agnes-video-v2.0",
  "prompt": "描述文本",
  "extra_body": {
    "image": ["url1", "url2"]
  },
  "num_frames": 121,
  "frame_rate": 24
}
```

### 关键帧动画
```json
{
  "model": "agnes-video-v2.0",
  "prompt": "描述文本",
  "extra_body": {
    "image": ["keyframe1.png", "keyframe2.png"],
    "mode": "keyframes"
  },
  "num_frames": 121,
  "frame_rate": 24
}
```

## 提示词结构

### 文生视频
```
[主体] + [动作] + [场景] + [镜头运动] + [光照] + [风格]
```

### 图生视频
```
描述哪些内容需要运动 + 哪些主体元素需要保持稳定
```

### 多图视频
```
描述输入图片之间的关系 + 画面如何过渡
```

### 关键帧动画
```
描述关键帧之间的过渡关系
```

## 错误码

| 状态码 | 说明 |
|--------|------|
| 400 | 请求无效，检查参数 |
| 401 | 未授权，检查 API Key |
| 404 | 任务或视频不存在 |
| 500 | 服务器错误 |
| 503 | 服务繁忙 |

## 轮询建议

- 推荐轮询间隔：5 秒
- 使用 `video_id` 查询（推荐）
- 旧版 `task_id` 查询仍支持
