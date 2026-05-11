# Security Policy

## 报告漏洞

如果你发现安全问题（例如可被恶意 `.notes` 文件触发的解析崩溃、内存耗尽、文件覆盖等），请通过以下方式联系：

- **首选**：在 GitHub 上提交一个标记为 `security` 的 [issue](https://github.com/micherwa/yinxiang-to-markdown/issues/new)，先不公开复现细节
- 我会确认后与你协调披露时间，修复发布后再补充技术细节

## 已知边界

本工具的攻击面仅限于"解析本地 `.notes` 文件并生成本地 Markdown / 资源文件"：

- 不进行任何网络通信
- 不需要任何凭证
- 不调用印象笔记 API
- XML 解析使用 `defusedxml`，已防御 XXE / Billion Laughs 等常见 XML 攻击
- HMAC 校验先于 AES 解密，密文被篡改会立即拒绝

如果你处理的是**自己导出**的 `.notes` 文件，几乎不存在攻击面。如果你打算用本工具批量处理来源不明的文件，请额外确认上述防护是否满足你的威胁模型。

## 支持版本

仅维护最新版本（main 分支与最新 release）。
