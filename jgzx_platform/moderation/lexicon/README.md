# 敏感词库来源

本目录词库来自开源项目 [Sensitive-lexicon](https://github.com/konsheng/Sensitive-lexicon) 的 `Vocabulary` 目录。

- 许可证：见上游仓库 LICENSE
- 更新方式：运行 `python jgzx_platform/moderation/download_lexicon.py` 重新下载
- 自定义词条：编辑同目录下的 `../sensitive_words.txt`

## 精简加载策略

检测引擎**不会**加载目录下全部 `.txt`（如 `零时-Tencent.txt` 等体量过大且易误伤），仅加载以下分类：

| 文件 | 类别 |
|------|------|
| `色情词库.txt`、`色情类型.txt` | 黄 |
| `涉枪涉爆.txt` | 暴力 |
| `反动词库.txt`、`政治类型.txt` | 政治 |
| `../sensitive_words.txt` | 赌、毒及项目自定义补充 |

最短匹配长度：**开源分类词库为 3 字**；**`sensitive_words.txt` 自定义词条为 2 字**（如「博彩」「冰毒」等明确违规词）。
