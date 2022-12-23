import re
import os
import glob
from pathlib import Path
from fontTools.ttLib import TTFont
import argparse as A


def parse_args() -> A.Namespace:
    parser = A.ArgumentParser()
    parser.add_argument(
        "--lang",
        "-l",
        type=str,
        default="zh_CN",
        choices=["zh_CN", "en_US", "ja_JP", "ko_KR", "zh_TW"],
        help="Language of the game data, default is zh_CN.",
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        type=str,
        default="output",
        help="Output directory, default is ./output.",
    )
    parser.add_argument(
        "--gamedata_dir",
        "-g",
        type=str,
        default="ArknightsGameData",
        help="Game data directory, default is ./ArknightsGameData.",
    )
    parser.add_argument(
        "--font_dir",
        "-f",
        type=str,
        default="fonts/SubsetOTF",
        help="Font directory, default is ./fonts/SubsetOTF.",
    )
    return parser.parse_args()


def get_supported_chars(fonts_dir: os.PathLike):
    unicode_map = {}
    for f in os.listdir(fonts_dir):
        if not f.endswith("otf"):
            continue
        fontType = os.path.join(fonts_dir, f)
        font = TTFont(fontType)
        unicode_map = font['cmap'].tables[0].ttFont.getBestCmap()
        break
    return unicode_map


def split_document(document: str, unicode_map: dict):
    result = set()
    document = document.replace(r'\"', "@@")
    match = re.search(r'"[^"]*": "([^"]*)"|"([^"]*)"', document)
    if match is None:
        return result
    content = match.groups()[0] or match.groups()[1]

    if not content or r'■■■■■■■■■■■■■■■■■■\n■■■■■■■■■■\n■■■■■\n\n' in content:
        return result
    content = content.replace("@@", r'\"')
    content = content.replace("\\\\", "\\")
    content = content.replace("\\\"", "\"")
    content = content.replace("\\n", "\n")
    content = content.replace("\\t", "\n")
    content = content.replace("\t", "\n")
    content = content.replace("......", "\n")
    content = re.sub(r"<.*?>|{.*?}", "", content)
    content = content.replace("\r", "")
    content = content.replace(" ", "")

    lines = [
        line for line in content.split("\n") if line and not line.isspace()
    ]
    for line in lines:
        if all([ord(ch) in unicode_map.keys()
                for ch in line]) and any([not ch.isascii() for ch in line]):
            result.add(line)
    return result


def find_all_wording(data_dir, unicode_map):
    result = set()
    for file in glob.glob(os.path.join(data_dir, "*.json")):
        lines = None
        with open(os.path.join(file), "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            result.update(split_document(line, unicode_map))
    return result


def main(args):
    client = args.lang
    font_lang = client[-2:]
    unicode_map = get_supported_chars(Path(args.font_dir) / font_lang)
    wording = find_all_wording(
        os.path.join(args.gamedata_dir, client, 'gamedata', 'excel'),
        unicode_map,
    )
    wording.update(set([chr(x) for x in range(33, 127)]))
    output_dir = os.path.join(args.output_dir, client)
    os.makedirs(output_dir, exist_ok=True)

    all_context = '\n'.join(wording)
    with open(os.path.join(output_dir, 'wording.txt'), 'w',
              encoding='utf-8') as f:
        f.write(all_context)

    keys = set()
    for k in all_context:
        if ord(k) <= 32:
            continue
        keys.add(k)
    with open(f'raw_keys/{client}.txt', 'r', encoding='utf-8') as f:
        key_text = f.read()
    for k in keys:
        if k not in key_text:
            key_text += k + "\n"
    with open(os.path.join(output_dir, 'keys.txt'), 'w',
              encoding='utf-8') as f:
        f.write(key_text)

    short_context = '\n'.join([w for w in wording if len(w) < 7])
    short_output_dir = os.path.join(output_dir, 'short')
    os.makedirs(short_output_dir, exist_ok=True)
    with open(os.path.join(short_output_dir, 'short_wording.txt'),
              'w',
              encoding='utf-8') as f:
        f.write(short_context)

    long_context = '\n'.join([w for w in wording if len(w) >= 7])
    long_output_dir = os.path.join(output_dir, 'long')
    os.makedirs(long_output_dir, exist_ok=True)
    with open(os.path.join(long_output_dir, 'long_wording.txt'),
              'w',
              encoding='utf-8') as f:
        f.write(long_context)


if __name__ == "__main__":
    args = parse_args()
    main(args)
