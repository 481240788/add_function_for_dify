# Dify 监测统计接口扩展——部署说明

本项目基于 Dify v1.20.0，对原有 Service API 进行扩展，使第三方系统可以通过 Dify 原生应用 API Key 查询应用监测统计数据。

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

| 接口路径                                      | 功能             |
| --------------------------------------------- | ---------------- |
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
