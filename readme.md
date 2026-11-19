
# Dify Statistics API Extension

基于**Dify v1.20.0**的Service API监测统计接口扩展项目。

## 项目背景

Dify原生Console API已具备应用监测统计功能，可以在管理后台查看消息数量、会话数量、终端用户数、Token消耗以及响应性能等数据。

但Dify的Service API默认没有开放对应的统计查询接口，第三方程序无法直接使用应用API Key获取这些数据。

本项目通过对 Dify 进行轻量级二次开发，**复用原生API Key鉴权机制和统计Service，新增 8 个应用级的 RESTful 统计接口**，使第三方系统无需使用 Console 登录凭据，即可查询对应应用的监测数据。

## 项目特点

- **原生鉴权：** 使用 Dify 应用 API Key，无需引入额外认证机制。
- **应用级数据隔离：** 使用鉴权得到的应用 ID 进行统计查询。
- **复用统计服务：** 不重新实现数据库聚合逻辑。
- **8 个统计接口：** 涵盖消息量、用户数、Token 消耗及响应性能。
- **容器化部署：** 支持 Docker 自定义镜像与 Docker Compose 配置覆盖。
- **功能验证：** 已完成 13 项基础自动化检查及 8 个指标与 Console 的数据一致性核对。

**适用版本：** Dify v1.20.0

**注意：** 本项目是第三方二次开发扩展，并非 Dify 官方内置功能。

## 部署说明

本项目基于 **Dify v1.20.0**，通过二次开发扩展原生 Service API，增加 8 个应用监测统计接口。

根据是否已经部署 Dify，请选择对应方式：

- **首次部署用户**：先完成下方的 Dify 环境安装和初始化，再进行源码修改与镜像构建。
- **已有 Dify 环境的用户**：确认版本为 v1.20.0 后，可直接跳转至「修改源码」。

### 一、首次部署 Dify

#### 1. 安装 Docker 环境

首先确保系统已经安装 Docker Engine 和 Docker Compose。

检查版本：

```bash
docker --version
docker compose version
```

确保 Docker 服务正常运行：

```bash
docker ps
```

