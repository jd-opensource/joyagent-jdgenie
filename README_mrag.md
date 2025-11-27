# 多模态知识库管理

## 简介
**1. 多模态问题**：处理结构化与非结构化内容
当面对企业内普遍存在的文档时，一个仅能理解文字的RAG系统，无法阅读和理解图片、表格中蕴含的丰富信息。这导致了检索的片面性与答案的不完整性，大量高价值的知识资产因此沉睡，无法被有效利用。

一方面图像中的数据（如截图或扫描件）也无法被文本RAG系统直接理解。另一方面PDF文档尤其是包含嵌入式表格、图表和复杂布局的文档，需要复杂的解析逻辑，因为其格式和布局往往不一致 。传统的文本提取方法在此处会丢失关键信息，例如表格中数字的列关系或图表中数据的视觉趋势。大型语言模型（LLM）主要通过海量的顺序文本进行训练，因此它们在处理多维、关系化的表格数据时会遇到困难 。如果将表格简单地转换为纯文本进行嵌入，就会破坏其固有的结构化关系，导致检索结果的准确性大打折扣 。

**2. 多模态知识管理** 

JoyAgent多模态知识管理整体分为知识加工层，知识使用和知识生成三层。

•知识加工主要负责将多模态数据异构数据进行统一处理，形成系统认识的统一的文档结构，方便后续流程统一处理。
    我们内部定义了一套统一文档结构，能够很好的处理包含表格，图片，引用，附件等多种格式的文档。

•知识使用包括了传统知识检索和多模态RAG。
•知识生成层目标是根据已有的知识，辅助用户进行知识的二次创作包括文档撰写，内容生成，方案建议等。这块会在后续的迭代中逐步实现。

## 系统架构
![](./docs/img/mrag/archi.png)

### 知识加工

为有效支持企业内多样化的文档格式（如Excel、Word、PDF、PPT、图片等），我们构建了一套统一的文档解析框架。针对不同文件类型，分别设计了相应的解析算法，最终输出标准化的文档结构。
在处理PDF或图片类文档时，若直接整页提取OCR结果或不经处理直接生成向量，往往难以达到理想的检索效果。为此，我们引入了布局分析（Layout Analysis）作为预处理步骤：首先将图像划分为多个语义独立的布局区域，再对每个区域分别进行结构化信息提取，包括文字识别、图像内容理解以及结构关系构建等，从而提升内容解析的粒度与准确性。
![](./docs/img/mrag/kg_processing.png)

### 知识使用
针对不同模态，分别采用多种召回通道（如向量召回、关键词检索、语义匹配等），多策略融合，极大提升召回覆盖率与相关性。

## 案例展示

|  |  |
| :---: | :---: |
| ![](./docs/img/mrag/gzjzz.png) <br> ![](./docs/img/mrag/example2.png) | ![](./docs/img/mrag/example3.png) <br> ![](./docs/img/mrag/example4.png) |

## 部署使用指南
<iframe src="//player.bilibili.com/player.html?isOutside=true&aid=115615268405740&bvid=BV1EBUYBjEmX&cid=34278803675&p=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true" width="100%" height="600"></iframe>

## 效果先进性：DoubleBench数据集测评

在公开数据集DoubleBench上，我们对比测评了MDocAgent、Colqwen-gen、ViDoRAG、M3DOCRAG等多模态问答系统。

最终答案的准确性采用LLM作为评判标准进行评估（https://arxiv.org/abs/2306.05685）
。 GPT-4o根据0到10的等级对生成的答案与真实答案的正确性进行评分。得分不低于7分的答案为正确，不高于3分的答案为错误，其余答案为部分正确。

测评结果如下：**JoyAgent的正确率达到76.2%,优于当前其他多模态问答系统。**

