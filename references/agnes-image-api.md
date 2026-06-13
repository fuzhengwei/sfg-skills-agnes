# Agnes Image 2.1 Flash API 参考文档

## API 信息

| 项目 | 说明 |
|------|------|
| Endpoint | `POST https://apihub.agnes-ai.com/v1/images/generations` |
| 模型名称 | `agnes-image-2.1-flash` |
| 认证方式 | Bearer Token |
| 价格 | $0.003/张 |

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 是 | 固定 `agnes-image-2.1-flash` |
| prompt | string | 是 | 图片生成或编辑提示词 |
| size | string | 是 | 输出图片尺寸，如 `1024x768` |
| image | string[] | 图生图必填 | 输入图片数组，支持公网 URL 或 Data URI Base64 |
| return_base64 | boolean | 否 | 文生图需要返回 Base64 时使用 |
| extra_body | object | 否 | 高级工作流扩展参数 |
| extra_body.response_format | string | 否 | 输出格式：`url` 或 `b64_json` |
| extra_body.image | string[] | 否 | 图生图时的输入图片数组 |

## 重要注意事项

1. **`response_format` 必须放在 `extra_body` 中**，放请求体顶层会报 400 错误
2. **图生图不需要 `tags: ["img2img"]`**
3. **图生图输入图片放在顶层 `image` 数组**中
4. **文生图 Base64 输出**：使用顶层 `return_base64: true`
5. **图生图 Base64 输出**：使用 `extra_body.response_format: "b64_json"`
6. 输入图片 URL 必须公网可访问，如不可访问使用 Data URI Base64

## 返回格式

### URL 输出

```json
{
  "created": 1780000000,
  "data": [
    {
      "url": "https://storage.googleapis.com/agnes-aigc/xxx.png",
      "b64_json": null,
      "revised_prompt": null
    }
  ]
}
```

### Base64 输出

```json
{
  "created": 1780000000,
  "data": [
    {
      "url": null,
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAA...",
      "revised_prompt": null
    }
  ]
}
```

## 推荐提示词结构

### 文生图

```
[主体] + [场景/环境] + [风格] + [光照] + [构图] + [质量要求]
```

示例：
```
A luminous floating city above a misty canyon at sunrise, cinematic realism, wide-angle composition, rich architectural details, soft golden light, high visual density
```

### 图生图

```
[修改要求] + [新风格/新场景] + [添加/移除的元素] + [需要保留的元素]
```

示例：
```
Transform the scene into a rain-soaked cyberpunk night with neon reflections while preserving the original composition and main subject layout
```

## 错误码

| 状态码 | 说明 |
|--------|------|
| 400 | 请求无效，检查参数（特别是 response_format 位置） |
| 401 | 未授权，检查 API Key |
| 500 | 服务器错误 |
| 503 | 服务繁忙 |

## 超时建议

- 客户端超时设置：60s - 360s
