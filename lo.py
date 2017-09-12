##################################################################################
#
#                               lo.py
#                               ver 0.0.1
#
#   COMIC LOの最新情報を取得できる素敵なスクリプト
#   最新号に掲載されている作品と作家名一覧を表示します
#   ネタ&ベースソース元→ http://qiita.com/sessions/items/a4fa1e0c83418d728c45
#   
#   HOWTO
#       PATHが通っている場所にloとして置くか、aliasで登録 
#   動作環境
#       python3以上
#   オプション
#       -l：最新号の詳細も表示
#   
##################################################################################

# coding:utf-8
#! /usr/bin/env python3
from urllib.request import urlopen
import re
import enum
import sys 

# オプションリスト
Option = enum.Enum('Option', 'none, long')

args = sys.argv # コマンドライン引数
contents = []   # タイトルリスト
writers = []    # 作家
details = []    # 今月号詳細(-lオプション) 
title = ''      # タイトル(-lオプション)

# 入力されたオプションを取得
# - returns: 入力されたオプション Option型
#            無効なオプションの場合はNoneで返す
def getArgs():
    if len(args) == 1:
        return Option.none.value
    elif len(args) > 1 and args[1] == '-l':
        return Option.long.value
    else:
        # 無効なオプション
        pass

# 我らが偉大なる茜新社様よりLOの新刊情報を取得
def getContentsAndWriters():
    # メインページのリンクから/item/で最初に見つかったやつを取得しているっぽい(最初=最新号)
    with urlopen("http://www.akaneshinsha.co.jp/category/item/itemgenre/itemad/magazine-ad/comic-lo/") as res:
        html = res.read().decode("utf-8")
    urlprefix = "http://www.akaneshinsha.co.jp/item/"
    founds = re.findall(r'<a href="{}(\d+?)/?".+?>'.format(urlprefix), html)
    if not founds:
        quit()

    # 最新号のページから作品一覧取得
    with urlopen(urlprefix + founds[0]) as res:
        html = res.read().decode("utf-8").replace("\n", " ")
    founds = re.findall(
        r'<div class="freetxt">\s*<p>.+?</p>\s*<p>(.+?)</p>', html)
    if not founds:
        quit()

    # -lオプション
    if getArgs() == Option.long.value:
        global title
        title = re.findall(r'<title>.+?</title>', html)
        title = re.sub('<title>|</title>', '', title[0])
        title = re.sub('　', ' ', title)
        print(title)
        global details
        details = re.findall(r'<dd>.+?</dd>|<dt>.+?</dt>', html)
        details = details[4:len(details)]
        for i, detail in enumerate(details):
            details[i] = re.sub('<dd>|</dd>|<dt>|</dt>', '', details[i])

    # 作家取得
    # FIXME: 先頭だけどうしてもまとめて正規表現で取れなかったので個別で取得
    firstWriter = re.search('.+?…', founds[0]).group(0)
    global writers
    writers = re.findall('>\s.+?…', founds[0])
    writers.insert(0, firstWriter)
    # 余分な文字を削除
    for i, writer in enumerate(writers):
        writers[i] = re.sub('>\s|…', '', writers[i])

    founds = re.findall(r'「(.+?)」', founds[0])
    global contents
    contents = founds

# 引数で渡された配列の要素(文字列)の中で最大の文字数を返す
# - parameter list: 文字列が格納された配列
def maxCharacterLength(list):
    length = 0
    for item in list:
        if length < len(item):
            length = len(item)
    return length

# -lオプションによる詳細表示
def showDetails():
    global details
    if len(details) > 0:
        item = ''
        print('------------------------')
        for i, detail in enumerate(details):
            if i % 2 == 0:
                pass
            else:
                print(details[i-1] + '：' + detail)
        print('------------------------')

# 表示
def showContents():
    # -lオプション
    if getArgs() == Option.long.value:
        showDetails()

    # 作家で一番長い文字数
    maxWriterLength = maxCharacterLength(writers)
    color = 202
    for i, content in enumerate(contents):
        # MAXから今表示する作家の文字数を引いて埋める空白数を出す
        spaceNum = maxWriterLength - len(writers[i])
        writer = writers[i].ljust((spaceNum * 2) + len(writers[i]) + 1, ' ') 
        print('\033[38;5;%dm%s\033[0m' % (color, writer + content))
        if (i + 1) % (max(4, len(contents)) // 4) == 0:
            color += 1

# メイン
def main():
    # オプションの判定
    args = getArgs()
    if args is None:
        print('無効なオプションです')
        quit()

    getContentsAndWriters()
    showContents()

# Start processing...
if __name__ == "__main__":
    main()
