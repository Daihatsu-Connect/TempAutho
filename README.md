# 用途
一時的なgithubの権限を申請する。

# 前提条件
- 申請者ならびに対象者はOrganization(Daihatsu-Connect)に所属していること。
- 追加先のteam名がOrganization(Daihatsu-Connect)に存在すること。

# 使い方
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
