# SeKnAck AI Skills

株式会社SeKnAckの社内配布用Codexスキルを管理するPrivateリポジトリです。

## 収録スキル

### aisetup-client-proposal

初回ヒアリングカルテのGoogle Sheets URLから、壁打ち、技術・見積承認、会社別提案画像、PDF、Google Drive URLまでを一括作成するスキルです。

[スキルフォルダを開く](https://github.com/seknackceo-droid/seknack-ai-skills/tree/main/aisetup-client-proposal)

### aisetup-business-research

公開情報から問い合わせ可能な企業だけを調査し、AIセットアップ事業の営業リストへ登録するスキルです。フォーム入力・送信は行いません。

[スキルフォルダを開く](https://github.com/seknackceo-droid/seknack-ai-skills/tree/main/aisetup-business-research)

### aisetup-inquiry-form-send

営業リストで人間が承認した行を対象に、問い合わせフォームへ送信者情報と承認済み文面を入力するスキルです。

[スキルフォルダを開く](https://github.com/seknackceo-droid/seknack-ai-skills/tree/main/aisetup-inquiry-form-send)

## インストール先

- macOS / Linux: `~/.codex/skills/[skill-name]`
- Windows: `%USERPROFILE%\.codex\skills\[skill-name]`

リポジトリをダウンロードし、利用するスキルフォルダを上記へコピーしてください。

## 起動例

```
$aisetup-client-proposal ヒアリングシート: https://docs.google.com/spreadsheets/d/...
$aisetup-business-research を使って、送信可能な企業を調査しAIセットアップ営業リストへ登録してください。
$aisetup-inquiry-form-send を使って、承認OKになった営業先の問い合わせフォームを入力してください。
```

## 取扱ルール

- このリポジトリはPrivateのまま運用する
- AIセットアップ事業で使うスキルは、GitHubを共有用マスターとして管理する
- GitHubへ登録後、営業管理スプレッドシートの情報保管庫にもURLを登録する
- 顧客固有情報、個人情報、パスワード、APIキーを保存しない
- 外部共有・Public変更は管理者承認後に行う
- 価格やサービス条件はライブの営業管理スプレッドシートを正とする
