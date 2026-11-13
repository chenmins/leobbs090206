# LeoBBS 论坛系统

LeoBBS 是一个基于 Perl CGI 的经典论坛系统。本项目提供了 Docker 容器化部署方案，让您可以快速启动和运行 LeoBBS 论坛。

## 环境要求

- [Docker](https://docs.docker.com/get-docker/) (版本 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (版本 2.0+)

## 快速启动

### 1. 克隆项目

```bash
git clone https://github.com/chenmins/leobbs090206.git
cd leobbs090206
```

### 2. 使用 Docker Compose 启动

```bash
docker compose up -d
```

> 如果您使用的是旧版 Docker Compose，请使用 `docker-compose up -d`

### 3. 访问论坛

启动成功后，在浏览器中访问：

- **论坛首页**: [http://localhost:8080/cgi-bin/leobbs.cgi](http://localhost:8080/cgi-bin/leobbs.cgi)
- **管理后台**: [http://localhost:8080/cgi-bin/admin.cgi](http://localhost:8080/cgi-bin/admin.cgi)

## 常用命令

```bash
# 启动服务（后台运行）
docker compose up -d

# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止服务
docker compose down

# 重新构建并启动（修改 Dockerfile 后）
docker compose up -d --build

# 完全清理（包括数据卷）
docker compose down -v
```

## 数据持久化

以下数据目录通过 Docker 卷进行持久化存储，即使容器重建数据也不会丢失：

| 卷名 | 容器路径 | 说明 |
|------|---------|------|
| `leobbs_data` | `/var/www/html/cgi-bin/data` | 论坛配置数据 |
| `leobbs_members` | `/var/www/html/cgi-bin/members` | 用户数据 |
| `leobbs_messages` | `/var/www/html/cgi-bin/messages` | 站内消息 |
| `leobbs_boarddata` | `/var/www/html/cgi-bin/boarddata` | 版块数据 |
| `leobbs_usr` | `/var/www/html/non-cgi/usr` | 用户上传文件 |

## 自定义配置

### 修改端口

编辑 `docker-compose.yml`，将 `8080:80` 中的 `8080` 修改为您需要的端口：

```yaml
ports:
  - "自定义端口:80"
```

### 仅使用 Docker（不使用 Compose）

```bash
# 构建镜像
docker build -t leobbs .

# 运行容器
docker run -d \
  --name leobbs-forum \
  -p 8080:80 \
  --restart unless-stopped \
  leobbs
```

## 故障排除

### URL 伪静态

Docker 镜像已内置 mod_rewrite 和 `.htaccess` 支持，伪静态 URL 开箱即用。例如：

- `topic-1-2-3-4-5.htm` → `topic.cgi?forum=1&topic=2&start=3&show=4&replynum=5`
- `leobbs.htm` → `leobbs.cgi`
- `profile-username.htm` → `profile.cgi?action=show&member=username`

### 查看 Apache 错误日志

```bash
docker compose exec leobbs cat /var/log/apache2/error.log
```

### 进入容器内部调试

```bash
docker compose exec leobbs bash
```

### 权限问题

如果遇到 "Permission denied" 错误，可以进入容器重新设置权限：

```bash
docker compose exec leobbs chown -R www-data:www-data /var/www/html
```

## 技术架构

- **操作系统**: Debian Bullseye (Slim)
- **Web 服务器**: Apache 2
- **运行环境**: Perl CGI
- **端口**: 容器内部 80，对外映射 8080

## 许可证

请参阅项目原始许可协议。

## Vue 3 手机站与 JSON API

在本地论坛安装并建立公开版块后，打开 [手机版](http://127.0.0.1:8080/m/)。
Compose 以多阶段构建编译 `mobile/web`，独立的 Perl CGI 位于 `mobile/api`。两个程序同域部署，Vue 不读取论坛文件。

`LEOBBS_MOBILE_PUBLIC_BOARDS` 是以逗号分隔的公开版块编号，本地默认 `1`。只填写允许游客阅读的版块。接口额外排除隐藏、私有、子版块、受密码保护或带独立样式配置的版块。关闭旧站游客阅读时，API 也不返回版块。

| 路径 | 用途 |
| --- | --- |
| `GET /api/v1/home` | 公开版块和最新主题 |
| `GET /api/v1/boards/{id}?page=1` | 版块及其主题，每页 20 条 |
| `GET /api/v1/boards/{id}/topics/{id}?page=1` | 主题及楼层，每页 20 条 |

API 将旧数据按 CP936（GBK）严格解码，输出 UTF-8 JSON。手机版以文本或有限的 UBB 标签显示正文，支持粗体、斜体、下划线、引用和代码块。包含旧站特殊标记的楼层提供经典版入口。手机版提供登录、发帖和回复表单，提交仍使用原 CGI 验证账号、权限并写入数据。手机版支持按公开版块的帖子标题搜索。

如果本机无法拉取默认镜像，可以指定镜像地址再构建。

```sh
LEO_BBS_BASE_IMAGE=docker.m.daocloud.io/library/debian:trixie-slim \
LEO_BBS_NODE_IMAGE=docker.m.daocloud.io/library/node:22-bookworm-slim \
docker compose up -d --build
```

本地测试版块命名为「站务公告区」时，可运行 `python3 mobile/tests/smoke.py`。如果版块已有主题，检查也会读取首个主题及其楼层。

### 搜索引擎抓取

Apache 镜像提供动态的 `/robots.txt` 和 `/sitemap.xml`。通过 Caddy 发布时，在 Compose 环境中把 `LEOBBS_PUBLIC_ORIGIN` 设置为浏览器使用的公网源地址，例如 `https://forum.example.com`。未设置时使用安装配置中的论坛地址。首页用相对 Location 跳转，HTTPS 由 Caddy 负责。

站点地图使用经典版的伪静态地址。镜像启用 Apache 重写，即使已有持久化目录没有新版重写文件，站点地图中的三类地址也可解析。地图每次按当前数据生成。具有独立配置的版块、子版块及带访问控制标记的帖子暂不列入。
