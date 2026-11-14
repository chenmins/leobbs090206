# LeoBBS 移动端 API

手机版与 Apache CGI 同域部署，使用 UTF-8 JSON。公开读取范围由 `LEOBBS_MOBILE_PUBLIC_BOARDS` 和论坛权限共同限定。API 响应使用 `Cache-Control: no-store`。

| 方法与路径 | 返回内容 |
| --- | --- |
| `GET /api/v1/home` | `boards`、`latest` 和全站 `stats` |
| `GET /api/v1/boards/{boardId}` | `board`、分页主题 `items`、热门阈值 `hotTopicMark` |
| `GET /api/v1/boards/{boardId}/topics/{topicId}` | `board`、`topic`、分页楼层 `items` |
| `GET /api/v1/search` | 匹配主题的分页 `items` 和公开 `boards` |
| `POST /api/v1/legacy-form` | 将 UTF-8 表单转为原版 CGI 使用的 GBK 百分号编码，返回 `{"form":"..."}` |

版块、主题和搜索接口接受 `page`，从 1 开始，每页 20 条，并返回 `page`、`pages` 和 `items`。超出末页时返回空列表。主题包含 `id`、`title`、`author`、`replies`、`views`、`created`、`updated`、`state`、`icon`、`pinned`、`hot`、`recent`。时间戳单位为秒。楼层包含 `floor`、`author`、`created`、`body`、`ubb`、`desktopOnly`、`edit`、`profile`。当 `desktopOnly` 为真时，通过经典版查看。编辑记录和作者资料可能为 `null`。

首页、版块和帖子详情请求可带 `count=1`，分别计入全站点击。手机版会话第一次计数同时增加访问数，帖子详情还增加该主题的点击数。省略该参数可读取而不增加统计。

搜索参数为 `q`（1–80 字符，逗号分隔多个词）、`mode`（`title`、`body`、`both`、`author`、`reply_author`、`all_authors`）、可重复的 `board`、`days`（`any`、1、7、14、30、90、180、365）和 `when`（`before` 或 `after`）。日期按主题发表时间筛选。

登录、注册、发帖、编辑、删除和站内信仍由经典 CGI 校验权限并处理。浏览器在同域请求中携带论坛 Cookie。以下是手机版调用的附加读取接口。

| 入口 | 用途 |
| --- | --- |
| `/cgi-bin/loginout.cgi?action=mobilestatus` | GBK 文本，登录时返回 `LEOBBS_MEMBER:用户名` |
| `/cgi-bin/loginout.cgi?action=mobileprofile` | 当前会员的个人状态 JSON |
| `/cgi-bin/delpost.cgi?action=mobilepermissions&forum=1&topic=3` | 按楼层返回 `canEdit` 和 `canDelete` |
| `/cgi-bin/messanger.cgi?action=mobileinbox` 或 `mobileoutbox` | 当前信箱，支持 `page`，`summary=1` 只返回统计而不返回信件内容 |
| `/cgi-bin/friendlist.cgi?action=mobilelist` 或 `blocklist.cgi?action=mobilelist` | 当前账号的好友录或黑名单 |

`/api/v1/` 的错误响应包含 `error` 字段。常见状态码为 400 参数无效、404 资源不可见或不存在、405 方法错误、413 表单过大、422 字符无法转换为 GBK、500 读取失败。经典 CGI 的操作响应仍可能是 GBK HTML。

## AI / Agent 接入

官方 SDK 实现的游客只读 MCP 见 [MCP 说明](../mcp/README.md)。它复用上述 API，不单独读取论坛文件。工具支持版块浏览、搜索和分页阅读；调用不携带 Cookie、不传 `count=1`。目前没有 JSON 发帖/回复写接口或 Agent Token，不能把 `legacy-form` 当作写入 API。
