# Dify Statistics API — 测试说明

## 1. 项目概述

本目录提供针对 **Dify v1.20.0 Service API 统计接口扩展**的自动化测试脚本，用于验证新增统计接口的功能正确性、身份认证、请求参数校验、跨应用数据隔离以及 API Key 撤销后的访问控制行为。

所有测试均通过 HTTP 请求访问已部署的 Dify 服务

## 2. 测试范围

项目共提供六组独立测试，覆盖以下内容：

| 测试脚本                  | 测试内容            | 预期行为                                             |
| ------------------------- | ------------------- | ---------------------------------------------------- |
| `test_01_functional.py` | 统计接口功能测试    | 有效请求返回正确的 HTTP 状态码和数据结构             |
| `test_02_auth.py`       | API Key 鉴权测试    | 无效或缺失 API Key 时返回 HTTP 401                   |
| `test_03_params.py`     | 请求参数校验测试    | 非法日期、时区及时间范围返回 HTTP 400                |
| `test_04_isolation.py`  | 跨应用数据隔离测试  | 应用 A 的密钥不能通过指定应用 B 的 ID 获取其统计数据 |
| `test_05_revoked.py`    | API Key 撤销测试    | 已撤销的密钥访问所有统计接口时均返回 HTTP 401        |
| `test_06_completion.py` | Completion 专项测试 | 平均响应时间接口返回有效统计数据                     |

此外，`common.py` 封装通用请求及结果检查逻辑，`run_all.py` 提供统一测试入口。

## 3. 环境要求

测试前应确保以下条件已满足：

- 已部署 Dify v1.20.0，并完成统计 Service API 扩展。
- Dify API 服务处于正常运行状态，能够通过 HTTP 访问。
- 本地已安装 Python 3.10 或更高版本。
- 已准备至少一个可正常调用的 Dify 应用及其有效 API Key。
- 跨应用隔离测试需要两个独立应用。
- Completion 专项测试需要一个文本生成（Completion）应用。

建议在独立的测试环境中执行，避免测试产生的数据影响生产环境的监测统计结果。

## 4. 环境变量配置

测试脚本使用环境变量管理服务地址、查询时间及 API Key，避免在源码中保存敏感信息。

### 4.1 配置 Dify 服务地址

```bash
export DIFY_BASE_URL="http://localhost"
```

如果 Dify 部署在远程服务器，应将 `localhost` 替换为实际可访问的服务地址。

### 4.2 配置统计时间范围

```bash
export DIFY_START="2026-11-01 00:00"
export DIFY_END="2026-11-20 00:00"
export DIFY_TIMEZONE="Asia/Shanghai"
```

上述时间范围仅为测试示例，可根据实际数据调整。

为保证测试结果有效，建议选择存在真实调用记录的时间段。

### 4.3 配置应用 API Key

首先配置 Advanced Chat 应用 A 的有效 API Key：

```bash
read -rsp "App A API Key: " DIFY_APP_A_KEY
echo
export DIFY_APP_A_KEY
```

如需执行跨应用隔离测试，还应配置应用 B 的 API Key 和应用 ID：

```bash
read -rsp "App B API Key: " DIFY_APP_B_KEY
echo
export DIFY_APP_B_KEY

export DIFY_APP_B_ID="应用B的实际UUID"
```

如需执行 Completion 专项测试，还应配置 Completion 应用的 API Key：

```bash
read -rsp "Completion API Key: " DIFY_COMPLETION_KEY
echo
export DIFY_COMPLETION_KEY
```

API Key 撤销测试需要单独配置一枚**已经撤销的临时密钥**：

```bash
read -rsp "Revoked API Key: " DIFY_REVOKED_KEY
echo
export DIFY_REVOKED_KEY
```

## 5. 执行测试

### 5.1 分组执行

在测试目录中运行相应的 Python 脚本。

**第一组：基础功能测试**

```bash
python3 test_01_functional.py
```

验证新增的 8 个统计接口，其中 Advanced Chat 应用适用的 7 个接口应返回 HTTP 200，平均响应时间接口因应用模式限制返回预期的 HTTP 400。