| 系统           | 正确✅       | 部分正确❓ | 错误❌ |
|--------------|-----------|-----------|-------|
| **JoyAgent** | **0.762** | 0.105     | 0.133 |
| MDocAgent    | 0.757     | 0.132     | 0.111 |
| Colqwen-gen  | 0.676     | 0.160     | 0.164 |
| ViDoRAG      | 0.623     | 0.144     | 0.233 |
| M3DOCRAG     | 0.538     | 0.138     | 0.324 |

- MDocAgent： 北卡罗来纳大学-2025年（https://arxiv.org/abs/2503.13964）

- ViDoRAG：阿里巴巴NLP实验室-2025年（https://arxiv.org/abs/2502.18017）

- M3DOCRAG：北卡罗来纳大学-2025年（https://arxiv.org/abs/2411.04952）

- Colqwen-gen：参照组，结果由gpt-4o直接回复生成（不采用RAG）。

## 相关配置
具体见JoyAgent首页的配置说明


## 项目共建者
贡献者：Liu Shangkun,[Li Yang](https://scholar.google.com.hk/citations?hl=zh-CN&user=AeCTbv8AAAAJ&view_op=list_works&gmla=AH8HC4zYqeayQxrQFmScZ7XYxLah1enc8ynhQYMtBdPmjwfpMBvsTj_OoBkFTPCw1Xi2xk7gbTzHPH-QpJSw_sGkCKdYDVXSu8Ty2tNJMhs),Jia Shilin,Tian Shaohua,Wang Zhen,Yao Ting,Wang Hongtao,Zhou Xiaoqing,Liu min,Zhang Shuang,Liuwen,Yangdong,Xu Jialei,Zhou Meilei,Zhao Tingchong,Wu jiaxing, Wang Hanmin, Zhou Zhiyuan, Xu Shiyue,Liu Jiarun, Hou Kang, Jing Lingtuan, Guo Hongliang, Liu Yanchen, Chen Kun, Pan Zheyi, Duan Zhewen, Tu Shengkun, Zhang Haidong, Wang Heng, Zhang Junbo, Liu haibo, Song Li, Zhang Meng

所属机构:京东CHO企业信息化团队（EI）、京东科技协同办公团队、京东物流

## 贡献和合作

我们欢迎所有好想法和建议，如果您想成为项目的共建者，可随时向我们提Pull Request。无论是完善产品和框架、修复bug还是添加新特性，您的贡献都非常宝贵。
在此之前需要您阅读并签署贡献者协议并发送到邮箱org.developer3@jd.com，请阅读 [贡献指南中文版](https://github.com/jd-opensource/joyagent-jdgenie/blob/main/contributor_ZH.pdf)，[贡献指南英文版](https://github.com/jd-opensource/joyagent-jdgenie/blob/main/contributor_EN.pdf)


## 引用

如需学术引用，请使用以下 BibTeX：
```bibtex
@software{JoyAgent-JDGenie,
  author = {Agent Team at JDCHO},
  title = {JoyAgent-JDGenie},
  year = {2025},
  url = {https://github.com/jd-opensource/joyagent-jdgenie},
  version = {0.1.0},
  publisher = {GitHub},
  email = {liuhaibo6@jd.com;jiashilin1@jd.com;liyang.1236@jd.com;liushangkun@jd.com;tianshaohua.1@jd.com;wangzhen449@jd.com;yaoting.2@jd.com;houkang6@jd.com;jinglingtuan@jd.com;guohongliang@jd.com}
}
```

## Contributors

<a href="https://github.com/jd-opensource/joyagent-jdgenie/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=jd-opensource/joyagent-jdgenie" />
</a>

# Star History
[![Star History Chart](https://api.star-history.com/svg?repos=jd-opensource/joyagent-jdgenie&type=Date&cache=false)](https://star-history.com/#jd-opensource/joyagent-jdgenie&Date)

欢迎沟通和联系我们  
<img width="396" height="396" alt="image" src="https://github.com/user-attachments/assets/275e8ca5-da74-4bf1-84e5-f5712aea0b94" />

[//]: # (![contact]&#40;./docs/img/contact.jpg&#41;)
