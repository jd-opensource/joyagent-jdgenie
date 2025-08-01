# JoyAgent-JDGenie 详细部署指南

本文档将引导您完成 JoyAgent-JDGenie 项目四个核心服务（前端、后端、Tools、MCP）的完整部署流程。

## 一、 环境准备 (Prerequisites)

在开始部署之前，请确保您的开发环境满足以下所有要求。如果已经满足可以直接调过。

### 1\. Java (版本 \> 17)

后端服务需要 Java 17 或更高版本。

- **macOS 用户 (推荐使用 Homebrew)**
  执行以下命令安装 `maven`，它会自动安装最新版的 OpenJDK。

  ```bash
  brew install maven
  ```

  安装后，设置 `JAVA_HOME` 环境变量。通常 Homebrew 的安装路径为 `/opt/homebrew/Cellar/openjdk/...`。

- **手动安装**

  1.  从 [Oracle 官方网站](https://www.oracle.com/java/technologies/downloads/) 下载并安装适用于您操作系统的 JDK (版本 \> 17)。
  2.  找到 Java 的安装路径。在 macOS 上可以使用：
      ```bash
      /usr/libexec/java_home -V
      ```
  3.  将 `JAVA_HOME` 添加到您的 shell 配置文件中（以 `zsh` 为例）：
      ```bash
      echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 17)' >> ~/.zshrc # 将 17 替换为您安装的版本
      echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.zshrc
      source ~/.zshrc
      ```

### 2\. pnpm (版本 \> 7)

前端项目使用 `pnpm` 作为包管理器。

- **安装 pnpm**
  请参考 [pnpm 官方安装指南](https://pnpm.io/zh/installation) 进行安装。

- 💡 **提示**
  如果 `pnpm` 安装依赖包速度较慢，建议配置使用国内镜像源以加速下载。

### 3\. Python & uv

Tools 服务和 MCP 服务使用 Python。`uv` 是一个极速的 Python 包安装和管理工具。

- 确保您的系统已安装 Python (推荐 3.8+)。
- 安装 `uv`：
  ```bash
  pip install uv
  ```

---

## 二、 部署步骤

请为每个步骤打开一个新的终端窗口，以保持各服务独立运行。

### 步骤一：启动前端服务 (UI)

此服务负责应用的图形用户界面。

1.  打开一个新终端，进入 `ui` 目录并执行启动脚本：

    ```bash
    cd joyagent-jdgenie/ui
    sh start.sh
    ```

2.  **验证成功**
    当终端输出以下信息时，即表示前端服务启动成功：

    ```
    > Local:   http://localhost:3000/
    ```

    > **排错提示**：如果遇到 `pnpm: command not found` 或其他与 `pnpm` 相关的错误，请返回 **环境准备** 部分，检查 `pnpm` 是否已正确安装。

### 步骤二：启动后端服务 (Backend)

此服务是应用的核心业务逻辑层。

1.  打开另一个新终端，进入 `genie-backend` 目录。

2.  首先，构建项目：

    ```bash
    cd joyagent-jdgenie/genie-backend
    sh build.sh
    ```

    看到 `[INFO] BUILD SUCCESS` 日志即表示构建成功。

    > **排错提示**：如果构建失败，请返回 **环境准备** 部分，确保已正确安装并配置 Java (版本 \> 17)。

3.  启动后端服务：

    ```bash
    sh start.sh
    ```

4.  您可以随时通过以下命令查看实时日志：

    ```bash
    tail -f genie-backend_startup.log
    ```

#### 后端配置 (可选)

您可以自定义后端服务使用的 LLM (大语言模型) 配置。

1.  编辑配置文件：
    `joyagent-jdgenie/genie-backend/src/main/resources/application.yml`

2.  找到 `settings` 部分，修改或添加您的模型配置。`key` (例如 `"claude-3-opus-20240229"`) 是模型的唯一标识符，可在应用其他地方引用。

    **示例配置**：

    ```yaml
    settings: '{"claude-3-opus-20240229": {
            "model": "claude-3-opus-20240229",
            "max_tokens": 8192,
            "temperature": 0,
            "base_url": "<在此输入您的 LLM API 地址>",
            "apikey": "<在此输入您的 LLM API Key>",
            "max_input_tokens": 128000
    }}'
    ```

3.  **重要**：修改配置后，必须重新执行构建和启动命令才能生效。

    ```bash
    sh build.sh
    sh start.sh
    ```

### 步骤三：启动 Tools 服务 (genie-tool)

此服务提供了一系列外部工具能力，如网络搜索。

1.  打开第三个终端，进入 `genie-tool` 目录。

2.  使用 `uv` 创建并同步虚拟环境的依赖：

    ```bash
    cd joyagent-jdgenie/genie-tool
    uv sync
    ```

3.  激活虚拟环境：

    ```bash
    source .venv/bin/activate
    ```

4.  **仅在首次启动时**，需要初始化数据库：

    ```bash
    python -m genie_tool.db.db_engine
    ```

    后续启动不再需要执行此命令。

5.  配置环境变量。首先复制模板文件：

    ```bash
    cp .env_template .env
    ```

6.  编辑 `.env` 文件，填入您的 `SERPER_SEARCH_API_KEY`。

    - 您可以从 [serper.dev](https://serper.dev/) 免费申请该 API Key。

7.  启动 Tools 服务：

    ```bash
    uv run python server.py
    ```

### 步骤四：启动 MCP 服务 (genie-client)

此服务是模型控制平台 (Model Control Platform)。

1.  打开第四个终端，进入 `genie-client` 目录。

2.  创建并激活虚拟环境：

    ```bash
    cd joyagent-jdgenie/genie-client
    uv venv
    source .venv/bin/activate
    ```

3.  执行启动脚本：

    ```bash
    sh start.sh
    ```

---

至此，所有服务均已启动。您现在可以通过浏览器访问 `http://localhost:3000/` 开始使用 JoyAgent-JDGenie 了。