**第二组：身份认证测试**

```bash
python3 test_02_auth.py
```

分别发送缺失 API Key 和使用错误 API Key 的请求，验证服务端是否正确拒绝未授权访问。

**第三组：参数校验测试**

```bash
python3 test_03_params.py
```

验证非法日期、非法时区及错误时间范围是否返回 HTTP 400。

**第四组：跨应用数据隔离测试**

```bash
python3 test_04_isolation.py
```

脚本首先获取应用 A、B 的统计数据作为基线，再使用应用 A 的 API Key，在请求参数中指定应用 B 的 `app_id`，检查是否发生跨应用数据访问。

为了提高验证的有效性，建议提前为两个应用生成不同的统计数据。

如果 A、B 的统计结果完全相同，脚本将标记相关数据区分度检查为 `SKIP`，不将其视为已充分证明隔离。

此外，如果应用类型不支持对应统计指标，例如 Advanced Chat 不支持当前实现的平均响应时间统计，相关项目也会被跳过。

**第五组：API Key 撤销测试**

```bash
python3 test_05_revoked.py
```

使用已经在 Dify 管理后台撤销的临时 API Key，请求全部 8 个统计接口，验证服务端是否返回 HTTP 401。

该脚本不会主动删除或撤销任何密钥。

**第六组：Completion 专项测试**

```bash
python3 test_06_completion.py
```

验证 Completion 应用的平均响应时间统计接口是否返回 HTTP 200，以及响应中的 `latency` 是否为有效的非负数值。

执行前应先通过 `/v1/completion-messages` 产生真实调用记录，并确保统计时间范围包含对应日期。

### 5.2 统一执行

也可以使用统一入口执行所有已满足配置条件的测试：

```bash
python3 run_all.py
```

该脚本依次调用六组独立测试。

对于缺少必要环境变量的测试组，程序会自动跳过，并在最终汇总中显示成功、失败及跳过的脚本数量。

需要注意，统一入口中的脚本级 `SKIP` 仅表示测试未执行，不代表相关功能已经验证通过。

## 6. 测试结果说明

测试脚本使用以下状态标识：

| 标识     | 含义                                     |
| -------- | ---------------------------------------- |
| `PASS` | 当前检查满足预期条件                     |
| `FAIL` | 当前检查不满足预期条件                   |
| `SKIP` | 测试条件不足，或当前检查不适用于被测应用 |

测试结束后会输出汇总信息，例如：

```text
结果: PASS=14, FAIL=0, SKIP=1
```

该结果表示：

- 14 项检查通过。
- 没有发现失败项。
- 1 项检查因测试条件限制未完成。

需要特别注意，**`FAIL=0` 并不等同于所有测试均已完成**。对于存在 `SKIP` 的测试组，应根据跳过原因补充相应测试条件。

测试结果应结合实际检查范围进行解释，避免将单次黑盒测试等同于完整安全审计。

## 7. 已完成的测试验证

在本地 Dify v1.20.0 测试环境中，已完成以下验证：

| 测试项目                | 验证结果                             |
| ----------------------- | ------------------------------------ |
| 基础功能测试            | 8 项符合预期                         |
| API Key 鉴权测试        | 2 项通过                             |
| 参数校验测试            | 3 项通过                             |
| 跨应用数据隔离测试      | PASS=14，FAIL=0，SKIP=1              |
| API Key 撤销验证        | 此前已确认全部 8 个接口返回 HTTP 401 |
| Console 数据一致性验证  | 8 个统计指标核对一致                 |
| Completion 平均响应时间 | 已完成实际请求与 Console 数据核对    |

其中，跨应用隔离测试覆盖了 7 个适用的统计接口，并验证了使用应用 A 的 API Key 注入应用 B 的 `app_id` 后，返回结果仍与 A 的统计基线一致。

平均响应时间的双应用隔离测试尚未完成，后续可使用两个独立 Completion 应用补充验证。

需要说明的是，Console 数据一致性验证采用人工核对方式完成，不属于当前测试脚本自动执行的检查。
