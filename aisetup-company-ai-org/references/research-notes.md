# AGENTS.md調査ノート

checked_at: 2026-09-01

公式一次情報と公式リポジトリの実例を中心に、以下10件を確認した。このファイルは要点と採用判断だけを残し、原文は複製しない。

1. [OpenAI: Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
   - ルートから作業ディレクトリまでの階層指示、`AGENTS.override.md` の優先、既定合計32KiBを確認。
2. [OpenAI Codex source: agents_md.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/agents_md.rs)
   - 既定名 `AGENTS.md`、探索順、ワークスペース信頼の実装を確認。
3. [AGENTS.md public specification and examples](https://agents.md/)
   - 概要、セットアップ、テスト、スタイル、セキュリティ、完了条件の構成を採用。
4. [OpenAI Codex repository AGENTS.md](https://github.com/openai/codex/blob/main/AGENTS.md)
   - 対象範囲、禁止、条件別テスト、レビュー基準の具体化を採用。長大化は採用しない。
5. [OpenAI Agents Python repository AGENTS.md](https://github.com/openai/openai-agents-python/blob/main/AGENTS.md)
   - 必須規則、レビュー、構造、運用を分け、適用条件と除外を対で書く方法を採用。
6. [OpenAI Codex Security repository AGENTS.md](https://github.com/openai/codex-security/blob/main/AGENTS.md)
   - 外部取得物を権限とみなさない、公開前機密監査、合成データ優先を採用。
7. [Anthropic: CLAUDE.md memory](https://code.claude.com/docs/en/memory)
   - Claude Code固有ファイルとCodexの差を分離。具体的・簡潔・200行未満の推奨を参考に採用。
8. [Anthropic: Debug your configuration](https://code.claude.com/docs/en/debug-your-config)
   - 指示文と強制的な権限・フック・サンドボックスの違いを採用。
9. [Google Gemini CLI: GEMINI.md](https://geminicli.com/docs/cli/gemini-md/)
   - 製品ごとのファイル名と階層読み込み差を確認。自動互換はしない。
10. [GitHub Copilot: Add repository custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions)
    - リポジトリ全体、path-specific、agent instructionの区別と、最も近い階層の優先を参考に採用。

## 統合原則

- ルートは全社共通、配下は差分だけを書く。
- 責任、入力、出力、許可、禁止、承認条件、完了条件を検証可能な形で書く。
- 各 `AGENTS.md` は200行未満をSkill独自の品質基準とする。これはCodexの仕様上限ではない。
- 重要な禁止はファイルだけで強制せず、人間承認と技術的制御を分ける。
- 起動ディレクトリによる読み込み差と、同一階層の競合を検査する。
