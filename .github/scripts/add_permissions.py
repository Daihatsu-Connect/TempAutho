#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
import datetime
import pandas as pd
from dateutil import parser
from github import Github
from github.GithubException import UnknownObjectException

def validate_date(date_str):
    """日付が有効かつ一週間以内かを確認する"""
    try:
        end_date = parser.parse(date_str)
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        max_date = today + datetime.timedelta(days=7)
        
        if end_date > max_date:
            print(f"エラー: 終了日 {date_str} は一週間以上先です。")
            return False
        
        if end_date < today:
            print(f"エラー: 終了日 {date_str} は過去の日付です。")
            return False
            
        return True
    except ValueError:
        print(f"エラー: 無効な日付形式です: {date_str}")
        return False

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
    
    try:
        # 組織を取得
        org = g.get_organization(org_name)
        
        # 台帳ファイルの存在確認
        ledger_file = 'permissions_ledger.csv'
        if not os.path.exists(ledger_file):
            # 台帳ファイルが存在しない場合は作成
            with open(ledger_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['team_name', 'username', 'end_date', 'status'])
            ledger_df = pd.DataFrame(columns=['team_name', 'username', 'end_date', 'status'])
        else:
            # 台帳を読み込む
            ledger_df = pd.read_csv(ledger_file)
        
        # 新規申請を読み込む
        new_requests = []
        with open('request.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) != 3:
                    print(f"エラー: 無効な行形式です: {row}")
                    continue
                
                team_name = row[0].strip()
                username = row[1].strip()
                end_date_str = row[2].strip()
                
                # 日付の検証
                if not validate_date(end_date_str):
                    continue
                
                new_requests.append({
                    'team_name': team_name,
                    'username': username,
                    'end_date': end_date_str,
                    'status': 'pending'
                })
        
        # 新規申請を処理
        for request in new_requests:
            team_name = request['team_name']
            username = request['username']
            end_date_str = request['end_date']
            
            try:
                # チームが存在するか確認
                print(f"チーム '{team_name}' を検索中...")
                team = org.get_team_by_slug(team_name)
                print(f"チーム '{team_name}' が見つかりました。")
                print(f"チームURL: https://github.com/orgs/{org_name}/teams/{team_name}")
                print(f"チームID: {team.id}")
                
                # ユーザーが存在するか確認
                try:
                    print(f"ユーザー '{username}' を検索中...")
                    user = g.get_user(username)
                    print(f"ユーザー '{username}' が見つかりました。ID: {user.id}")
                except UnknownObjectException:
                    print(f"エラー: ユーザー '{username}' が見つかりません。")
                    request['status'] = 'error'
                    continue
                
                # ユーザーをチームに追加
                print(f"ユーザー '{username}' をチーム '{team_name}' に追加しています...")
                try:
                    team.add_membership(user)
                    print(f"成功: ユーザー '{username}' をチーム '{team_name}' に追加しました。終了日: {end_date_str}")
                    request['status'] = 'active'
                except Exception as e:
                    print(f"エラー: ユーザー '{username}' をチーム '{team_name}' に追加できませんでした。")
                    print(f"エラー詳細: {str(e)}")
                    request['status'] = 'error'
                
            except UnknownObjectException:
                print(f"エラー: チーム '{team_name}' が見つかりません。")
                # 組織内の全チームを表示
                print("組織内の利用可能なチーム一覧:")
                for t in org.get_teams():
                    print(f"- {t.name} (slug: {t.slug})")
                request['status'] = 'error'
                continue
        
        # 台帳を更新
        for request in new_requests:
            # 既存のエントリを確認
            mask = (ledger_df['team_name'] == request['team_name']) & (ledger_df['username'] == request['username'])
            if mask.any():
                # 既存のエントリを更新
                ledger_df.loc[mask, 'end_date'] = request['end_date']
                ledger_df.loc[mask, 'status'] = request['status']
            else:
                # 新しいエントリを追加
                ledger_df = pd.concat([ledger_df, pd.DataFrame([request])], ignore_index=True)
        
        # 台帳を保存
        ledger_df.to_csv(ledger_file, index=False)
        
        # request.csvをクリア
        with open('request.csv', 'w') as f:
            pass
        
        print(f"台帳が更新されました: {ledger_file}")
                
    except Exception as e:
        print(f"エラー: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()