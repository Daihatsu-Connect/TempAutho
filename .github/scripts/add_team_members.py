#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
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
        
        # CSVファイルを読み込む
        with open('team_members.csv', 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            
            if len(rows) < 2:
                print("エラー: CSVファイルには少なくとも2行（チーム名と追加するメンバー）が必要です。")
                sys.exit(1)
            
            # 1行目からチーム名を取得
            team_name = rows[0][0].strip()
            
            # 2行目からメンバーリストを取得
            if len(rows) > 1 and len(rows[1]) > 0:
                members = [username.strip() for username in rows[1] if username.strip()]
            else:
                print("エラー: 2行目にメンバーが指定されていません。")
                sys.exit(1)
            
            print(f"チーム '{team_name}' に以下のメンバーを追加します: {', '.join(members)}")
            
            # 存在しないユーザーのリスト
            invalid_users = []
            
            try:
                # チームが存在するか確認
                print(f"チーム '{team_name}' を検索中...")
                team = org.get_team_by_slug(team_name)
                print(f"チーム '{team_name}' が見つかりました。")
                print(f"チームURL: https://github.com/orgs/{org_name}/teams/{team_name}")
                print(f"チームID: {team.id}")
                
                # 各メンバーをチームに追加
                for username in members:
                    try:
                        print(f"ユーザー '{username}' を検索中...")
                        user = g.get_user(username)
                        print(f"ユーザー '{username}' が見つかりました。ID: {user.id}")
                        
                        # ユーザーをチームに追加
                        print(f"ユーザー '{username}' をチーム '{team_name}' に追加しています...")
                        try:
                            team.add_membership(user)
                            print(f"成功: ユーザー '{username}' をチーム '{team_name}' に追加しました。")
                        except Exception as e:
                            print(f"エラー: ユーザー '{username}' をチーム '{team_name}' に追加できませんでした。")
                            print(f"エラー詳細: {str(e)}")
                    
                    except UnknownObjectException:
                        print(f"エラー: ユーザー '{username}' が見つかりません。")
                        invalid_users.append(username)
                        continue
            
            except UnknownObjectException:
                print(f"エラー: チーム '{team_name}' が見つかりません。")
                # 組織内の全チームを表示
                print("組織内の利用可能なチーム一覧:")
                for t in org.get_teams():
                    print(f"- {t.name} (slug: {t.slug})")
                sys.exit(1)
            
            # 存在しないユーザーがいる場合は報告
            if invalid_users:
                print("\n===== 処理結果の要約 =====")
                print(f"以下のユーザーは組織に存在しないため追加できませんでした: {', '.join(invalid_users)}")
                # 結果をファイルに書き出し
                with open('invalid_users.txt', 'w') as f:
                    f.write(','.join(invalid_users))
    
    except Exception as e:
        print(f"エラー: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()