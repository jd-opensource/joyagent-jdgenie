# GenieController.java 代码说明文档

## 文件概述

**文件路径**: `/home/rich/dev/study/ai-agent-try/genie-backend/src/main/java/com/jd/genie/controller/GenieController.java`

**主要功能**: Genie 系统的主要 REST API 控制器，提供智能代理服务的 HTTP 接口，支持 SSE (Server-Sent Events) 流式响应。

**技术栈**: 
- Spring Boot Web MVC
- Server-Sent Events (SSE)
- 异步编程
- 线程池管理
- JSON 处理

## 类结构分析

### 类定义
```java
@Slf4j
@RestController
@RequestMapping("/")
public class GenieController
```

### 核心属性

#### 线程管理
- **executor** (ScheduledExecutorService): 调度线程池，用于心跳和定时任务 (线程池大小: 5)
- **HEARTBEAT_INTERVAL** (long): 心跳间隔时间 (10秒)

#### 依赖注入
- **genieConfig** (GenieConfig): 系统配置管理器
- **agentHandlerFactory** (AgentHandlerFactory): 代理处理器工厂
- **gptProcessService** (IGptProcessService): GPT 处理服务

## 核心方法详细说明

### startHeartbeat 方法

**方法签名**: 
```java
private ScheduledFuture<?> startHeartbeat(SseEmitter emitter, String requestId)
```

**方法用途**: 
启动 SSE 连接的心跳机制，定期发送心跳消息保持连接活跃

**参数说明**:
- `emitter` (SseEmitter): SSE 事件发射器
- `requestId` (String): 请求唯一标识

**返回值**: 
- ScheduledFuture<?> - 可取消的定时任务句柄

**执行逻辑**:
1. **定时任务设置**: 每 10 秒执行一次心跳发送
2. **心跳发送**: 通过 emitter 发送 "heartbeat" 消息
3. **异常处理**: 发送失败时关闭连接并记录错误
4. **日志记录**: 记录每次心跳发送的日志

**异常处理策略**:
- 捕获发送异常，调用 `emitter.completeWithError(e)` 关闭连接
- 记录详细的错误日志信息

### registerSSEMonitor 方法

**方法签名**: 
```java
private void registerSSEMonitor(SseEmitter emitter, String requestId, ScheduledFuture<?> heartbeatFuture)
```

**方法用途**: 
注册 SSE 连接的各种事件监听器，管理连接生命周期

**参数说明**:
- `emitter` (SseEmitter): SSE 事件发射器
- `requestId` (String): 请求唯一标识  
- `heartbeatFuture` (ScheduledFuture<?>): 心跳任务句柄

**返回值**: void

**事件监听器注册**:

1. **完成事件监听** (`onCompletion`):
   - 正常完成时记录日志
   - 取消心跳定时任务

2. **超时事件监听** (`onTimeout`):
   - 连接超时时记录日志
   - 取消心跳任务并完成连接

3. **错误事件监听** (`onError`):
   - 连接错误时记录异常
   - 取消心跳任务并关闭连接

### AutoAgent 方法

**方法签名**: 
```java
@PostMapping("/AutoAgent")
public SseEmitter AutoAgent(@RequestBody AgentRequest request)
```

**方法用途**: 
核心 API 接口，处理智能代理请求并返回 SSE 流式响应

**参数说明**:
- `request` (AgentRequest): 代理请求对象

**返回值**: 
- SseEmitter: SSE 事件发射器，用于流式响应

**执行流程**:

1. **请求日志记录**:
   - 记录完整的请求参数 JSON

2. **SSE 初始化**:
   - 设置超时时间为 1 小时
   - 启动心跳机制
   - 注册事件监听器

3. **请求预处理**:
   - 调用 `handleOutputStyle()` 处理输出样式
   - 更新查询内容

4. **异步执行**:
   - 使用线程池异步处理请求
   - 构建代理上下文 (AgentContext)
   - 构建工具集合
   - 获取对应的处理器并执行
   - 执行完成后关闭 SSE 连接

5. **异常处理**:
   - 捕获执行过程中的异常
   - 记录详细错误日志

### handleOutputStyle 方法

**方法签名**: 
```java
private String handleOutputStyle(AgentRequest request)
```

**方法用途**: 
根据输出样式配置处理查询内容，支持不同的展示格式

**参数说明**:
- `request` (AgentRequest): 包含输出样式配置的请求对象

