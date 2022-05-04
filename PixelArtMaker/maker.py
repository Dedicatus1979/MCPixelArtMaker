# -*- coding:utf-8 -*-
# @Time : 2022/4/28 上午 11:18
# @Author : Dedicatus1979
# @File : maker.py
# @Software : PyCharm

"""
这个文件，也就是Maker类是这个像素画生成器内外交互的一个最主要的类，一般来说需要生成像素画只需要使用这个类中的transformation()方法即可，
当然在使用的时候得先指定文件的输入输出路径。"""

from pathlib import Path
from typing import Union

from .picture import Picture
from .structure import Structure

"""
简易实现原理：
    Maker类会创建文件输入输出的路径，一个空的所需转换的文件列表（类似于缓存？）
    使用transformation方法时，解释器会进行以下运行步骤：
        解释器检测是当前模式是否为批量模式
        解释器尝试寻找所输入的文件(夹)。
        解释器将找到的所以文件路径存入文件缓存列表中。
        解释器创建一个Structure的实例与Picture的实例。
        解释器将图片中的列表通过picture内的方法转换成所需要的文件。
        解释器将上一步中的文件一个一个的通过structure内的方法转换为nbt文件。
        解释器将这些nbt文件输出至指定文件夹。"""


class Maker:
    version: Union[float, str]
    direction: str
    color_space: str
    batch: bool

    def __init__(self):
        self.__size = None  # 生成的结构大小
        self.__file_path = None  # 输入文件地址
        self.__out_path = None  # 输出文件地址
        self.__file_cache = []  # 所需要生成结构的文件
        self.__using_blocks = ['wool']  # 生成的像素画所使用的方块
        self.__allow_blocks = ("wool", "concrete", "terracotta")  # 像素画生成器允许使用的方块
        self.__allow_setting = ("version", "direction", "color_space", "batch")  # 生成器允许在外部设置中直接设置的参数名
        self.__allow_color_space = ("RGB", "HSV", "HSL", "L")  # 生成器允许的颜色空间
        self.version = 1.18  # 生成的结构的版本
        self.direction = 'ns'  # 生成的像素画的方向
        self.color_space = 'RGB'  # 生成的像素画的色彩空间
        self.batch = False  # 是否批量生成像素画

    def __update_files(self):
        """用于更新输入文件路径里的所有jpg、jpeg与png格式的图片"""
        if self.batch:
            self.reset_file_cache()
            for files in self.__file_path.iterdir():
                if files.suffix in [".png", ".jpg", ".jpeg"]:
                    self.__file_cache.append(files)

    def __update_out_path(self):
        """用于更新输出文件路径"""
        if not self.__out_path or self.__file_path == self.__out_path:
            if not (self.__file_path / "file_out").exists():
                (self.__file_path / "file_out").mkdir()
            self.__out_path = self.__file_path / "file_out"

    def __check_file_path(self, path: Union[Path, str]):
        """检测文件path是否存在，若存在，则返回True，不存在则报错"""
        if not path:
            raise OSError("OSError:\n\t未指定输入文件路径。")
        elif not Path(path).exists():
            raise OSError(f"OSError:\n\t路径'{path}'并不存在。")
        else:
            return True

    def __prevent_cover(self, out_path: Union[Path, str], file_stem: str, file_suffix: str) -> Path:
        """防止文件被覆写的方法，输入需要写的文件的绝对路径，输出文件的绝对路径，如果会覆写文件的话，会在文件后加数字。
        例如需要保存pic_1.png，但这个文件已经存在，则文件会被保存为pic_1_1.png，若pic_1_1.png同样存在，则会保存为pic_1_2.png
        file_stem指文件名pic_1，file_suffix指文件后缀.png"""
        i = 1
        temp_name = file_stem
        while True:
            if (out_path / (temp_name + file_suffix)).exists():
                temp_name = file_stem + f"_{i}"
                i += 1
            else:
                break
        return out_path / (temp_name + file_suffix)

    def get_size(self):
        """用于获取输出的结构大小"""
        return self.__size

    def get_allow_blocks(self):
        """用于获取允许使用的方块"""
        return list(self.__allow_blocks)

    def get_allow_setting(self):
        """用于获取可以在外部直接修改的参数名"""
        return list(self.__allow_setting)

    def get_allow_color_space(self):
        """用于获取支持的颜色空间"""
        return list(self.__allow_color_space)

    def reset_file_cache(self):
        """将结构缓存复位为空"""
        self.__file_cache = []

    def reset_batch(self):
        """将self.batch置为False，即关闭批量模式"""
        self.batch = False

    def set_version(self, version: Union[float, str]):
        """本方法用于设置输出的结构的版本，支持输入浮点数float或字符串str，输入格式为类似于'1.16'这样的游戏大版本号。
        不支持输入类似于'1.18.2'这样的具体版本号，不建议版本号小于1.12。"""
        try:
            self.version = float(version)
        except ValueError:
            raise NameError(f"'NameError:\n\t'{version}'似乎不是一个MC的大版本，请输入类似于'1.16'这样的版本号。'")

    def set_direction(self, direction: str):
        """本方法用于设置像素画的方向，仅仅支持两种方法，一种是从北向南的方向，即ns；还有一种是从上至下的方向，即ud。
        默认为ns方向，所以本方法的参数direction接受的实参只有'ud'与'ns'。"""
        if direction.lower() in ["ud", "ns"]:
            self.direction = direction.lower()
        else:
            raise NameError(f"NameError:\n\t未定义的方向'{direction}'。")

    def set_color_space(self, color_space: str):
        """用于设置颜色的色彩空间，可以设置RGB, HSV, HSL或L，默认使用RGB"""
        if color_space.upper() in self.__allow_color_space:
            self.color_space = color_space.upper()
        else:
            raise NameError(f"NameError:\n\t未定义的色彩空间'{color_space}'。")

    def set_batch(self, status: Union[bool, str] = True):
        """将self.batch置为status，默认为True，即开启批量模式"""
        if isinstance(status, bool):
            self.batch = status
        elif status.lower() == "false":
            self.batch = False
        else:
            self.batch = True

    def set_using_blocks(self, using_blocks: Union[str, list, tuple]):
        """本方法用于设置像素画的使用方块，方块使用字符串关键词，'wool'表示使用羊毛，'terracotta'表示陶瓦，
        'concrete'表示混凝土。默认使用'wool'。可以以列表形式传入多个方块也可以输入关键词'all'表示使用3种方块。"""
        if isinstance(using_blocks, str):
            if ("[" in using_blocks and "]" in using_blocks) or ("(" in using_blocks and ")" in using_blocks):
                using_blocks = eval(using_blocks)
            else:
                using_blocks = [using_blocks]
        for block in using_blocks:
            if block == '':
                return None
            elif block.lower() == 'all':
                self.__using_blocks = self.__allow_blocks
                return None
            elif block.lower() not in self.__allow_blocks:
                raise NameError(f"NameError:\n\t未定义的方块空间'{block}'。")
        self.__using_blocks = using_blocks

    def set_size(self, struct_size: Union[tuple[int, int], list[int, int]]):
        """本方法用于设置所需要生成的结构的大小，接受元组或列表，元组与列表里应该是两个元素作为所需要的长与宽。
        本参数没有默认值，必须需要设置！！！"""
        if isinstance(struct_size, (tuple, list)):
            self.__size = struct_size
        else:
            raise TypeError(f"TypeError:\n\t结构大小仅接受tuple或list类型的参数。'{struct_size}'不是所能接受的参数。")

    def set_path(self, path: Union[str, Path], path_type: str = "in"):
        """本方法用于设置文件输入输出的绝对路径，输入类型为str。当path_type = 'in'时，表示设置的是输入路径，
        当path_type = 'out'时，表示设置的是输出路径。输入错误或默认时为设置输入路径。"""
        self.__check_file_path(path)
        if path_type == "out":
            self.__out_path = Path(path)
        else:
            self.__file_path = Path(path)

    def set_transformation_file(self, trans_file_name: str):
        """本方法原则上只在非批量生成的情况下才可使用，用于设置需要转换的文件名。
        本方法只需要设置文件名就行，例如：'badapple_1.png'，不需要设置路径，但需要保证文件在输入文件的路径下。"""
        if not trans_file_name or self.batch:
            pass
        elif self.__check_file_path(self.__file_path / trans_file_name):
            self.__file_cache.append(self.__file_path / trans_file_name)

    def settings(self, setting_dict: dict):
        """用于在外部使用字典来设置Maker内的部分参数"""
        for key, value in setting_dict.items():
            if key not in self.__allow_setting:
                raise NameError(f"NameError:\n\t参数'{key}'无法被设置，可能是因为不存在，也可能是不允许设置这个参数。")
            else:
                eval(f'self.set_{key}("{value}")')

    def transformation(self, import_file: str = None):
        """用于转换文件的方法函数，基本只需要用这个函数就可以运行本程序了。
        参数file是用于方便单个文件的转换，不过如果batch是True的情况下并没有什么意义就是了。"""
        self.__check_file_path(self.__file_path)
        self.set_transformation_file(import_file)
        self.__update_files()
        self.__update_out_path()
        struct = Structure(self.version, self.direction, self.__size, self.__using_blocks, self.color_space)
        i = 0
        while i < len(self.__file_cache):
            pict = Picture(self.__file_cache[i])
            pict.picture_resize(self.__size)
            pict.picture_to_L() if self.color_space.upper() == "L" else pict.picture_to_rgb()
            pict_arr = pict.get_ndarray_picture()
            # pict_img = pict.get_image_picture()
            # pict_img.save(self.__out_path / (self.__files[i].split(".")[0] + ".png"))
            out_struct = struct.mk_struct(pict_arr, i, len(self.__file_cache))
            out_struct.write_file(self.__prevent_cover(self.__out_path, self.__file_cache[i].stem, ".nbt"))
            i += 1
        self.reset_file_cache()
