# GitHub Agent 项目全景图

把 GitHub 上真正在用的 Agent 项目按赛道梳理成一张可以搜索、筛选、排序的清单，用来解决一个具体问题：**想搭一个 Agent，到底该从哪个项目开始看。**

**在线浏览 → https://xiaowang018.github.io/agent-landscape/**

收录 **121 个仓库 / 15 个赛道 / 累计 723.9 万星标**。每个项目都标注了中文定位、适用人群、上手门槛和维护状态，而不是只丢一个 star 数排名。页面末尾另设「科研前沿」区块，收录 18 篇 2025–2026 年会改变 Agent 系统设计与评测结论的论文与基准（不计入上面的仓库统计）。本轮新增「Agent 学习路线」：从官方课程和框架教程入门，接着做项目，再用公开基准验证，不把课程证书或榜单分数当成工程能力。

---

## 这个页面里有什么

| 赛道 | 说明 | 数量 |
| --- | --- | :--: |
| 编排框架 / SDK | 搭 Agent 的底层骨架 | 21 |
| 编码 Agent | 写代码、改仓库、跑测试 | 21 |
| 低代码平台 / 工作流 | 拖拽或节点式搭建，少写代码 | 7 |
| 浏览器操作 | 让 Agent 自己上网 | 6 |
| 通用自主 Agent | 给个目标自己拆解执行 | 9 |
| 多智能体协作 | 多个角色分工配合 | 6 |
| 桌面 / 电脑操作 | 看屏幕、动鼠标、控本机 | 6 |
| 语音 Agent | 能听会说的实时对话 | 3 |
| 知识库 / RAG | 把私域文档变成 Agent 的上下文 | 8 |
| 深度研究 / 检索 | 自动调研并产出报告 | 6 |
| 记忆层 | 跨会话记住人和事 | 7 |
| 工具协议 / MCP | 给 Agent 装手脚的标准接口 | 9 |
| Agent 可观测 / 评测 | 看得见它干了什么、跑得好不好 | 6 |
| Agentic RL / 训练环境 | 训练 Agent 自己的策略 | 5 |
| Agent 基础设施 | 沙箱、运行时等底座 | 1 |

星标前八（截至 2026-11-24）：

