# 金融研究智能体示例

本示例展示了如何使用 Agents SDK 构建一个功能更丰富的金融研究智能体。该模式类似于 `research_bot` 示例,但包含更专业化的子智能体和验证步骤。

工作流程如下:

1. **规划**: 规划智能体将最终用户的请求转换为与金融分析相关的搜索词列表——最新新闻、财报电话会议、公司文件、行业评论等。
2. **搜索**: 搜索智能体使用内置的 `WebSearchTool` 为每个搜索词检索简洁的摘要。(如果你已索引 PDF 或 10-K 报表,也可以添加 `FileSearchTool`。)
3. **子分析师**: 额外的智能体(例如基本面分析师和风险分析师)作为工具暴露出来,以便写作智能体可以内联调用它们并整合其输出结果。
4. **写作**: 高级写作智能体将搜索片段和任何子分析师摘要整合成一份长篇 Markdown 报告以及一份简短的执行摘要。
5. **验证**: 最终的验证智能体审核报告,检查明显的不一致或缺失的来源引用。

你可以使用以下命令运行示例:

```bash
python -m examples.financial_research_agent.main
```

并输入类似这样的查询:

```
Write up an analysis of Apple Inc.'s most recent quarter.
```

### 启动提示词

写作智能体的种子指令类似于:

```
You are a senior financial analyst. You will be provided with the original query
and a set of raw search summaries. Your job is to synthesize these into a
long‑form markdown report (at least several paragraphs) with a short executive
summary. You also have access to tools like `fundamentals_analysis` and
`risk_analysis` to get short specialist write‑ups if you want to incorporate them.
Add a few follow‑up questions for further research.
```

你可以调整这些提示词和子智能体,以适应你自己的数据源和首选的报告结构。
