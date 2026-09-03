---
name: aisetup-company-ai-org
description: AIエージェント初心者の企業に、安全な質問と構成プレビューを経て、全社統括と必要部署の階層フォルダ、AGENTS.md、AI責任者定義、承認・情報分類ルールを一括生成する。Codex向けの会社AI組織の初期導入、授業用の架空企業演習、実際の会社向けの非公開下書き作成で使う。実データ処理、権限設定、外部送信、法的承認の代行には使わない。
metadata:
  short-description: 初心者企業向け安全な部署別AGENTS.md一括生成
---

# 企業AI組織スターター

会社の実際の組織を推測せず、機密に触れない質問だけで、Codex向けの階層型 `AGENTS.md` スターターを作る。

## 正しい期待値

- 標準名は `agent.md` ではなく `AGENTS.md` である。
- `AGENTS.md` はフォルダ配下の作業指示であり、AI社員を常駐起動する権限設定ではない。
- 利用者への質問、選択肢、プレビュー、フォルダ名、役割名、状態名は日本語で示す。英語IDは設定JSON内部だけで使い、利用者へ選ばせない。
- Windows向けの保存先、同期フォルダ検知、安全停止はコードと自動テストで確認する。Windows以外で検査した場合は、Windows実機で確認済みとは報告しない。
- 責任者AIの確認は「責任者確認済み」、人間の確定後だけ「人間承認済み」とする。
- 絶対禁止を指示文だけで保証しない。権限、安全な隔離環境、外部サービス連携の制限、人間承認は別途実装が必要と明示する。

## 実行フロー

1. 最初に「個人名、連絡先、顧客名、パスワード、APIキー、契約内容、実データは入力しない」と伝える。
2. [references/interview.md](references/interview.md) を読み、日本語で1問ずつ質問する。企業名は必ず仮名・案件コードの選択肢も出す。
3. [references/departments.md](references/departments.md) で「実在」「兼務」「不要」「要確認」を整理する。実在しない部署や権限を確定事実として作らない。
4. [references/security-baseline.md](references/security-baseline.md) を読み、プロファイル、扱う情報区分、承認役職、外部AI利用可否を設定する。
5. 生成前に、会社表示名を除いた構成プレビューと「作る/作らない/要確認」を提示する。
6. 基本保存先は端末内のローカルフォルダとする。macOS/Linuxは利用者の `Documents/AI導入研修`、Windowsは `%USERPROFILE%\Documents\AI導入研修` を提案する。WindowsのDocumentsがOneDrive等へ移されている場合はローカル扱いにしない。利用者が別の安全なローカル場所を指定した場合はそれを優先する。Google Drive、OneDrive、Dropbox、iCloud等の既知の同期パスはスクリプトが停止する。利用者が明示して共有範囲を確認した場合だけ `--confirm-cloud-sync-location` で解除する。
7. JSON設定をGit・`skills/`・同期共有フォルダから分離したローカルの非公開フォルダに保存し、POSIX環境でモード `600` にする。まず `--dry-run` で確認する。
8. 生成先が「この会社または授業専用の、アクセス制限されたローカルフォルダ」だと人間が確認した後だけ、`--confirm-private-output` 付きで生成する。
   - macOS/Linux: 所有者だけが読める設定をスクリプトで検査する。
   - Windows: POSIX権限値を使えないため、フォルダの「プロパティ → セキュリティ」で、利用者と許可された管理者だけがアクセスできることを人間が確認する。確認できない場合は生成しない。
9. `scripts/validate_company_ai_org.py` で全検査する。不合格のまま実運用・共有しない。
10. 作成ファイル、未確定、技術的に未強制の安全管理、次の人間確認を報告する。

## コマンド

```bash
python3 scripts/generate_company_ai_org.py \
  --config /private/path/company-ai-org-config.json \
  --output /private/path/company-ai-org \
  --dry-run

python3 scripts/generate_company_ai_org.py \
  --config /private/path/company-ai-org-config.json \
  --output /private/path/company-ai-org \
  --confirm-private-output \
  --confirm-access-restricted \
  --confirm-no-sensitive-data

python3 scripts/validate_company_ai_org.py /private/path/company-ai-org
```

## 停止条件

- 実企業導入で人間の最終承認役職が未定。
- 外部AI利用可否、保存先、公開範囲が未定。
- 既存フォルダと衝突する。スクリプトは上書きせず停止する。
- 生成先または設定JSONがGit管理・いずれかの `skills/` 配下にある。
- 個人情報・機密情報の実体が回答へ入っている。
- Codex以外の製品向け互換ファイルを同時生成しようとしている。
- 権限、安全な隔離環境、外部サービス連携の制限を `AGENTS.md` だけで代替しようとしている。

## 共有境界

- このSkill本体、空テンプレート、架空例は公開可能。
- 質問回答、JSON設定、会社別生成物、顧客固有ルールは公開リポジトリやSkillフォルダへ入れない。
- クラウドへの移動、同期、外部共有、Git push、共有リンク発行はそれぞれ別の人間承認ゲートとする。

## 調査根拠

`AGENTS.md` 系の公式一次情報10件と採用判断は [references/research-notes.md](references/research-notes.md) に分離してある。更新時は原始URLを再確認する。
