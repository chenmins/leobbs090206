# 更新日志

本文根据 Git 提交历史整理，记录本项目从原始 LeoBBS 代码导入到 Docker 化、本地运行适配、图片查看修复、反向代理真实 IP 识别等改动。

## 目录

- [2026-06-29](#2026-06-29)
- [2026-06-20](#2026-06-20)
- [2026-06-16](#2026-06-16)
- [2026-06-15](#2026-06-15)
- [2026-06-14](#2026-06-14)
- [2026-06-10](#2026-06-10)
- [初始导入](#初始导入)
- [涉及目录说明](#涉及目录说明)

## 2026-06-29

### 修复皮肤选择中的固定 localhost 资源地址

提交：`1de1c40b`

涉及文件：

- `cgi-bin/data/skinselect.pl`

具体修改：

- 将皮肤选择菜单中的图片地址从固定的 `http://localhost/non-cgi/images/fg.gif` 改为使用 `$imagesurl/images/fg.gif`。
- 修复站点部署在非 localhost、非默认端口或反向代理环境下时，页面请求 `http://localhost/non-cgi/images/fg.gif` 导致 `ERR_CONNECTION_REFUSED` 的问题。

### 统一在线用户真实 IP 获取逻辑

提交：`3564bebe`

涉及文件：

- `cgi-bin/bbs.lib.pl`

具体修改：

- `whosonline` 相关逻辑不再单独读取 `HTTP_CLIENT_IP` 等容易被伪造的请求头。
- 改为统一调用已修复的 `myip()` 方法。
- 在线用户 IP 来源与全站 IP 识别规则保持一致，适配 Caddy/Nginx 反向代理转发的真实公网 IP。

### 改进反向代理环境下的 IP 判断

提交：`3039c02a`

涉及文件：

- `cgi-bin/bbs.lib.pl`
- `cgi-bin/ip.cgi`

具体修改：

- 优先从 `X-Real-IP`、`X-Forwarded-For` 等由 Caddy 或 Nginx 设置的请求头中读取客户端 IP。
- 从 `X-Forwarded-For` 中选择第一个有效公网 IP。
- 过滤 Docker、局域网和内网地址，例如 `192.168.*`、`10.*`、`172.16.*` 到 `172.31.*`。
- 避免记录容器网关、反代内网地址或用户可伪造头部作为真实访问 IP。

### Docker Compose 增加北京时间配置

提交：`1ecdf8c1`

涉及文件：

- `docker-compose.yml`

具体修改：

- 为容器增加时区相关配置，使运行环境使用北京时间。
- 便于论坛日志、发帖时间、在线状态和统计信息与实际使用地区保持一致。

## 2026-06-20

### 外挂所有运行数据目录

提交：`0b3b753d`

涉及文件：

- `Dockerfile`
- `docker-compose.yml`
- `docker-entrypoint.sh`

具体修改：

- 调整 Docker 镜像和启动脚本，进一步将论坛运行时会写入的数据目录外挂到宿主机。
- 降低容器重建、升级或重新部署时丢失论坛数据的风险。
- 精简 `docker-compose.yml` 中的数据挂载配置，让运行数据与镜像内置程序文件边界更清晰。

## 2026-06-16

### 增加外挂目录初始化逻辑

提交：`c9e987fe`

涉及文件：

- `Dockerfile`
- `docker-compose.yml`
- `docker-entrypoint.sh`

具体修改：

- 新增 `docker-entrypoint.sh`。
- 在容器启动时处理外挂目录初始化。
- 调整 Dockerfile 与 Compose 配置，使论坛数据目录可以通过 volume 持久化保存。

### 修复图片查看问题

提交：`047edff0`

涉及文件：

- `cgi-bin/topic.cgi`

具体修改：

- 调整帖子页面中图片查看相关输出逻辑。
- 修复图片信息查看流程中的异常行为。

### 修复“按此查看图片详细信息”无法打开

提交：`26543a63`

涉及文件：

- `cgi-bin/topic.cgi`
- `cgi-bin/view.cgi`

具体修改：

- 修正帖子页与查看页之间的图片详细信息跳转逻辑。
- 修复点击“按此查看图片详细信息”后无法正常打开图片详情的问题。

### 修复安装程序端口识别

提交：`40584f6f`、`7cf4d421`

涉及文件：

- `cgi-bin/install.cgi`

具体修改：

- 调整安装过程中生成论坛访问地址的端口处理逻辑。
- 修复非默认端口部署时生成地址错误的问题。
- 改善 Docker、本地 Apache、反向代理等运行场景下的安装兼容性。

### 安装程序协议自适应

提交：`633f7acb`

涉及文件：

- `cgi-bin/install.cgi`

具体修改：

- 安装时不再固定默认使用 `http`。
- 根据当前请求环境自适应生成访问协议。
- 适配 HTTPS 反向代理部署，避免安装后配置中生成错误的站点地址。

## 2026-06-15

### 图片详细信息查看兼容性修复

提交：`eef501a5`、`e76958f7`

涉及文件：

- `Dockerfile`
- `cgi-bin/ExifTool.pm`
- `cgi-bin/codeno.cgi`
- `cgi-bin/doupload.pl`
- `cgi-bin/getphotoinfo.cgi`
- `cgi-bin/topic.cgi`
- `cgi-bin/view.cgi`

具体修改：

- 调整图片上传、图片信息读取和帖子展示相关代码。
- 修复“按此查看图片详细信息”相关功能。
- 更新 `ExifTool.pm` 及调用链，改善图片元信息读取能力。
- 清理临时打包文件 `xqlbrtchTJnEI.tar`。

## 2026-06-14

### 尝试修复图片信息读取卡死

提交：`ebf314b1`

涉及文件：

- `cgi-bin/getphotoinfo.cgi`
- `cgi-bin/topic.cgi`
- `cgi-bin/view.cgi`

具体修改：

- 针对“正在读取此图片的详细信息，请稍候 ...”长时间卡住的问题进行修复。
- 调整图片详细信息读取页面、帖子页面和查看页面之间的交互逻辑。

### 尝试修复“正在读取，请稍候”卡死

提交：`af1cc57a`

涉及文件：

- `cgi-bin/forums.cgi`
- `cgi-bin/reply_tree.cgi`

具体修改：

- 调整论坛列表和回复树相关页面逻辑。
- 尝试解决页面停留在“正在读取，请稍候”状态的问题。

### 标记项目为老 GB2312/GBK 项目

提交：`55b36b70`

涉及文件：

- `.vscode/settings.json`

具体修改：

- 增加编辑器配置，用于适配老项目的 GB2312/GBK 编码。
- 降低直接编辑 Perl/CGI 源码时出现中文乱码的概率。

## 2026-06-10

### 移除链接 hover 的上划线效果

提交：`6ec43d80`

涉及文件：

- `cgi-bin/data/template/leobbs.cgi`
- `cgi-bin/data/template/title.cgi`

具体修改：

- 去掉 `A:hover{TEXT-DECORATION: underline overline}` 中的 overline 效果。
- 保留更常规的 hover 下划线样式，改善页面视觉表现。

### 启用伪静态支持

提交：`4ae13469`

涉及文件：

- `.dockerignore`
- `Dockerfile`
- `README.md`

具体修改：

- 在 Docker Apache 环境中启用 `mod_rewrite`。
- 支持 `.htaccess` 规则，让 LeoBBS 的伪静态功能可以在容器中运行。
- 更新 README 中的运行说明。

### 修复 Docker 中 `/non-cgi/` 静态资源 404

提交：`babafd07`

涉及文件：

- `Dockerfile`

具体修改：

- 调整 Apache `DocumentRoot` 或相关路径配置。
- 修复容器中访问 `/non-cgi/` 静态资源时出现 404 的问题。

### 增加 Docker 支持

提交：`d6ee2ccc`

涉及文件：

- `.dockerignore`
- `Dockerfile`
- `docker-compose.yml`
- `README.md`

具体修改：

- 新增 Dockerfile，用于构建可运行 LeoBBS 的 Apache/Perl 环境。
- 新增 `docker-compose.yml`，简化本地启动流程。
- 新增 `.dockerignore`，减少构建上下文中不必要文件。
- 新增 README，说明项目运行方式、Docker 启动方式和基础目录结构。

## 初始导入

提交：`37353a98`

主要内容：

- 导入 LeoBBS 090206 原始项目文件。
- 包含 CGI/Perl 程序、论坛模板、静态资源、头像、表情、皮肤、字体图片、转换工具和历史说明文档。

主要目录：

- `cgi-bin/`：论坛核心 CGI/Perl 程序、配置、模板、缓存目录、安装程序和管理功能。
- `non-cgi/`：图片、头像、表情、图标、皮肤资源、静态脚本和其他公开静态文件。
- `addon/`：插件、附加 Perl 模块和扩展资源。
- `conv/`：其他论坛系统迁移到 LeoBBS 的转换脚本。
- 根目录历史文档：安装、注册、伪静态、虚拟主机、安全、插件、模板和用户格式说明。

## 涉及目录说明

### 根目录

- `Dockerfile`：定义容器运行环境，包括 Apache、Perl、CGI 支持和相关路径配置。
- `docker-compose.yml`：定义容器启动方式、端口、时区和数据挂载。
- `docker-entrypoint.sh`：处理容器启动前的数据目录初始化和外挂目录准备。
- `.dockerignore`：控制 Docker 构建上下文。
- `README.md`：项目运行和 Docker 使用说明。

### `cgi-bin/`

- 论坛核心程序目录。
- 本轮历史中主要修改了安装、帖子展示、图片详情、IP 识别、在线用户统计、论坛列表和模板相关脚本。
- 重点文件包括：
  - `install.cgi`：安装流程、协议和端口自适应。
  - `bbs.lib.pl`：公共函数与真实 IP 识别。
  - `ip.cgi`：IP 显示与判断逻辑。
  - `topic.cgi`、`view.cgi`、`getphotoinfo.cgi`：帖子图片展示和图片详细信息读取。
  - `forums.cgi`、`reply_tree.cgi`：论坛列表和回复树读取状态修复。
  - `data/skinselect.pl`：皮肤切换菜单资源地址修复。
  - `data/template/`：页面模板样式调整。

### `non-cgi/`

- 公开静态资源目录。
- Docker 化过程中重点修复了 `/non-cgi/` 在容器中的访问路径，避免图片、皮肤、图标等资源 404。

### `addon/`

- 附加模块和插件目录。
- 初始导入中包含 CGI、Net、HTTP、DNS 等 Perl 模块和插件资源。

### `conv/`

- 论坛数据转换脚本目录。
- 初始导入中包含从 Discuz、vBulletin、YaBB、UBB 等系统迁移到 LeoBBS 的脚本或压缩包。

### `.vscode/`

- 编辑器配置目录。
- 增加了对老 GB2312/GBK 项目的编码适配配置。