| # | 项目 | 星标 | 语言 | 许可证 |
| :-: | --- | --: | --- | --- |
| 1 | [morluto/rea](https://github.com/morluto/rea) | 475,682 | TypeScript | MIT |
| 2 | [openclaw/openclaw](https://github.com/openclaw/openclaw) | 395,121 | TypeScript | MIT |
| 3 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 309,604 | JavaScript | MIT |
| 4 | [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) | 286,111 | TypeScript | MIT |
| 5 | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | 265,675 | Python | MIT |
| 6 | [anomalyco/opencode](https://github.com/anomalyco/opencode) | 228,818 | TypeScript | MIT |
| 7 | [n8n-io/n8n](https://github.com/n8n-io/n8n) | 211,913 | TypeScript | Sustainable Use |
| 8 | [Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | 188,155 | Python | Polyform + MIT |

一个比上次更极端的现象：**前八名里有六个是「成品 Agent / Harness」，没有一个传统意义上的框架。** 榜首 rea 用 Agent 做逆向工程拿到 47.6 万星，OpenClaw、Hermes 这类「装完就能常驻干活」的个人 Agent 运行时包揽第二和第五；n8n 是前八里唯一的可视化平台，LangChain 这种框架鼻祖已跌出前八。入口已经彻底从「自己搭」变成「装完直接用」。

第三个变化是「训练」这一层终于被补上了，新增赛道 **Agentic RL / 训练环境**：verl、slime、prime-rl、ART、OpenEnv。原因是这半年 arXiv 上的 Agent 研究重心明显从「怎么调提示词」挪到「怎么造可验证环境和 verifier」——SETA 造了 4,500+ 个终端环境、腾讯混元在做环境随模型一起变难、BIRD-RL 在解有状态数据环境的空间效率。选型上也多了个问题：跑通的流程要不要固化成小模型，把每次的推理钱省下来。

另一个增量是把「看不见的接线」补齐了：**A2A**（Google 发起、现归 Linux 基金会的 Agent 间通信协议）补上 MCP 没管的另一半——Agent 之间怎么发现彼此、怎么委派任务；**promptfoo** 和 **inspect_ai** 让评测能进 CI、能审计；**graphiti** 把记忆从「说过什么」推进到「这条现在还有效吗」。

另一个增量来自博主们的 2026 盘点：DeepSeek 官方的 Harness、用自己订阅跑编码舰队的 Orca、100 行代码的 mini-swe-agent、统管各家 CLI Agent 的 cc-switch 都是这轮补进来的新面孔。同时页面末尾新增「科研前沿」一节——评测基准正在从静态分数转向轨迹与环境级验证（AgentGym2、EvoClaw），记忆研究从「能不能记住」转向「何时该遗忘」（Memora），Agentic RL 的瓶颈从算法转向环境与 verifier（ToolVerse）。


---

## Agent 学习路线

按「先懂循环，再学编排，最后做验证」走。课程和文档链接均指向发布方或项目官方页面；课程内容、可用性与证书政策可能变化，开始前以原站为准。

| 阶段 | 资料 | 适合谁 / 学什么 | 建议产出 |
| --- | --- | --- | --- |
| 1. 建立心智模型 | [Anthropic：Building effective agents](https://www.anthropic.com/research/building-effective-agents) | 所有人；workflow 与 agent 的边界、提示词链/路由/并行/编排器-工作者/评估器-优化器 | 把一个任务分别画成固定流程和 Agent loop，说明为何选其一 |
| 2. 动手做第一个 Agent | [Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course/en/unit1/introduction) | 初学者；Think → Act → Observe、工具、smolagents，并发布到 Spaces | 做一个能调用工具并对结果做检查的 Agent |
| 3. 理解状态与控制流 | [DeepLearning.AI：AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) · [LangGraph 官方 quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart) | 有 Python 基础；从手写循环迁移到图、持久化、streaming、人类介入 | 做一个可暂停、恢复、人工批准的长任务 |
| 4. 横向比较开发栈 | [OpenAI Agents SDK 指南](https://developers.openai.com/api/docs/guides/agents) · [Google ADK 文档](https://google.github.io/adk-docs/) · [Microsoft Agent Framework 概览](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) | 已能写简单 Agent；比较工具调用、handoff、workflow、session 与观测 | 用同一小任务做两个实现，记录状态/错误处理差异 |
| 5. 评估与可靠性 | [SWE-bench leaderboard](https://www.swebench.com/) · [OSWorld](https://os-world.github.io/) · [WebArena](https://webarena.dev/) · [τ-bench](https://github.com/sierra-research/tau-bench) | 想验证真实任务能力；按编码、桌面、浏览器、工具交互选基准 | 为自己的任务写外部 checker、失败分类和回归集 |

### 学习时优先做的项目

- **最小工具 Agent**：不用框架先写一轮 observe → decide → act，给工具加 schema、超时、错误返回和步数上限；确认脚本能解决的部分就别交给模型。
- **带恢复的研究 Agent**：用 LangGraph 或 Microsoft Agent Framework 做搜索、引用收集、草稿、事实检查；加持久状态和人工审批，模拟进程中断后继续运行。
- **小型编码 Agent**：挑一个小型开源仓库，让 Agent 修一个 issue；测试必须由 Agent 之外的命令运行，统计成功率、重试数、耗时和 token 成本。
- **基准复现**：先跑 SWE-bench Verified 的单个样例或 OSWorld 的一个任务，保存环境版本、模型、提示、工具、完整轨迹。榜单数字只在配置可比时参考。

不建议一开始就做「多 Agent 自主公司」：先找一条单 Agent 轨迹的失败点，只有单一执行者确实卡住时才引入委派，并给每个子任务定义输入、输出、权限和验收器。

### 官方项目入口

| 项目 | 从这里开始 | 要学会的核心 |
| --- | --- | --- |
| [smolagents](https://huggingface.co/docs/smolagents/index) | [教程](https://huggingface.co/docs/smolagents/tutorials/overview) | 最小代码 Agent、工具、代码执行边界 |
| [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) | [Quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart) | state、节点/边、持久化、人工介入 |
| [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) | [官方指南](https://developers.openai.com/api/docs/guides/agents) | tools、handoffs、guardrails、tracing |
| [Google ADK](https://google.github.io/adk-docs/) | [Python quickstart](https://google.github.io/adk-docs/get-started/quickstart/) | Agent 与 workflow、工具、评估 |
| [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) | [First Agent](https://learn.microsoft.com/en-us/agent-framework/get-started/your-first-agent) | agents、harness、workflows、session 与 middleware |
| [Claude Agent SDK](https://docs.anthropic.com/en/docs/claude-code/sdk) | [Python SDK](https://github.com/anthropics/claude-agent-sdk-python) | 把 Claude Code 的工具循环集成到应用 |
| [Deep Agents](https://github.com/langchain-ai/deepagents) | [官方文档](https://docs.langchain.com/oss/python/deepagents/overview) | 长任务规划、文件系统、子 Agent；高层 Harness，需理解其默认授权与状态行为 |

### 常用基准入口

| 基准 | 主要测什么 | 官方入口 |
| --- | --- | --- |
| SWE-bench | 真实 GitHub issue 修复 | [项目与 leaderboard](https://www.swebench.com/) |
| OSWorld | 跨应用桌面 GUI 操作 | [项目页](https://os-world.github.io/) · [代码](https://github.com/xlang-ai/OSWorld) |
| WebArena | 自托管网站中的浏览器任务 | [项目页](https://webarena.dev/) · [代码](https://github.com/web-arena-x/webarena) |
| τ-bench | 多轮工具调用与业务规则遵循 | [代码与任务](https://github.com/sierra-research/tau-bench) |
| Terminal-Bench | 终端环境中的多步操作 | [项目与 leaderboard](https://www.tbench.ai/) |

---

## 数据是怎么来的

| 字段 | 来源 | 说明 |
| --- | --- | --- |
| 星标、Fork、语言、许可证、最后提交时间、创建时间 | GitHub REST API `/repos/{owner}/{repo}` | 实时抓取，非人工录入 |
| 分类、中文定位、适用人群、点评、上手门槛 | 人工标注 | 主观判断，可讨论 |

维护状态按最后提交时间自动判定：

- **活跃** —— 45 天内有提交
- **维护中** —— 210 天内有提交
- **沉寂** —— 超过 210 天无提交（这类不建议作为新项目选型）

上手门槛按"装完能不能直接跑"来分三档：**易**（装完能跑）／**中**（需读文档改代码）／**难**（需要理解其架构或研究背景）。

> 许可证标注为 `NOASSERTION` 的（n8n、Dify、AutoGPT、Flowise 等）已逐个人工核对，多为"附加条款 / Sustainable Use"这类**不完全开放**的许可。星标高不等于能随便商用，落地前请逐条读 LICENSE。

---

## 仓库结构

```
agent-landscape/
├── index.html    # 单文件页面，无外部依赖，双击即可在本地打开
└── data.json     # 数据快照（121 条），字段与页面一致
```

`index.html` 里没有 CDN、没有构建步骤、没有网络请求，断网也能正常筛选。

---

## 怎么更新

数据不是定时任务，是手动重抓。流程：

```bash
# 1. 改候选仓库列表（agent-projects/fetch.py 里的 REPOS）
python fetch.py      # 走核心 API，60 次/小时，504 也计次
python fetch2.py     # 核心配额用完后，改走 search API（10 次/分钟）
python fetch4.py     # 按 topic 批量检索兜底
python fetch5.py     # 个别仓库用镜像拿元数据

# 2. 补充中文标注（新增仓库必须在这步加，否则不会出现在页面上）
#    编辑 meta.py 的 META 字典

# 3. 生成页面
python gen.py        # 输出 index.html
```

抓数据时会遇到的两个真实问题：

1. **核心 API 未认证只有 60 次/小时，且 504 超时同样计次。** 所以脚本设计成"核心 API 打头，配额耗尽后自动降级到 search API 和 topic 检索"。
2. **仓库改名非常频繁。** 照老教程 clone 会 404，脚本里用 `ALIAS` 做映射。目前已确认的迁移：

   | 旧地址 | 现地址 |
   | --- | --- |
   | `geekan/MetaGPT` | `FoundationAgents/MetaGPT` |
   | `All-Hands-AI/OpenHands` | `OpenHands/OpenHands` |
   | `block/goose` | `aaif-goose/goose` |
   | `jlowin/fastmcp` | `PrefectHQ/fastmcp` |
   | `modelscope/agentscope` | `agentscope-ai/agentscope` |
   | `OpenInterpreter/open-interpreter` | `openinterpreter/openinterpreter` |
   | `gpt-engineer-org/gpt-engineer` | `AntonOsika/gpt-engineer` |
   | `sst/opencode` | `anomalyco/opencode` |
   | `strands-agents/sdk-python` | `strands-agents/harness-sdk` |
   | `volcengine/verl` | `verl-project/verl` |
   | `microsoft/autogen` / `microsoft/semantic-kernel` | `microsoft/agent-framework`（微软新一代 successor；旧仓库仍可作历史参考） |

---

## 关于

这份清单来自一次实际的选型需求：框架太多、评测文章太旧、star 数又不能直接当质量用。所以把"星数"和"它到底能干什么、适不适合我"放在一起看。

收录范围有明确边界：**只收 Agent 相关**，纯 LLM 应用框架、模型推理框架、聊天客户端不在内。判断标准是"这东西能不能自己决定下一步做什么"。

发现分类错了、定位写偏了、或者漏掉了重要项目，欢迎开 issue 指正。本仓库只整理公开信息，各项目的版权与许可证归属其原作者。
