# JoyAgent-JDGenie Open Source Documentation

## The industry’s first open-source, highly complete, lightweight, general-purpose multi-agent product (JoyAgent-JDGenie)
**Address the last-mile challenge in rapidly developing multi-agent products.**

## Introduction
Most existing open-source agent projects are primarily SDKs or frameworks, requiring users to perform additional development and lacking true out-of-the-box usability. In contrast, our open-source JoyAgent-JDGenie is an end-to-end multi-agent product that can directly answer or resolve user queries or tasks. For example, when a user submits a query like“Provide an analysis of recent trends between the US dollar and gold,”JoyAgent-JDGenie can instantly generate a report in web or PPT format.

- **Generality and Customization**
  - JoyAgent-JDGenie is a versatile multi-agent framework. To customize functionality for new scenarios, users only need to integrate relevant sub-agents or tools into JoyAgent-Genie. To demonstrate its generality, JoyAgent-JDGenie achieved 75.15% accuracy on the GAIA benchmark Validation set and 65.12% on the Test set, outperforming industry-leading products such as OWL (CAMEL), Smolagent (Hugging Face), LRC-Huawei (Huawei), xManus (OpenManus), and AutoAgent (University of Hong Kong).

- **Lightweight and Independence**
  - Unlike Alibaba’s SpringAI-Alibaba (which relies on the Alibaba Cloud Bailian platform for LLM capabilities) or Coze (dependent on the Volcano Engine platform), our open-source multi-agent product JoyAgent-JDGenie is lightweight and platform-agnostic.

- **Comprehensive Open-Source Offering**
  - We have fully open-sourced JoyAgent-JDGenie, including its:
    - Frontend and backend
    - Framework and engine
    - Core sub-agents (e.g., Report Generator Agent, Code Agent, PPT Agent, File Agent)
    - For enhanced performance, we welcome users to leverage JoyAgent with fine-tuned models.

## Case Studies
<table>
<tbody>
<tr>
<td><img src="./docs/img/首页.png" alt=""></td>
<td><img src="./docs/img/ppt.png" alt=""></td>
</tr>
<tr>
<td><img src="./docs/img/report.png" alt=""></td>
<td><img src="./docs/img/table_analysis.png" alt=""></td>
</tr>
</tbody>
</table>



<table>
<tbody>
<tr>
<td>

<video src="https://private-user-images.githubusercontent.com/49786633/469170308-065b8d1a-92e4-470a-bbe3-426fafeca5c4.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTMxOTEzNzEsIm5iZiI6MTc1MzE5MTA3MSwicGF0aCI6Ii80OTc4NjYzMy80NjkxNzAzMDgtMDY1YjhkMWEtOTJlNC00NzBhLWJiZTMtNDI2ZmFmZWNhNWM0Lm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA3MjIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNzIyVDEzMzExMVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWRjNGY5ZTlmMTA4ODVhMWE0ZmEzYzU3YTIwYzJkYmIyY2Y0ZWE0NGUwZWU2ODAxNDA2MzQ0NzMyMWFlNTdiNWImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.fJyoUGcWjPWyG64ZwIcWWKz3FrBWuXAHHfdTLpIaaeU" data-canonical-src="https://private-user-images.githubusercontent.com/49786633/469170308-065b8d1a-92e4-470a-bbe3-426fafeca5c4.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTMxOTEzNzEsIm5iZiI6MTc1MzE5MTA3MSwicGF0aCI6Ii80OTc4NjYzMy80NjkxNzAzMDgtMDY1YjhkMWEtOTJlNC00NzBhLWJiZTMtNDI2ZmFmZWNhNWM0Lm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA3MjIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNzIyVDEzMzExMVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWRjNGY5ZTlmMTA4ODVhMWE0ZmEzYzU3YTIwYzJkYmIyY2Y0ZWE0NGUwZWU2ODAxNDA2MzQ0NzMyMWFlNTdiNWImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.fJyoUGcWjPWyG64ZwIcWWKz3FrBWuXAHHfdTLpIaaeU" controls="controls" muted="muted" class="d-block rounded-bottom-2 border-top width-fit" style="max-height:640px; min-height: 200px">
</video>

<td>

