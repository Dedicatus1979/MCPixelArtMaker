# -*- coding:utf-8 -*-
# @Time : 2022/5/4 下午 3:11
# @Author : Dedicatus1979
# @File : __main__.py
# @Software : PyCharm

"""这是这个模块的主文件？这个文件没什么用，不要瞎导入这个文件！！！"""

import sys
# from os import system
from pathlib import Path

from .maker import Maker
from . import __version__


def path_test(import_path):
    """用于判定输入路径是否为空，若为空则返回当前文件所在路径"""
    if not import_path:
        return Path(sys.argv[0]).parent
    else:
        return Path(import_path)


def main():
    """主函数，应该没什么好过多说明的吧"""
    maker = Maker()
    print(f"-------MCPixelArtMaker V{__version__}-------@Dedicatus1979-------感谢@御坂10703的耐心指导-------")
    print("更多使用方式可以可前往'https://github.com/Dedicatu1979/MCPixelArtMaker'中了解更多。")
    print("------以下是一些全局设置：------")
    path_in = input("请输入需要转换的图片所在的文件夹的路径。(仅需要输入文件夹的路径即可，跳过则以当前文件所在文件夹的路径作为输入)\n")
    maker.set_path(path_test(path_in))
    print(f"您当前输入的路径为:{path_in}") if path_in != '' else print("当前使用默认路径。")
    print("--*--*--#--*--*--")
    path_out = input("请输入转换后的文件保存的文件夹的路径。(仅需要输入文件夹的路径即可，跳过则文件保存至输入文件夹所在的路径下的\\file_out)\n")
    maker.set_path(path_test(path_out), "out")
    print(f"您当前输入的路径为:{path_out}") if path_out != '' else print("当前使用默认路径。")
    print("--*--*--#--*--*--")
    using_block = input(f'请输入结构所使用的方块，限在{maker.get_allow_blocks()}中任选1-3个。默认使用wool.\n'
                        '如需多选请使用("圆括号","加引号")或["中括号","加引号"](元组或列表的形式)输入。\n'
                        '例如直接输入wool或输入["wool", "concrete"]，全部使用的话也可直接输入all。\n')
    maker.set_using_blocks(using_block)
    print(f"您当前输入的方块为:{using_block}") if using_block != '' else print("当前使用默认方块。")
    print("--*--*--#--*--*--")
    others = input("是否还有其他需要设置的，如有需要设置的话请以{'大括号': '冒号引号','的方式': '继续进行设置'}(字典形式)输入：\n"
                   f"{maker.get_allow_setting()} 以上是允许继续设置的参数，如不需要的话可以直接跳过。\n")
    if others == '':
        pass
    elif isinstance(eval(others), dict):
        maker.settings(eval(others))
    else:
        raise SyntaxError("SyntaxError:\n\t设置的格式有误，无法进行设置。")
    print("--*--*--*--*--*--*--*--")
    while True:
        if not (maker.batch and maker.get_size()):
            size = input("请输入所需要的结构的大小，格式为元组或列表的形式，例如(96, 72).\n")
            if size == '':
                raise ValueError("ValueError:\n\t结构大小没有默认值。请输入需要的结构大小。")
            else:
                maker.set_size(eval(size))
            print(f"您所设置的结构大小为{size}")
            print("--*--*--#--*--*--")
        if not maker.batch:
            file = input("请输入需要转换的图片名称。(仅需要输入文件名即可，例如lenna.png).\n")
            maker.set_transformation_file(file)
            print(f"您所设置的文件为{file}")
            print("--*--*--#--*--*--")
        maker.transformation()
        if not maker.batch:
            out = input("\n运行已结束，请问还需要继续转换结构吗？输入任意值继续，输入q退出。")
            if out == 'q':
                break
        else:
            print("\n-------运行结束。-------\n")
            break


# if __name__ == '__main__':
try:
    main()
except Exception as result:
    print("\n\n", result, "\n\n")
# finally:
#     if Path(__file__).parent != Path(sys.argv[0]).parent:
#         system("pause")
