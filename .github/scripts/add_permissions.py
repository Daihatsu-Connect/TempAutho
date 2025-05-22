#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
import datetime
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
        
        # CSVファイルを読み込む
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
                
                try:
                    # チームが存在するか確認
                    team = org.get_team_by_slug(team_name)
                    
                    # ユーザーが存在するか確認
                    try:
                        user = g.get_user(username)
                    except UnknownObjectException:
                        print(f"エラー: ユーザー '{username}' が見つかりません。")
                        continue
                    
                    # ユーザーをチームに追加
                    team.add_membership(user)
                    print(f"成功: ユーザー '{username}' をチーム '{team_name}' に追加しました。終了日: {end_date_str}")
                    
                except UnknownObjectException:
                    print(f"エラー: チーム '{team_name}' が見つかりません。")
                    continue
                
    except Exception as e:
        print(f"エラー: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()