<video src="https://private-user-images.githubusercontent.com/49786633/469171050-15dcf089-5659-489e-849d-39c651ca7e5a.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTMxOTEzNzEsIm5iZiI6MTc1MzE5MTA3MSwicGF0aCI6Ii80OTc4NjYzMy80NjkxNzEwNTAtMTVkY2YwODktNTY1OS00ODllLTg0OWQtMzljNjUxY2E3ZTVhLm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA3MjIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNzIyVDEzMzExMVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTY5ZGU2MWU3NzA5NjYxM2ZhZDYxYTZjMWQxYWMzNGM2MTY2ODkzMTIzYjQ1NzRiOGZkOWUyODYzNmQ4N2Y5ZTUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.7KW-JGmFACnf5IS3kL7M0eV8uZhlxDD8Br61XvcgmjY" data-canonical-src="https://private-user-images.githubusercontent.com/49786633/469171050-15dcf089-5659-489e-849d-39c651ca7e5a.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTMxOTEzNzEsIm5iZiI6MTc1MzE5MTA3MSwicGF0aCI6Ii80OTc4NjYzMy80NjkxNzEwNTAtMTVkY2YwODktNTY1OS00ODllLTg0OWQtMzljNjUxY2E3ZTVhLm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA3MjIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNzIyVDEzMzExMVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTY5ZGU2MWU3NzA5NjYxM2ZhZDYxYTZjMWQxYWMzNGM2MTY2ODkzMTIzYjQ1NzRiOGZkOWUyODYzNmQ4N2Y5ZTUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.7KW-JGmFACnf5IS3kL7M0eV8uZhlxDD8Br61XvcgmjY" controls="controls" muted="muted" class="d-block rounded-bottom-2 border-top width-fit" style="max-height:640px; min-height: 200px">
</video>

</td>
</tr>
<tr>
<td>
<video src="https://private-user-images.githubusercontent.com/49786633/469171112-cd99e2f8-9887-459f-ae51-00e7883fa050.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTMxOTEzNzEsIm5iZiI6MTc1MzE5MTA3MSwicGF0aCI6Ii80OTc4NjYzMy80NjkxNzExMTItY2Q5OWUyZjgtOTg4Ny00NTlmLWFlNTEtMDBlNzg4M2ZhMDUwLm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA3MjIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNzIyVDEzMzExMVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWYyYmU5ODg4ZjI5NDNjZjBiYTVjYWRjMTI2ZGEyMDdjOWU2OTk2M2EwZjU4N2ZkYzU5NTQ5ZDJjMmUxMWNjNjAmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.OSPODm-E7K7PJaao8uThG1toIKsX3h93UEXS5GDqruQ" data-canonical-src="https://private-user-images.githubusercontent.com/49786633/469171112-cd99e2f8-9887-459f-ae51-00e7883fa050.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTMxOTEzNzEsIm5iZiI6MTc1MzE5MTA3MSwicGF0aCI6Ii80OTc4NjYzMy80NjkxNzExMTItY2Q5OWUyZjgtOTg4Ny00NTlmLWFlNTEtMDBlNzg4M2ZhMDUwLm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA3MjIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNzIyVDEzMzExMVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWYyYmU5ODg4ZjI5NDNjZjBiYTVjYWRjMTI2ZGEyMDdjOWU2OTk2M2EwZjU4N2ZkYzU5NTQ5ZDJjMmUxMWNjNjAmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.OSPODm-E7K7PJaao8uThG1toIKsX3h93UEXS5GDqruQ" controls="controls" muted="muted" class="d-block rounded-bottom-2 border-top width-fit" style="max-height:640px; min-height: 200px">
</video>
</td>
<td>

<video src="https://private-user-images.githubusercontent.com/49786633/469171151-657bbe61-5516-4ab9-84c2-c6ca75cc4a6f.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTMxOTEzNzEsIm5iZiI6MTc1MzE5MTA3MSwicGF0aCI6Ii80OTc4NjYzMy80NjkxNzExNTEtNjU3YmJlNjEtNTUxNi00YWI5LTg0YzItYzZjYTc1Y2M0YTZmLm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA3MjIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNzIyVDEzMzExMVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTVmNGExZTlhNmM5NWMzMjc3ZWFlNTcyMzZjZTA4NWU4ZjY3OTA5ZTg5NzgwNDA2ODExNTg5MTkyNGQ5NDYzNTgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.n3ZWlSK1GSM5Zyibk-D9jAArzDqvX3WdZtj7IdzG-4I" data-canonical-src="https://private-user-images.githubusercontent.com/49786633/469171151-657bbe61-5516-4ab9-84c2-c6ca75cc4a6f.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTMxOTEzNzEsIm5iZiI6MTc1MzE5MTA3MSwicGF0aCI6Ii80OTc4NjYzMy80NjkxNzExNTEtNjU3YmJlNjEtNTUxNi00YWI5LTg0YzItYzZjYTc1Y2M0YTZmLm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA3MjIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNzIyVDEzMzExMVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTVmNGExZTlhNmM5NWMzMjc3ZWFlNTcyMzZjZTA4NWU4ZjY3OTA5ZTg5NzgwNDA2ODExNTg5MTkyNGQ5NDYzNTgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.n3ZWlSK1GSM5Zyibk-D9jAArzDqvX3WdZtj7IdzG-4I" controls="controls" muted="muted" class="d-block rounded-bottom-2 border-top width-fit" style="max-height:640px; min-height: 200px">
</video>
  
