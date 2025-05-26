#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
import datetime
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
    
    try:
        # 組織を取得
        org = g.get_organization(org_name)
        
        errors = []
        
        # CSVファイルを読み込む
        with open('request.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if not row or len(row) == 0:
                    continue
                    
                if len(row) != 3:
                    errors.append(f"無効な行形式です: {row}")
                    continue
                
                team_name = row[0].strip()
                username = row[1].strip()
                end_date_str = row[2].strip()
                
                # チームが存在するか確認
                try:
                    team = org.get_team_by_slug(team_name)
                    print(f"チーム '{team_name}' が見つかりました。")
                except UnknownObjectException:
                    errors.append(f"チーム '{team_name}' が見つかりません。")
                
                # ユーザーが存在するか確認
                try:
                    user = g.get_user(username)
                    print(f"ユーザー '{username}' が見つかりました。")
                    # ユーザーが組織のメンバーか確認
                    if not org.has_in_members(user):
                        errors.append(f"ユーザー '{username}' は組織 '{org_name}' のメンバーではありません。")
                except UnknownObjectException:
                    errors.append(f"ユーザー '{username}' が見つかりません。")
                
                # 日付の検証
                try:
                    if isinstance(end_date_str, int):
                        end_date_str = str(end_date_str)
                    end_date = parser.parse(end_date_str)
                    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    if end_date <= today:
                        errors.append(f"終了日 '{end_date_str}' は過去の日付です。")
                    else:
                        print(f"終了日 '{end_date_str}' は有効です。")
                except ValueError:
                    errors.append(f"無効な日付形式です: '{end_date_str}'")
        
        # エラーがあれば出力して終了
        if errors:
            print("検証エラー:")
            for error in errors:
                print(f"- {error}")
            sys.exit(1)
        else:
            print("検証成功: すべての項目が正常です。")
            
    except Exception as e:
        print(f"エラー: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()