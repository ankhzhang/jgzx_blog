# 敏感词库来源

本目录词库来自开源项目 [Sensitive-lexicon](https://github.com/konsheng/Sensitive-lexicon) 的 `Vocabulary` 目录。

- 许可证：见上游仓库 LICENSE
- 更新方式：运行 `python jgzx_platform/moderation/download_lexicon.py` 重新下载
- 自定义词条：编辑同目录下的 `../sensitive_words.txt`

检测引擎启动时会自动加载 `sensitive_words.txt` 与本目录下全部 `.txt` 文件。