</td>
</tr>
</tbody>
</table>

## Product Comparison

<table>
<thead>
<tr>
<th>Category</th>
<th>agent</th>
<th>Open Sourced?</th>
<th>Fully Open-Sourced Product?</th>
<th>Dependent on Ecosystem?</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="2"><strong>SDK</strong></td>
<td>SpringAI-Alibaba</td>
<td>Partial</td>
<td>No (SDK only)</td>
<td>Yes (Alibaba Cloud Bailian Platform)</td>
</tr>
<tr>
<td>Coze</td>
<td>Partial</td>
<td>No (Nieo SDK only)</td>
<td>Yes (Volcano Engine Platform)</td>
</tr>
<tr>
<td rowspan="6"><strong>Framework</strong></td>
<td>Fellow</td>
<td>YES</td>
<td>No (Eko Agent Framework only)</td>
<td>No</td>
</tr>
<tr>
<td>Dify</td>
<td>YES</td>
<td>No (Workflow-focused framework only)</td>
<td>No</td>
</tr>
<tr>
<td>SkyworkAI</td>
<td>YES</td>
<td>No (Agent framework only)</td>
<td>No</td>
</tr>
<tr>
<td>OpenManus</td>
<td>YES</td>
<td>No (Agent framework only)</td>
<td>No</td>
</tr>
<tr>
<td>Owl</td>
<td>YES</td>
<td>No (Agent framework only)</td>
<td>No</td>
</tr>
<tr>
<td>n8n</td>
<td>YES</td>
<td>No (Agent framework only)</td>
<td>no</td>
</tr>
<tr>
<td rowspan="3"><strong>Protocol</strong></td>
<td>MCP</td>
<td>Yes</td>
<td>No (Protocol only)</td>
<td>no</td>
</tr>
<tr>
<td>A2A</td>
<td>YES</td>
<td>No (Protocol only)</td>
<td>No</td>
</tr>
<tr>
<td>AG-UI</td>
<td>YES</td>
<td>No (Protocol only)</td>
<td>No</td>
</tr>
<tr>
<td rowspan="2"><strong>Technical Module</strong></td>
<td>memory0</td>
<td>YES</td>
<td>No (Technical module only)</td>
<td>No</td>
</tr>
<tr>
<td>LlamaIndex</td>
<td>YES</td>
<td>No (Technical module only)</td>
<td>No</td>
</tr>
<tr>
<td><strong>Product</strong></td>
<td>Our</td>
<td>YES</td>
<td>Yes (End-to-end open-source agent product)</td>
<td>No</td>
</tr>
</tbody>
</table>

## Framework Performance Superiority

### Test set performance 65.12%
<img width="3524" height="1022" alt="test" src="https://github.com/user-attachments/assets/06c85286-e61f-4b5e-8335-413cd22ecbf4" />

### Validation set performance 75.15%

| Agent                     | Score      | Score_level1 | Score_level2 | Score_level3 | Organization         |
|---------------------------|------------|--------------|--------------|--------------|------------|
| Alita v2.1                | 0.8727     | 0.8868       | 0.8953       | 0.7692       | Princeton  |
| Skywork                   | 0.8242     | 0.9245       | 0.8372       | 0.5769       | 天工         |
| AWorld                    | 0.7758     | 0.8868       | 0.7791       | 0.5385       | Ant Group  |
| Langfun                   | 0.7697     | 0.8679       | 0.7674       | 0.5769       | DeepMind   |
| **JoyAgent-JDGenie(Our)** | **0.7515** | **0.8679**   | **0.7791**   | **0.4230**   | **Our**    |
| OWL                       | 0.6909     | 0.8491       | 0.6744       | 0.4231       | CAMEL      |
| Smolagent                 | 0.5515     | 0.6792       | 0.5349       | 0.3462       | Huggingface |
| AutoAgent                 | 0.5515     | 0.7170       | 0.5349       | 0.2692       | HKU        |
| Magentic                  | 0.4606     | 0.5660       | 0.4651       | 0.2308       | MSR AI Frontiers |
| LRC-Huawei                | 0.406      | 0.5283       | 0.4302       | 0.0769       | Huawei     |
| xManus                    | 0.4061     | 0.8113       | 0.2791       | 0.0000       | OpenManus  |

