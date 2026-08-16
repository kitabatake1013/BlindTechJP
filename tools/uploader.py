# Blind Tech JP Uploader

from argparse import ArgumentParser
from pathlib import Path
from datetime import datetime, timedelta
import re
import hashlib
from shutil import copy2
from mutagen.mp3 import MP3

AUDIO_DIR = Path("audio")
ARTICLE_DIR = Path("_posts")
FILENAME_PATTERN = re.compile(r"btj(ex)?(\d{3})\.mp3")  # 本編: btj001.mp3 / 号外: btjex001.mp3（いずれも3桁）
MAX_FILE_SIZE = 100 * 1024 * 1024  # GitHubにアップロードできる上限（100MB）


def file_hash(path):
	h = hashlib.sha256()
	with open(path, "rb") as fp:
		for chunk in iter(lambda: fp.read(1024 * 1024), b""):
			h.update(chunk)
	return h.hexdigest()

parser = ArgumentParser(description="Blind Tech JPの音声データと、それを再生するための記事をアップロードします。")
parser.add_argument("file", help="オーディオファイルのパス（リポジトリ外にあってもかまいません）")
args = parser.parse_args()
file = Path(args.file)
match = re.fullmatch(FILENAME_PATTERN, file.name)

if not file.exists():
	print(f"指定されたファイルが見つかりません: {file.absolute()}")
	exit(1)
elif file.suffix.lower() != ".mp3":
	print(f"mp3ファイルではありません: {file.name}")
	exit(1)
elif not match:
	print(f"ファイル名の形式が不正です: {file.name}")
	exit(1)
elif file.stat().st_size >= MAX_FILE_SIZE:
	print(f"ファイルサイズが100MB以上のため、GitHubにアップロードできません: {file.stat().st_size / 1024 / 1024:.1f}MB")
	exit(1)

is_special = match.group(1) is not None
num = match.group(2)
target_file = AUDIO_DIR / file.name

existing_files = []
existing_nums = []
for f in AUDIO_DIR.glob("btj*.mp3"):
	m = re.fullmatch(FILENAME_PATTERN, f.name)
	if not m:
		continue
	existing_files.append(f)
	if (m.group(1) is not None) == is_special:
		existing_nums.append(int(m.group(2)))
expected_num = f"{(max(existing_nums) + 1) if existing_nums else 1:03d}"

source_hash = file_hash(file)
duplicate_file = next((f for f in existing_files if file_hash(f) == source_hash), None)

if target_file.exists():
	print(f"同じ番号のファイルが既にアップロードされています: {file.name}")
	exit(1)
elif duplicate_file is not None:
	print(f"過去にアップロードした{duplicate_file.name}と内容が同じファイルです: {file.name}")
	exit(1)
elif num != expected_num:
	print(f"番号が連番になっていません（次にアップロードできるのは {expected_num} です）: {file.name}")
	exit(1)

copy2(file, target_file)
print(f"{file.name}をコピーしました。")

now = datetime.now()
slug = f"{match.group(1) or ''}{num}"
titlePrefix = f"号外" if is_special else f"#{num}"
articlePath = ARTICLE_DIR / f"{now:%Y-%m-%d}-{slug}.md"

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
	f"title: \"{titlePrefix} \"",
	"---",
]
with open(articlePath, "w", encoding="utf-8", newline="\n") as f:
	for line in lines:
		f.write(line + "\n")
print(f"{articlePath.name}を作成しました。")
