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

---

# 部署说明

本项目基于 Dify v1.20.0，对原有 Service API 进行扩展，使第三方系统可以通过 Dify 原生应用 API Key 查询应用监测统计数据。

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

本项目适用于 **Dify v1.20.0**，建议使用对应版本的源码。

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

根据实际需要修改 `.env` 中的配置，例如服务端口和相关密钥。

关于`DIFY_AGENT_LOCAL_SANDBOX_AUTH_TOKEN`使用：

```Shell
openssl rand -hex 32
```

随机生成即可。

具体配置要求以当前 Dify 版本为准。

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
| `/v1/statistics/user-satisfaction-rate`       | 用户满意         |
| `/v1/statistics/average-response-time`        | 平均响应时间     |
| `/v1/statistics/tokens-per-second`            | Token 生成速度   |

**注意事项：**

- `average-response-time` 接口仅支持对应的 Completion 应用模式，不支持时会返回 HTTP 400。
- 统计数据根据 API Key 所属应用确定。
- 修改 Python 源码后，需要重新构建镜像并重新创建 API 容器，修改才会在容器中生效。

## 兼容性说明

本项目基于 **Dify v1.20.0** 开发，并已在该版本下完成接口功能及数据一致性验证。

- **支持版本：** Dify v1.20.0。
- **其他版本：** 尚未进行兼容性验证，不保证直接适用。
- **部署方式：** 修改 Dify 后端源码并重新构建 API Docker 镜像。
- **升级注意事项：** 本项目依赖 Dify 内部 Controller 注册机制及 App Statistics Service。升级 Dify 后，应检查相关源码结构及方法签名，并重新执行测试。

建议在应用本项目之前备份原有修改文件，并使用与目标 Dify 版本对应的源码。

## 安全说明

本项目复用 Dify 原生应用 API Key 鉴权机制，无需单独管理统计接口的访问令牌。

**需要注意的是，安装本扩展后，持有有效应用 API Key 的调用方也将能够查询该应用的监测统计数据。**

因此，建议遵循以下原则：

1. 不要将真实 API Key 提交到公开 GitHub 仓库。
2. 不要在浏览器前端代码中直接保存应用 API Key。
3. 为不同应用分别管理 API Key，并遵循最小权限原则。
4. 对第三方调用方谨慎授权，必要时增加独立的统计只读鉴权层。
5. 在正式环境部署前，执行鉴权、跨应用数据隔离及回归测试。

本项目已验证无效密钥、撤销密钥的访问限制，并完成 7 个适用统计接口的跨应用隔离测试。上述验证不构成完整的安全审计。

## 自动化测试

项目提供独立的 Python 测试脚本，涵盖接口功能、身份认证、参数校验、跨应用数据隔离、密钥撤销及 Completion 模式专项测试。

详细配置与运行方式参见 [测试说明](statistics_tests/README.md)。