**返回值**: 
- String: 处理后的查询内容

**支持的输出样式**:
- **html 模式**: 查询 + 以 HTML 展示
- **docs 模式**: 查询 + 以 Markdown 展示  
- **table 模式**: 查询 + 以 Excel 展示

**处理逻辑**:
1. 获取原始查询内容
2. 从配置中获取输出样式提示词映射
3. 根据请求中的输出样式添加对应的提示词
4. 返回增强后的查询内容

### buildToolCollection 方法

**方法签名**: 
```java
private ToolCollection buildToolCollection(AgentContext agentContext, AgentRequest request)
```

**方法用途**: 
构建代理可用的工具集合，包括默认工具和 MCP 工具

**参数说明**:
- `agentContext` (AgentContext): 代理执行上下文
- `request` (AgentRequest): 代理请求对象

**返回值**: 
- ToolCollection: 构建完成的工具集合

**工具构建流程**:

1. **基础工具初始化**:
   - 创建新的 ToolCollection 实例
   - 设置代理上下文

2. **文件工具添加**:
   - 创建并配置 FileTool
   - 设置代理上下文并添加到工具集合

3. **默认工具集合**:
   - 从配置获取默认工具列表 (search,code,report)
   - 根据配置动态添加工具:
     - **code**: CodeInterpreterTool (代码解释器)
     - **report**: ReportTool (报告生成器)  
     - **search**: DeepSearchTool (深度搜索)

4. **MCP 工具集成**:
   - 遍历配置的 MCP 服务器 URL
   - 调用每个服务器的 listTool 接口
   - 解析返回的工具列表 JSON
   - 验证响应状态码和数据有效性
   - 为每个工具创建 MCP 工具实例

**MCP 工具处理逻辑**:
- 验证服务器响应有效性
- 解析工具信息 (name, description, inputSchema)
- 批量添加到工具集合
- 异常处理和错误日志记录

### health 方法

**方法签名**: 
```java
@RequestMapping(value = "/web/health", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public ResponseEntity<String> health()
```

**方法用途**: 
系统健康检查接口

**返回值**: 
- ResponseEntity<String>: 返回 "ok" 表示服务正常

### queryAgentStreamIncr 方法

**方法签名**: 
```java
@RequestMapping(value = "/web/api/v1/gpt/queryAgentStreamIncr", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public SseEmitter queryAgentStreamIncr(@RequestBody GptQueryReq params)
```

**方法用途**: 
处理 GPT 代理流式增量查询请求

**参数说明**:
- `params` (GptQueryReq): GPT 查询请求参数

**返回值**: 
- SseEmitter: SSE 事件发射器

**执行逻辑**:
- 委托给 `gptProcessService.queryMultiAgentIncrStream()` 处理

## SSE 流式响应机制

### 连接管理
- **超时设置**: 默认 1 小时超时
- **心跳保活**: 每 10 秒发送心跳消息
- **事件监听**: 完成、超时、错误事件处理

### 异步处理
- 使用线程池异步处理请求
- 主线程立即返回 SSE 对象
- 避免阻塞 HTTP 连接

### 错误处理
- 完善的异常捕获和日志记录
- 优雅的连接关闭处理
- 心跳失败自动断开连接

## 工具集合管理

### 工具类型
1. **文件工具**: 文件读取、写入、管理
2. **代码工具**: 代码执行和解释
3. **报告工具**: 各种格式报告生成
4. **搜索工具**: 深度搜索和分析
5. **MCP 工具**: 外部 MCP 服务器提供的工具

### 动态工具加载
- 支持从配置文件动态加载工具
- MCP 工具的动态发现和注册
- 工具异常不影响其他工具正常使用

## 配置管理

### 输出样式配置
- 支持多种输出格式配置
- 灵活的提示词模板系统

### 工具配置
- 可配置的默认工具列表
- MCP 服务器地址配置
- 工具参数动态配置

## 性能优化

### 线程池管理
- 心跳使用独立的调度线程池
- 请求处理使用异步线程池
- 避免线程阻塞和资源竞争

### 连接优化
- 心跳机制保持连接活跃
- 及时的连接清理和资源释放
- 超时保护防止连接泄漏

该控制器是系统的主要入口点，提供了完整的 RESTful API 和流式响应能力，是前端和智能代理系统之间的重要桥梁。