<img width="1073" height="411" alt="score" src="https://github.com/user-attachments/assets/9d997b68-565e-4228-8f5b-229158f33617" />

## System Architecture

<img width="1092" height="582" alt="ME1753788413469" src="https://github.com/user-attachments/assets/cf42bdb9-e62d-4e88-a29a-1777369665d7" />


This open-source project is based on JoyAgent-JDGenie, publicly releasing the complete product interface, multiple core agent modes (React mode, Plan and Execute mode, etc.), multiple sub-agents (Report Agent, Search Agent, etc.), and multi-agent interaction protocols.
### Key Features and Advantages

- **End-to-End Multi-Agent Product: Ready out-of-the-box with support for secondary development**
- **Agent Framework Protocols**
  - Support for Diverse Agent Design Patterns
  - Multi-Agent Context Management
  - High-Concurrency DAG Execution Engine: Exceptional execution efficiency
- **Sub-Agents and Tools**
  - Pluggable sub-agents and tools: Pre-configured with various sub-agents and utilities
  - Multiple file export formats: HTML, PPT, Markdown
  - Plan & Tool Call Optimization: Iteratively enhanced via Reinforcement Learning (RL)
  - End-to-End Streaming Responses

### Key Innovations

![invo](./docs/img/invo.png)

#### multi-level and multi-pattern thinking
- **multi-level**：work level VS task level
- **multi-pattern**：plan and executor VS react

#### cross task workflow memory

#### tool evolution via auto-disassembly-and-reassembly of atom-tools
Generates novel tools from existing ones instead of creating from scratch (reducing faulty tool generation):
- Implicit Atomization:
  - Automatically decomposes existing tools into atomic sub-tools
  - No need for manual pre-definition of atomic components
- LLM-Driven Reassembly:
  - Dynamically recombines atomic tools via large language models
  - Enables emergent tool creation without human intervention

## Quick Start

### Method 1: One-Command Docker Deployment

```
1.git clone https://github.com/jd-opensource/joyagent-jdgenie.git

2.Manually update the following configurations in genie-backend/src/main/resources/application.yml:
base_url, apikey, model, max_tokens, model_name
Note for DeepSeek users: Set max_tokens: 8192 for deepseek-chat

Manually update the following environment variables in genie-tool/.env_template:
OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_MODEL, SERPER_SEARCH_API_KEY
DeepSeek Configuration:Set DEEPSEEK_API_KEY and DEEPSEEK_API_BASE，Configure DEFAULT_MODEL = deepseek/deepseek-chat，
Replace all occurrences of ${DEFAULT_MODEL} with deepseek/deepseek-chat

3.Build the Docker image
docker build -t genie:latest .

4.Launch the Docker container
docker run -d -p 3000:3000 -p 8080:8080 -p 1601:1601 --name genie-app genie:latest

5.Access Genie via browser
Open http://localhost:3000
```
If you encounter deployment issues, refer to this video tutorial:【5分钟使用deepseek启动开源智能体应用joyagent-genie-哔哩哔哩】 https://b23.tv/8VQDBOK

### Method 2: Manual Environment Initialization and Service Launch

#### Prerequisites
- jdk17
- python3.11
- python Environment Setup
  - pip install uv
  - cd genie-tool
  - uv sync
  - source .venv/bin/activate

#### Option 1: Step-by-Step Manual Deployment
Ultra-detailed guide reference: [Step by Step](./Deploy.md)

#### Option 2: One-Command Launch (Recommended)
Directly start all services via shell:
```
sh check_dep_port.sh # Verify all dependencies and port occupancy
sh Genie_start.sh  # Launch services directly; restart this script after configuration changes (terminate all services with Control+C)
```
For deployment guidance, refer to the demonstration video:【joyagent-jdgenie部署演示】 https://www.bilibili.com/video/BV1Py8Yz4ELK/?vd_source=a5601a346d433a490c55293e76180c9d

