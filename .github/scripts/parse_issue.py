#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys

def parse_issue_body(body):
    """Issueの本文から必要な情報を抽出する"""
    # 「# 以下を編集」から「---」までの部分を抽出
    pattern = r'# 以下を編集(.*?)---'
    match = re.search(pattern, body, re.DOTALL)
    
    if not match:
        print("エラー: 指定された形式でIssue本文が記載されていません。", file=sys.stderr)
        return None
    
    content = match.group(1).strip()
    
    # 各項目を抽出
    team = None
    user = None
    date = None
    
    team_match = re.search(r'付与したいチーム:(.+?)(?:\n|$)', content)
    user_match = re.search(r'付与するユーザ:(.+?)(?:\n|$)', content)
    date_match = re.search(r'期限:(.+?)(?:\n|$)', content)
    
    if team_match:
        team = team_match.group(1).strip()
    if user_match:
        user = user_match.group(1).strip()
    if date_match:
        date = date_match.group(1).strip()
    
    # 必要な情報が揃っているか確認
    if not team or not user or not date:
        print("エラー: 必要な情報が不足しています。", file=sys.stderr)
        print(f"チーム: {team}", file=sys.stderr)
        print(f"ユーザー: {user}", file=sys.stderr)
        print(f"期限: {date}", file=sys.stderr)
        return None
    
    # CSVフォーマットで出力
    return f"{team}, {user}, {date}"

def main():
    # 標準入力から本文を読み込む
    body = sys.stdin.read()
    
    # 本文を解析
    csv_content = parse_issue_body(body)
    
    if csv_content:
        print(csv_content)
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())