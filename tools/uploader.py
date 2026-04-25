# Blind Tech JP Uploader

from argparse import ArgumentParser
from pathlib import Path
from datetime import datetime, timedelta
import re
from shutil import copy2
from mutagen.mp3 import MP3

AUDIO_DIR = Path("audio")
ARTICLE_DIR = Path("_posts")
FILENAME_PATTERN = re.compile(r"btj(\d+)\.mp3")

parser = ArgumentParser(description="Blind Tech JPの音声データと、それを再生するための記事をアップロードします。")
parser.add_argument("file", help="オーディオファイルのパス（リポジトリ外にあってもかまいません）")
args = parser.parse_args()
file = Path(args.file)

if not file.exists():
	print(f"指定されたファイルが見つかりません: {file.absolute()}")
	exit(1)
elif not re.fullmatch(FILENAME_PATTERN, file.name):
	print(f"ファイル名の形式が不正です: {file.name}")
	exit(1)

target_file = AUDIO_DIR / file.name
if not target_file.exists():
	copy2(file, target_file)
	print(f"{file.name}をコピーしました。")

now = datetime.now()
progNum = re.match(FILENAME_PATTERN, file.name).group(1)
articlePath = ARTICLE_DIR / f"{now:%Y-%m-%d}-{progNum}.md"

# 記事の各行に記載する内容のリスト（改行コードは入れない）
lines = [
	"---",
	"actor_ids:",
	"  - 北畠一翔",
	f"audio_file_path: /{target_file.absolute().relative_to(Path.cwd()).as_posix()}",
	f"audio_file_size: {target_file.stat().st_size}",
	f"date: {now:%Y-%m-%d %H:%M:%S} +0900",
	"description: ",
	f"duration: \"{timedelta(seconds=MP3(target_file).info.length)}\"",
	"layout: article",
	f"title: \"#{progNum} \"",
	"---",
]
with open(articlePath, "w", encoding="utf-8", newline="\n") as f:
	for line in lines:
		f.write(line + "\n")
print(f"{articlePath.name}を作成しました。")