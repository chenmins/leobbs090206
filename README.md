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
