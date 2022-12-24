from glob import glob
import os
from pathlib import Path
import argparse as A


def extract_labels_from_txt(txt_file: Path) -> list:
    parent = txt_file.parent
    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        prefix = parent.as_posix()
        if not prefix.endswith('/'):
            prefix += '/'

        lines = [f"{prefix}{line[:8]}.jpg\t{line[9:]}" for line in lines]
        return lines


def extract_labels_from_filenames(data_dir: Path) -> list:
    if not data_dir.exists() or not data_dir.is_dir():
        return []
    all_imgs = [
        *list(data_dir.rglob("**/*.png")),
        *list(data_dir.rglob("**/*.jpg")),
        *list(data_dir.rglob("**/*.jpeg")),
        *list(data_dir.rglob("**/*.bmp")),
    ]
    res = [f"{Path(img).as_posix()}\t{Path(img).stem}\n" for img in all_imgs]
    return res


def main(args):
    data_root: Path = args.data_root / args.lang
    output_dir: Path = args.output_dir / args.lang
    train_mappings = glob(str(data_root / '**' / 'train.txt'), recursive=True)
    test_mappings = glob(str(data_root / '**' / 'test.txt'), recursive=True)
    train_lines = []
    test_lines = []

    for mapping in train_mappings:
        train_lines += extract_labels_from_txt(Path(mapping))

    for mapping in test_mappings:
        test_lines += extract_labels_from_txt(Path(mapping))

    if args.extra_data:
        train_lines += extract_labels_from_filenames(args.extra_data /
                                                     args.lang / 'train')
        test_lines += extract_labels_from_filenames(args.extra_data /
                                                    args.lang / 'test')

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / 'rec_gt_train.txt', 'w', encoding='utf-8') as f:
        f.writelines(train_lines)

    with open(output_dir / 'rec_gt_test.txt', 'w', encoding='utf-8') as f:
        f.writelines(test_lines)


def parse_args():
    parser = A.ArgumentParser()
    parser.add_argument(
        "--data_root",
        "-d",
        type=Path,
        default=Path(os.path.join('.', 'output', 'render')),
        help="Path to the root of the data",
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        type=Path,
        default=Path(os.path.join(".", "output")),
        help="Path to the output directory",
    )
    parser.add_argument(
        "--extra_data",
        "-e",
        type=Path,
        default="my_data",
        help="Path to the extra data",
    )
    parser.add_argument(
        "--lang",
        "-l",
        type=str,
        choices=["zh_CN", "en_US", "ja_JP", "ko_KR", "zh_TW"],
        default="zh_CN",
        help="Language of the data",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)