#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import pandas as pd
from dateutil import parser
from github import Github
from github.GithubException import UnknownObjectException

def main():
    # 環境変数からトークンを取得
    token = os.environ.get('GH_TOKEN')
    # 組織名をハードコーディング
    org_name = "Daihatsu-Connect"
    
    if not token:
        print("エラー: 環境変数 GH_TOKEN が設定されていません。")
        sys.exit(1)
    
    # GitHub APIに接続
    g = Github(token)
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    try:
        # 組織を取得
        org = g.get_organization(org_name)
        
        # 台帳ファイルの存在確認
        ledger_file = 'permissions_ledger.csv'
        if not os.path.exists(ledger_file):
            print(f"エラー: 台帳ファイル {ledger_file} が見つかりません。")
            sys.exit(1)
        
        # 台帳を読み込む
        ledger_df = pd.read_csv(ledger_file)
        
        # 台帳を更新するためのフラグ
        updated = False
        
        # アクティブなエントリを処理
        for index, row in ledger_df[ledger_df['status'] == 'active'].iterrows():
            team_name = row['team_name']
            username = row['username']
            end_date_str = row['end_date']
            
            try:
                # 終了日を解析（整数の場合は文字列に変換）
                if isinstance(end_date_str, int):
                    end_date_str = str(end_date_str)
                end_date = parser.parse(end_date_str)
                
                # 終了日が今日以前かチェック
                if end_date <= today:
                    print(f"期限切れを検出: チーム '{team_name}', ユーザー '{username}', 終了日 '{end_date_str}'")
                    
                    try:
                        # チームが存在するか確認
                        team = org.get_team_by_slug(team_name)
                        
                        # ユーザーが存在するか確認
                        try:
                            user = g.get_user(username)
                            
                            # ユーザーがチームのメンバーか確認
                            if team.has_in_members(user):
                                # ユーザーをチームから削除
                                team.remove_membership(user)
                                print(f"削除: ユーザー '{username}' をチーム '{team_name}' から削除しました。期限: {end_date_str}")
                                # 台帳のステータスを更新
                                ledger_df.at[index, 'status'] = 'expired'
                                updated = True
                            else:
                                print(f"スキップ: ユーザー '{username}' はチーム '{team_name}' のメンバーではありません。")
                                # 台帳のステータスを更新
                                ledger_df.at[index, 'status'] = 'expired'
                                updated = True
                                
                        except UnknownObjectException:
                            print(f"エラー: ユーザー '{username}' が見つかりません。")
                            continue
                        
                    except UnknownObjectException:
                        print(f"エラー: チーム '{team_name}' が見つかりません。")
                        continue
                else:
                    print(f"有効: チーム '{team_name}', ユーザー '{username}', 終了日 '{end_date_str}' はまだ有効です。")
                    
            except ValueError:
                print(f"エラー: 無効な日付形式です: {end_date_str}")
                continue
        
        # 台帳を更新
        if updated:
            # 期限切れのエントリを削除
            ledger_df = ledger_df[ledger_df['status'] != 'expired']
            
            # 台帳の内容をログ出力
            print("台帳に書き込む内容:")
            for index, row in ledger_df.iterrows():
                print(f"  {row['team_name']}, {row['username']}, {row['end_date']}, {row['status']}")
            
            ledger_df.to_csv(ledger_file, index=False)
            print(f"台帳が更新されました: {ledger_file}")
                
    except Exception as e:
        print(f"エラー: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()