# SeKnAck AI Skills

株式会社SeKnAckが公開配布するCodexスキルを管理するPublicリポジトリです。

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

### aisetup-company-ai-org

AIエージェント初心者向けに、安全な日本語の質問を1問ずつ行い、会社全体と必要部署のAI責任者・AI担当者・承認ルールをローカルフォルダへ一括生成するスキルです。macOSとLinuxで利用でき、Windows向けの保存先・同期フォルダ検知・安全停止も実装しています。Windows実機での確認はまだ行っていません。

[スキルフォルダを開く](https://github.com/seknackceo-droid/seknack-ai-skills/tree/main/aisetup-company-ai-org)

## 初めて使う方のインストール手順

1. GitHub画面の「Code」を押し、「Download ZIP」を選びます。
2. ダウンロードしたZIPを展開します。
3. 使いたいスキルのフォルダを、次の場所へコピーします。
   - macOS / Linuxの例: `~/.codex/skills/aisetup-company-ai-org`
   - Windowsの例: `%USERPROFILE%\.codex\skills\aisetup-company-ai-org`
4. Codexを再起動するか、新しい会話を開きます。
5. 下の起動文を、ターミナルではなくCodexの入力欄へ貼り付けます。

別のスキルを使う場合は、上の `aisetup-company-ai-org` をそのスキルのフォルダ名へ置き換えます。

## Codexの入力欄へ貼る起動例

```
$aisetup-client-proposal ヒアリングシート: https://docs.google.com/spreadsheets/d/...
$aisetup-business-research を使って、送信可能な企業を調査しAIセットアップ営業リストへ登録してください。
$aisetup-inquiry-form-send を使って、承認OKになった営業先の問い合わせフォームを入力してください。
$aisetup-company-ai-org を使って、初心者向けの日本語で質問を1問ずつ行い、端末内の非公開ローカルフォルダへ会社AI組織を作成してください。
```

## 取扱ルール

- このリポジトリはPublicとして運用し、公開可能な汎用スキルだけを置く
- AIセットアップ事業で使うスキルは、GitHubを共有用マスターとして管理する
- GitHubへ登録後、営業管理スプレッドシートの情報保管庫にもURLを登録する
- 顧客固有情報、個人情報、会社固有の設定、生成済み会社フォルダ、パスワード、APIキーを保存しない
- 公開内容の追加・変更は管理者の依頼または承認後に行う
- 価格やサービス条件はライブの営業管理スプレッドシートを正とする
