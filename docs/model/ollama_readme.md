# 使用Ollama环境下的模型说明

Ollama 是一个开源的大型语言模型服务工具，旨在帮助用户快速在本地运行大模型。通过简单的安装指令，用户可以通过一条命令轻松启动和运行开源的大型语言模型。

直接在浏览器地址栏输入www.ollama.com，进入Ollama 的官网，根据自己的系统下载即可。

下载后拉取对应的大模型服务。

Ollama通过内置的RESTful接口与OpenAI API兼容，默认运行在`http://localhost:11434/v1`地址，因此当前项目也是可以对接Ollama环境下的模型服务的。更改为真实的IP即可。

我们可以在当前项目中使用适配OpenAI的接口地址来运行项目。

比如替换当前后端项目中的application.yml文件为：

```
OPENAI_API_KEY=http://localhost:11434/v1
OPENAI_BASE_URL=xxxxxx
```

同时更改默认的模型名称。

项目某些地方如果需要写绝对路径，可以配置为http://localhost:11434/v1/chat/completions

或者我们可以下载部署OneAPI开源项目，在OneAPI中维护自己Ollama地址。