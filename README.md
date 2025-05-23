# 用途
一時的なgithubの権限を申請する。

# 前提条件
- 申請者ならびに対象者はOrganization(Daihatsu-Connect)に所属していること。
- 追加先のteam名がOrganization(Daihatsu-Connect)に存在すること。

# 使い方

## 方法1: Issueから申請する（推奨）
1. 以下の形式でIssueを作成する
   - タイトル: 任意（例: 「権限申請」）
   - 本文: 申請内容を以下のフォーマットで記載
     ```csv
     24pf-jp-dmc-dev-member, dmc-tdaihatsu, 20250505
     24pf-jp-dmc-pf-member, tpd-abcdef, 20250506
     ```
2. Issueを作成すると自動的にブランチとPRが作成される
3. PRが承認されマージされると権限が付与される

## 方法2: 手動で申請する
1. ブランチをきる。以下命名規則。
   ```csv
   request/{連番}
   ```
2. request.csv に以下のフォーマットで申請内容を記載する。
   ```csv
   24pf-jp-dmc-dev-member, dmc-tdaihatsu, 20250505
   24pf-jp-dmc-pf-member, tpd-abcdef, 20250506
   ```
   - 左から、追加希望のteam名, アカウント名, 終了日(一週間以内)
   - 上書きする。複数行可能。
3. mainにPRを出す。
4. 承認後、PRをマージする。
5. 反映される。

# 手動実行
GitHub Actionsの「Actions」タブから「一時的な権限付与」ワークフローを選択し、「Run workflow」ボタンをクリックすることで手動実行も可能です。

# 権限管理の仕組み
1. 申請内容は `request.csv` に記載されます
2. 権限付与アクションが実行されると、申請内容が処理され `permissions_ledger.csv` に記録されます
3. 毎日午前0時に期限切れ権限削除アクションが実行され、期限切れの権限が自動的に削除されます
4. 削除されたエントリは台帳から完全に削除されます

# 台帳ファイル
`permissions_ledger.csv` には以下の情報が記録されます：
- team_name: チーム名
- username: ユーザー名
- end_date: 終了日
- status: ステータス（pending, active, error）