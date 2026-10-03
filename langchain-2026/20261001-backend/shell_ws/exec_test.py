#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在命令行使用 ASCII Art 打印佛祖形象。

用法示例:
    python exec_test.py
    python exec_test.py -m "代码无BUG"
    python exec_test.py --plain
"""

import argparse

# 佛祖 ASCII Art（原始字符串，避免反斜杠被转义）
BUDDHA_ART = r"""
                        _ooOoo_
                       o8888888o
                       88" . "88
                       (| -_- |)
                       O\  =  /O
                    ____/`---'\____
                  .'  \\|     |//  `.
                 /  \\|||  :  |||//  \
                /  _||||| -:- |||||-  \
                |   | \\\  -  /// |   |
                | \_|  ''\---/''  |_/ |
                \  .-\__  `-`  ___/-. /
              ___`. .'  /--.--\  `. .'___
           ."" '<  `.___\_<|>_/___.' >' "".
          | | :  `- \`.;`\ _ /`;.`/ - ` : | |
          \  \ `-.   \_ __\ /__ _/   .-` /  /
     ======`-.____`-.___\_____/___.-`____.-'======
                        `=---='
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
"""

# 默认的祈福文字
DEFAULT_BLESSING = "佛祖保佑       永无BUG"

# 每条横幅的宽度，用于居中祈福文字
_WIDTH = 51


def render(blessing=DEFAULT_BLESSING, plain=False):
    """返回完整的 ASCII Art 字符串。

    :param blessing: 佛祖下方的祈福文字
    :param plain: 为 True 时输出纯文本（不居中对齐祈福文字）
    """
    art = BUDDHA_ART.strip("\n")
    if plain:
        return art + "\n" + blessing
    return art + "\n" + blessing.center(_WIDTH)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="命令行 ASCII Art 打印佛祖形象",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-m",
        "--message",
        default=DEFAULT_BLESSING,
        help="佛祖下方的祈福文字（默认: %(default)s）",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="不居中祈福文字，直接原样输出",
    )
    args = parser.parse_args(argv)

    print(render(args.message, plain=args.plain))


if __name__ == "__main__":
    main()
