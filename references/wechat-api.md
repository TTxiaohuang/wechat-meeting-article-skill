# 微信 API 说明

仅在用户要求创建公众号草稿或对接发布流程时参考本文件。

## 推荐流程

1. 用公众号的 `appid` 和 `secret` 获取并缓存 `access_token`。
2. 根据选择的发布路径，用图片上传接口或永久素材接口上传正文图片。
3. 用草稿箱 API 创建草稿。
4. 发送预览或打开平台草稿供人工审核。
5. 明确批准后才发布。

## 草稿请求字段

常用的字段包括：

- `title`
- `author`
- `digest`
- `content`
- `content_source_url`
- `thumb_media_id`
- `need_open_comment`
- `only_fans_can_comment`

## 安全规则

- 不要将 `appid`、`secret`、token、cookie 或账号凭据硬编码到技能中。
- API 代码与渲染器代码分离。
- 实际部署中 IP 白名单、认证状态、频率限制、token 过期和账号权限都可能失败。
- 保存草稿请求 payload 用于调试，但日志中要脱敏。
- 优先使用干运行模式，输出 `wechat_draft_payload.json`。