## Custom development

### Integrating Custom MCP Tools into JoyAgent-JDGenie

#### Configuration File:

Edit genie-backend/src/main/resources/application.yml to add MCP server URLs (comma-separated):

You can change the front-end request path to the back-end in ui/.env.

```yaml
mcp_server_url: "http://ip1:port1/sse,http://ip2:port2/sse"
```

#### Start Service:

```bash
sh start_genie.sh
```

#### Usage Example:

After integrating the 12306 ticket tool, initiate:
*"Plan a 7-day trip for 2 people from Beijing to Xinjiang in July and query train tickets"*
→ Genie designs travel itinerary → Invokes MCP tool for ticket queries → Generates final report
![img.png](./docs/img/mcp_example.png)


### Adding Custom Sub-Agent to JoyAgent-JDGenie

Implementing the BaseTool Interface: Declaring Tool Name, Description, Parameters, and Invocation Methods.

```java
/** * Base Tool Interface */publicinterfaceBaseTool {
    StringgetName(); // Tool name
    StringgetDescription(); // Tool description
    Map<String, Object> toParams(); // Tool parameters
    Objectexecute(Objectinput); // Invoke tool
}
// Weather Agent Example
    publicclassWeatherToolimplementsBaseTool {
    @Override
    publicStringgetName() {
        return"agent_weather";
    }

    @Override
    publicStringgetDescription() {
        return"A weather query agent";
    }

    @Override
    publicMap<String, Object> toParams() {
        return"{\"type\":\"object\",\"properties\":{\"location\":{\"description\":\"地点\",\"type\":\"string\"}},\"required\":[\"location\"]}";
    }

    @Override
    publicObjectexecute(Objectinput) {
        return"Today's weather is sunny";
    }
}
```

Add the following code in `com.jd.genie.controller.GenieController#buildToolCollection` to integrate custom Agent.
```java
WeatherTool weatherTool = new WeatherTool();
toolCollection.addTool(weatherTool);
```

#### Start service

```bash
sh start_genie.sh
```


## Contributors
Core Team: Liu Shangkun,Li Yang,Jia Shilin,Tian Shaohua,Wang Zhen,Yao Ting,Wang Hongtao,Zhou Xiaoqing,Liu min,Zhang Shuang,Liuwen,Yangdong,Xu Jialei,Zhou Meilei,Zhao Tingchong,Wu jiaxing, Wang Hanmin,Xu Shiyue,Liu Jiarun

Core Team: JD.com CHO Enterprise Informatization Team (EI)

## Contribution & Collaboration
We welcome all great ideas and suggestions. If you wish to become a project co-builder, you may submit Pull Requests at any time. Whether it's improving products/frameworks, fixing bugs, or adding new features - all contributions are highly valued.
Before contributing, you need to read and sign the Contributor Agreement and send it to org.developer3@jd.com.
 [Chinese Version](https://github.com/jd-opensource/joyagent-jdgenie/blob/main/contributor_ZH.pdf)，[English Version](https://github.com/jd-opensource/joyagent-jdgenie/blob/main/contributor_EN.pdf)


## Citation
For academic references or inquiries, please use the following BibTeX entry:：
```bibtex
@software{JoyAgent-JDGenie,
  author = {Agent Team at JDCHO},
  title = {JoyAgent-JDGenie},
  year = {2025},
  url = {https://github.com/jd-opensource/joyagent-jdgenie},
  version = {0.1.0},
  publisher = {GitHub},
  email = {jiashilin1@jd.com;liyang.1236@jd.com;liushangkun@jd.com;tianshaohua.1@jd.com;wangzhen449@jd.com;yaoting.2@jd.com}
}
```

## Contributors

<a href="https://github.com/jd-opensource/joyagent-jdgenie/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=jd-opensource/joyagent-jdgenie" />
</a>

# Star History
[![Star History Chart](https://api.star-history.com/svg?repos=jd-opensource/joyagent-jdgenie&type=Date&cache=false)](https://star-history.com/#jd-opensource/joyagent-jdgenie&Date)

Contact Us  

[//]: # (![contact]&#40;./docs/img/ME1753153769883.png&#41;)
![contact](./docs/img/wechat2.png)

[//]: # (![contact]&#40;./docs/img/contact.jpg&#41;)
