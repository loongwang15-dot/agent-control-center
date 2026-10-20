# Lovart 狮子主题艺术海报｜2026-10-20

## 状态

- 最终产出：**PASS**
- 平台：Lovart（现有已登录页面，Playwright MCP Extension）
- 任务：生成 1 张竖版狮子主题艺术海报
- 输出：1024×1536 PNG，2:3 竖版，2,596,128 bytes
- SHA-256：`7F40F10479490DA7FF422ACC6320EAA1C48C543AA2D650FB9D8D0B3DE408A74B`
- 实际积分扣减：**UNVERIFIED**（提交前按钮标价 8；成功页未显示实时余额）

## 最终成品

- 项目归档：`deliverables/狮子主题艺术海报_Lovart_2026-10-20.png`
- 浏览器下载原文件：`C:\Users\AB\Downloads\1792507931892.png`

## 实际执行

1. Playwright MCP 定位现有 Lovart 项目标签，读取到 GPT Image 2、图像模式、1 张和可视生成按钮。
2. 首次设置为“中 · 2:3 · 1 张”，提交一段带英文标题与杂志封面描述的较长提示词。
3. Lovart 返回“请求违反内容政策”，页面明确写明“本次操作不消耗积分”；没有生成图片。
4. 新建干净对话，改为无文字、无品牌元素的简洁狮子艺术海报描述，保持“中 · 2:3 · 1 张”。
5. 第二次提交后页面进入“生成中”，约 20 秒后完成并显示可打开作品。
6. 打开预览、点击“下载”；本地出现 `1792507931892.png`，尺寸、体积、哈希和画面均已核验。

## 视觉结果

成年雄狮侧面半身构图，金色夕照勾勒鬃毛，背景为暖橙与深棕草原日落，顶部与底部留有空间。画面无额外文字、水印或品牌标志，整体为电影摄影感的竖版视觉海报。

## 浏览器交互说明

本轮 Lovart 的多个普通按钮仍重复出现 Playwright actionability 超时，日志停在等待“visible/enabled/stable”。只读诊断确认生成按钮 `disabled=false`、`visibility=visible`、`opacity=1`、`pointer-events=auto`，中心无透明层遮挡。

在连续两次同类点击失败后，停止普通点击重试；改用 Playwright 对已核验为可点击的按钮执行 `force: true`。没有把“点击调用返回成功”当作验收依据，最终以页面进入“生成中”、作品出现、预览可打开、下载文件存在和尺寸可读作为 PASS 证据。

## 证据

- `.p1-codex-lovart/lovart-lion-poster-submit-2026-10-20.png`：首次长提示词提交前画面。
- `.p1-codex-lovart/lovart-lion-poster-retry-submit-2026-10-20.png`：简化提示词提交前画面。
- `.p1-codex-lovart/lovart-lion-poster-complete-2026-10-20.png`：作品完成并打开预览后的页面截图。
- `C:\Users\AB\Downloads\1792507931892.png`：浏览器下载原文件。

## 边界

- 未读取账号身份、Cookie、Token 或支付信息。
- 未购买会员、未发布、未进行额外重新生成。
- 首次内容政策失败由平台返回，未确认触发该误判的具体词句。
- 成功生成的实时积分余额未从页面读取，因此只记录提交前标价 8，不声称实际扣费数值。