如未安装，请参考 [Docker 官方安装文档](https://docs.docker.com/engine/install/)。

#### 2. 下载 Dify 官方源码

本扩展基于 Dify v1.20.0 开发，建议使用相同版本，避免不同版本之间出现接口注册方式或依赖不兼容的问题。

```bash
git clone https://github.com/langgenius/dify.git
cd dify
git checkout 1.20.0
```

#### 3. 初始化 Docker Compose 配置

进入 Docker 部署目录：

```bash
cd docker
cp .env.example .env
```

根据对应版本的 `.env.example` 和官方 Docker 部署文档，完成必要的环境变量配置。

如使用该版本要求的 Agent Sandbox Token，请执行：

```bash
openssl rand -hex 32
```

将生成的随机字符串填入 `.env` 中对应的 `DIFY_AGENT_LOCAL_SANDBOX_AUTH_TOKEN`。

**注意：** 不同 Dify 版本的环境变量结构可能有所不同，应以当前检出的 v1.20.0 版本为准。

#### 4. 启动原版 Dify

首次部署时，需要启动完整的 Dify 服务，而不只是 API 容器。

```bash
docker compose up -d
```

首次执行时，Docker 会下载所需镜像、创建网络和数据卷，并启动各个服务。

查看容器状态：

```bash
docker compose ps -a
```

根据容器日志确认主要服务正常运行。

#### 5. 初始化 Dify 管理后台

默认 HTTP 端口为 80，具体以 Docker Compose 配置为准。

本机访问：

```text
http://localhost/install
```

如果部署在虚拟机或远程服务器中，可以通过对应 IP 地址访问：

```text
http://<服务器IP>/install
```

按照页面提示创建管理员账号。

进入 Dify 管理后台后，确认能够正常创建和访问应用，即表示基础环境部署完成。

### 二、安装本项目的统计接口扩展

Dify 基础环境正常运行后，继续按照本文后续章节操作：

1. 下载 `add_function_for_dify` 扩展仓库。
2. 将 `statistic.py` 添加到对应目录。
3. 修改或替换 `service_api/__init__.py`。
4. 重新构建自定义 API 镜像。
5. 使用 Docker Compose 覆盖 API 服务镜像。
6. 重新创建 API 容器。
7. 使用应用 API Key 测试新增统计接口。

### 三、首次部署与已有部署的区别

| 项目                  | 首次部署 | 已有部署     |
| --------------------- | -------- | ------------ |
| 下载 Dify 源码        | 需要     | 视情况       |
| 配置 `.env`         | 需要     | 保留现有配置 |
| 启动完整 Dify 服务    | 需要     | 通常不需要   |
| 初始化管理后台        | 需要     | 不需要       |
| 修改 Service API 源码 | 需要     | 需要         |
| 构建自定义镜像        | 需要     | 需要         |
| 替换 API 容器         | 需要     | 需要         |

**重要说明：**

- 首次部署时不能只运行 `docker compose up -d --no-deps api`，因为数据库、Redis 等依赖服务可能尚未创建。
- 已有部署环境不要直接覆盖原来的 `.env` 文件。
- 修改源码后必须重新构建 API 镜像，才能使新增接口生效。
- 如果应用没有产生消息或会话数据，统计接口可能正常返回空结果，这不一定是程序错误。

## 首次部署 Dify（未部署过的用户）

如果尚未安装和部署 Dify，需要先完成以下步骤，再按照后续章节进行 Service API 扩展。

### 1. 安装 Docker 和 Docker Compose

首先确保系统已安装 Docker Engine 和 Docker Compose。

```bash
docker --version
docker compose version
```

如果尚未安装，请参考 [Docker 官方安装文档](https://docs.docker.com/engine/install/)。

### 2. 下载 Dify 源码

本项目适用于 **Dify v1.20.0**，(之前版本暂未测试，但是应该大差不差)建议使用对应版本的源码。

```bash
git clone --branch 1.20.0 --depth 1 https://github.com/langgenius/dify.git
cd dify
```

### 3. 初始化 Docker Compose 配置

进入 Docker 部署目录：

```bash
cd docker
cp .env.example .env
```

根据实际需要修改 `.env` 中的配置，例如服务端口和相关密钥。具体配置要求以当前 Dify 版本为准。

### 4. 启动 Dify

首次部署需要启动完整的 Dify 服务，包括 API、Worker、Web、PostgreSQL、Redis 等组件。

```bash
docker compose up -d
```

首次启动时会自动拉取相关 Docker 镜像，可能需要一定时间。

检查容器运行状态：

```bash
docker compose ps
```

### 5. 初始化 Dify 管理后台

容器正常启动后，在浏览器访问：

```text
http://localhost/install
```

如果部署在虚拟机或远程服务器中，需要使用对应的 IP 地址：

```text
http://<服务器IP>/install
```

按照页面提示创建管理员账号，完成 Dify 初始化。

### 6. 继续安装本项目扩展

确认 Dify 能够正常访问后，返回源码根目录：

```bash
cd ..
```

接下来按照下方的 **「一、修改源码」** 及后续章节操作，添加统计接口、构建自定义 API 镜像并更新 Docker Compose 配置。

**注意：** 首次部署需要先启动完整的 Dify 服务。后续章节中的 `--no-deps --force-recreate api` 仅用于重新创建 API 容器，不能代替首次部署过程。

## 一、修改源码

### 1. 新增统计接口文件

将 `folder` 文件夹中的 `statistic.py` 复制到 Dify 项目中的以下目录：

```
dify/api/controllers/service_api/app/statistic.py
```

如果目标目录中不存在同名文件，直接复制即可。

### 2. 修改 `__init__.py`

需要修改的文件：

```
dify/api/controllers/service_api/__init__.py
```

**方式一：直接替换**

将 `folder` 中提供的 `__init__.py` 复制到上述目录，替换原文件。

注意：此方式仅适用于对应版本的 Dify。如果原文件已经存在其他自定义修改，建议采用方式二，避免覆盖其他代码。

**方式二：手动修改**

只需要在 `__init__.py` 中的以下四处加入 `statistic`：

1. `.app` 模块的导入列表。
2. `_register_controllers()` 函数的返回元组。
3. `_register_controllers()` 调用结果的解包元组。
4. `__all__` 导出列表。

例如，在 `.app` 模块导入列表中增加：

```
from .app import (
    # 原有模块
    statistic,
)
```

其余三处按照原有代码结构增加 `statistic`，保持变量顺序和返回值顺序一致即可。

## 二、重新构建 Docker 镜像

完成源码修改后，返回dify文件夹根目录；

构建自定义 API 镜像：

```
docker build \
  -f api/Dockerfile \
  -t dify-api-change:latest \
  .
```

构建成功后，可以查看镜像：

```
docker images | grep dify-api-change
```

## 三、更新 Docker Compose 配置

进入 Docker Compose 目录：

```
cd docker
```

新建文件：

```
docker-compose.custom.yaml
```

内容如下：

```
services:
  api:
    image: dify-api-change:latest
```

此文件用于覆盖默认 Compose 配置中 API 服务使用的镜像，不需要修改原有 `docker-compose.yaml`。

## 四、重新创建 API 容器

在 `docker` 目录下执行：

```
docker compose \
  -f docker-compose.yaml \
  -f docker-compose.custom.yaml \
  up -d --no-deps --force-recreate api
```

该命令只重新创建 API 服务，不会主动重建数据库等其他服务。

检查容器状态：

```
docker compose \
  -f docker-compose.yaml \
  -f docker-compose.custom.yaml \
  ps api
```

如果启动异常，查看日志：

```
docker compose \
  -f docker-compose.yaml \
  -f docker-compose.custom.yaml \
  logs --tail=100 api
```

## 五、测试新增统计接口

以调用每日消息数统计接口为例：

首先在 Dify 中打开需要查询的应用，进入 **API 访问** 页面，生成或获取应用 API Key。

设置环境变量：

```
read -rsp "Dify API Key: " DIFY_API_KEY
echo
export DIFY_API_KEY
```

调用每日消息数统计接口：

```
curl -G \
  "http://localhost/v1/statistics/daily-messages" \
  -H "Authorization: Bearer $DIFY_API_KEY" \
  --data-urlencode "start=2026-11-01 00:00" \
  --data-urlencode "end=2026-11-20 00:00" \
  --data-urlencode "timezone=Asia/Shanghai"
```

成功时，返回格式类似：

```
{
  "data": [
    {
      "date": "2026-11-19",
      "message_count": 4
    }
  ]
}
```

统计值根据实际应用数据变化。

## 六、新增接口列表

所有接口均采用 GET 方法，并使用应用 API Key 进行认证。

| 接口路径                                        | 功能             |
| ----------------------------------------------- | ---------------- |
| `/v1/statistics/daily-messages`               | 每日消息数       |
| `/v1/statistics/daily-conversations`          | 每日会话数       |
| `/v1/statistics/daily-end-users`              | 每日终端用户数   |
| `/v1/statistics/token-costs`                  | Token 消耗及费用 |
| `/v1/statistics/average-session-interactions` | 平均会话交互次数 |
| `/v1/statistics/user-satisfaction-rate`       | 用户满意度       |
| `/v1/statistics/average-response-time`        | 平均响应时间     |
| `/v1/statistics/tokens-per-second`            | Token 生成速度   |

**注意事项：**

- `average-response-time` 接口仅支持对应的 Completion 应用模式，不支持时会返回 HTTP 400。
- 统计数据根据 API Key 所属应用确定。
- 修改 Python 源码后，需要重新构建镜像并重新创建 API 容器，修改才会在容器中生效。
