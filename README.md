# Movie Crawler 
> **免责声明**：
> 
> 本项目仅供技术学习与交流。
> 
> 本仓库的代码及结构设计旨在展示针对电影评价类网站的数据采集工程实践。任何人或组织不得将本仓库的内容用于非法抓取数据、侵犯他人合法权益或违反目标网站的用户协议。本仓库不提供任何可直接用于实际网站抓取的具体配置。对于因使用本仓库内容而引起的任何法律责任，本仓库及开发者不承担任何责任。使用本仓库的内容即表示您同意本免责声明的所有条款和条件。
>
> 点击查看更为详细的免责声明。[点击跳转](https://github.com/Drift-bottle/movie-crawler#disclaimer)
> 
## 📖 项目简介
> 🎯 支持榜单抓取、海报下载、短评采集，所有子项目共享统一的请求客户端与日志系统。
### 🔧 技术原理
基于 Python 异步网络库 `httpx` 构建的模块化电影数据采集框架。

### ✨ 功能特性
- 🚀 **全异步架构**：基于 `httpx` 和 `asyncio`，底层支持并发抓取，当前采用顺序分页以保持对目标网站的礼貌访问
- 🔍 **智能编码检测**：集成 `chardet` + 手动 Fallback 机制，兼容各类网页编码
- ⏱️ **网络耗时监控**：基于 `event_hooks` 的请求/响应计时器，精准定位性能瓶颈
- 📊 **数据统计**：支持评分分布统计、百分比计算，自动生成分析结果CSV
- 🍪 **浏览器 Cookie 复用**：通过 Playwright CDP 连接 Edge 浏览器，获取真实登录态
- 🔄 **指数退避重试**：基于 `tenacity` 的健壮重试机制，抵御网络波动
- 📝 **双通道日志**：控制台 INFO 级别输出 + 文件 DEBUG 级别持久化，按子项目独立管理
- 🧩 **数据模型化**：使用 `dataclass` 定义数据结构，类型安全，支持自定义拓展为 JSON 字典序列化
- 💉 **依赖注入设计**：Logger 与 Cookies 通过参数注入，子项目独立配置，互不干扰

### 📂 项目结构
```bash
movie-crawler/
├── movie/ # 核心工具库
│ ├── __init__.py
│ ├── client.py # 异步请求客户端（编码检测、重试、hooks）
│ └── utils.py # 日志配置、计时装饰器、Cookie 获取
├── moving_rating/ # 子项目：榜单数据采集
│ ├── __init__.py
│ ├── crawler.py # 抓取与解析逻辑
│ ├── main.py # 入口文件
│ ├── models.py # 数据模型（dataclass）
│ └── pipeline.py # 数据存储与校验
├── poster/ # 子项目：海报下载（规划中）
├── reviews/ # 子项目：短评采集（规划中）
├── storage/ # 数据产出目录（已在 .gitignore 中忽略）
├── tests/ # 测试脚本
│ ├── test_client.py # HTTP 客户端连通性测试
│ ├── test_logger.py # 日志装饰器测试
│ └── test_playwright.py # Playwright 环境连通性测试
├── .gitignore
├── README.md
├── requirements.txt
```


## 🚀 快速开始

### 环境要求
- Python 3.11+
- Microsoft Edge 浏览器(用于 Cookie 获取)

### 安装
```bash
git clone https://github.com/Drift-bottle/movie-crawler.git
cd movie-crawler
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate      # macOS / Linux
pip install -r requirements.txt
playwright install chrome
```
> **说明**：`chrome` 指的是 Playwright 1.57.0 默认使用的 Chrome for Testing，并非系统自带的 Chrome 浏览器。
<details> 
<summary>💡 点此查看：如果报错或安装失败怎么办？</summary>

**1. 提示 `"chrome" is already installed` (如已有旧版 Chromium)**
请使用 --force 参数强制覆盖安装：
```bash
playwright install --force chrome
```

**2. 下载速度慢或无法连接**
可临时设置国内镜像加速（以 npmmirror.com 为例）：
```bash
# Windows PowerShell
$env:PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright"
playwright install chrome
```
>镜像为临时方案，若不生效请还原为官方源后重试。
</details>

## 配置与运行
### 确保 Edge 浏览器已登录目标网站
### 启动 Edge 远程调试模式（默认路径）
```bash
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="D:\edge_debug_profile"
```
如果上述命令提示找不到路径，请尝试手动定位 Edge 的安装目录：
- 1.在 Windows 开始菜单搜索 `Edge`，右键选择“打开文件位置”
- 2.在弹出的文件夹中，再次右键 Edge 快捷方式 → “打开文件所在的位置”
- 3.复制地址栏的完整路径，替换命令中的路径部分即可

### 运行榜单数据采集：
```bash
cd moving_rating
python main.py
```
### 采集完成后，数据文件将保存在 storage/ 目录下，运行日志可在对应的 .log 文件中查看。

### 运行测试
```bash
cd tests
python test_client.py        # 测试 HTTP 客户端连通性
python test_logger.py        # 测试日志装饰器功能
python test_playwright.py    # 测试 Playwright 环境
```


## 🛠️ 技术栈
| 类别 | 技术 |
|:---|:---|
| 异步 HTTP | `httpx`, `asyncio` |
| 网页解析 | `BeautifulSoup4`, `lxml` |
| 数据统计 | `pandas` |
| 编码检测 | `chardet` |
| 重试策略 | `tenacity` |
| 浏览器自动化 | `playwright` |
| 数据模型 | `dataclasses` |
| 日志系统 | `logging` |


## 🧩 技术难点与解决方案
### 响应编码兼容
- **难点**：目标网站可能缺少 charset 声明或声明与实际不符，导致解码失败
- **方案**:：实现 smart_encoding_detect 三层 Fallback 机制：

- **1. chardet.detect 高置信度优先匹配**
- **2. 手动遍历常见编码（utf-16, gb2312, gbk, utf-8）依次尝试**
- **3. 最终 Fallback 使用 utf-8 + errors='replace' 兜底**

### 异步装饰器计时
- **难点**：同步装饰器无法捕获异步函数的实际网络耗时
- **方案**：使用 async def wrapper + await func()，从协程内部计时，精准记录包含 I/O 等待的完整执行时间

### 日志系统解耦
- **难点**：如何在多个子项目间共享日志工具，同时保持每个子项目的日志独立
- **方案**：采用依赖注入模式，由 main.py 统一配置 Logger，通过参数传递给下游组件，避免硬编码

### Cookies获取
- **难点**：httpx.AsyncClient 在初始化时绑定 _current_cookies 对象的引用。一旦这个对象被意外替换（例如 _current_cookies = httpx.Cookies()），客户端就会与新的 Cookie 数据失联。另外，从浏览器获取的 Cookie 可能包含过期项，直接复用会逐渐累积。
- **方案**：采用原地更新策略。get_position_with_edge_login 内部通过 _current_cookies.clear() 清空所有现有 Cookie，再逐个重新填充，确保对象引用始终不变。

## ✅ 测试
基础冒烟测试已覆盖核心模块:
- **test_client.py**：验证 HTTP 客户端能正常发起请求并获取响应
- **test_logger.py**：验证日志装饰器能正确记录函数执行时间
- **test_playwright.py**：验证 Playwright 环境与 Chromium 内核已就绪


## 📄 许可证
本项目基于 Apache License 2.0 许可证开源。详见 [LICENSE](LICENSE) 文件。


## <a id="disclaimer"></a> ⚠️ 免责声明
### 1. 项目目的与性质
本项目（以下简称“本项目”）是作为一个技术研究与学习工具而创建的，旨在探索和学习网络数据采集技术。本项目专注于影评平台的数据爬取技术研究，旨在提供给学习者和研究者作为技术交流之用。

### 2. 法律合规性声明
本项目开发者（以下简称“开发者”）郑重提醒用户在下载、安装和使用本项目时，严格遵守中华人民共和国相关法律法规，包括但不限于《中华人民共和国网络安全法》、《中华人民共和国反间谍法》等所有适用的国家法律和政策。用户应自行承担一切因使用本项目而可能引起的法律责任。

### 3. 使用目的限制
本项目严禁用于任何非法目的的行为。本项目不得用于任何形式的非法侵入他人计算机系统，不得用于任何侵犯他人知识产权或其他合法权益的行为。

### 4. 免责声明
开发者已尽最大努力确保本项目的正当性及安全性，但不对用户使用本项目可能引起的任何形式的直接或间接损失承担责任。包括但不限于由于使用本项目而导致的任何数据丢失、设备损坏、法律诉讼等。

### 5. 知识产权声明
本项目的知识产权归开发者所有。本项目受到著作权法和国际著作权条约以及其他知识产权法律和条约的保护。用户在遵守本声明及相关法律法规的前提下，可以下载和使用本项目。

### 6. 最终解释权
关于本项目的最终解释权归开发者所有。开发者保留随时更改或更新本免责声明的权利，恕不另行通知。

### 法律风险参考资料
- [中国爬虫违法违规案例汇总](https://github.com/HiddenStrawberry/Crawler_Illegal_Cases_In_China)

## 关于商业使用的特别声明
尽管本项目采用 Apache License 2.0 许可证，该许可证允许商业使用，但**作者本人强烈建议**将本项目仅用于个人学习、研究及非商业目的。
本项目是作者独立开发，并在 AI 辅助下进行架构优化与工程实践，为展示个人技术能力创建的。作者现阶段专注于个人学习与技术研究，暂不参与商业合作或提供相关授权。


### 如果你遇到与本项目相关的问题，欢迎在 [Issues](https://github.com/Drift-bottle/movie-crawler/issues) 提出。