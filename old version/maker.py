# -*- coding:utf-8 -*-
# @Time : 2022/4/28 上午 11:18
# @Author : Dedicatus1979
# @File : maker.py
# @Software : PyCharm

import os
import sys
from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image
from nbt import nbt
from tqdm import trange

"""
2022.4.29 已经将颜色的计算，即计算与输入颜色向量最为接近的颜色向量修改完了。即已经兼容最大四种方块了。
    还需要修改结构的生成器，这个还没修改，需要修改成支持多组方块的形式。
2022.4.30 大致已经把想实现的功能给写完了，但还有东西需要修改，需要修改的东西是灰度模式，我打算灰度模式改成用四种颜色的方块。
    还有就是要修改程序结构，这个文件写的太乱了。。。
    之后想的首先是要把这个文件给打包，打包完后gui懒得设计了，就用cmd交互吧。。。
2022.5.1 主要的部分基本已经写完了，明天开始就修修补补改改代码写法吧。明天把下面这些给改掉
    把色彩空间color_space与色彩模式color_mode合并成一个色彩空间color_space吧，毕竟灰度也可看作是一种色彩空间，
    color_block，using_block之类的东西，凡是表达使用的方块颜色之类的意思的变量通通改为using_blocks，
    把游戏版本通通统一成version，我记得里面好像version与edition一直有混用来着。
2022.5.2 把除了maker类外的类基本都看了一遍，把一些不需要的函数之类的通通去掉了，明天把maker类跟主函数内的内容再仔细看看吧。
    应该这些地方还有很多可以去掉的语句之类的。"""

wool_RGB = np.array([[234, 241, 191, 56, 249, 113, 238, 61, 143, 13, 123, 50, 115, 84, 162, 13],
                     [237, 119, 67, 176, 199, 186, 142, 67, 143, 139, 38, 55, 70, 110, 35, 13],
                     [237, 13, 181, 218, 35, 18, 173, 70, 136, 146, 174, 158, 36, 21, 29, 19]])
wool_HSV = np.array([[-2, 106, 47, -91, 76, 8, 48, -15, 3, -116, 13, -47, 79, 22, 104, -20],
                     [0, 56, -68, -25, 78, 114, -17, -6, 5, -6, -98, -73, 38, 100, 5, -35],
                     [237, 241, 191, 218, 249, 186, 238, 70, 143, 146, 174, 158, 115, 110, 162, 19]])
wool_HSL = np.array([[-10, 101, 36, -84, 84, 7, 88, -8, 2, -106, 11, -36, 60, 19, 88, -12],
                     [0, 53, -51, -23, 86, 104, -31, -3, 3, -6, -81, -55, 29, 84, 4, -21],
                     [236, 127, 129, 137, 142, 102, 190, 66, 140, 80, 106, 104, 76, 66, 96, 16]])
wool_L = np.array([236, 65, 142, 14])  # 羊毛的rgb,hsv,hsl与灰度

terracotta_RGB = np.array([[208, 160, 148, 111, 184, 100, 160, 52, 133, 83, 116, 70, 73, 72, 141, 28],
                           [176, 80, 85, 105, 131, 115, 74, 34, 104, 88, 65, 55, 45, 79, 56, 11],
                           [159, 29, 106, 136, 26, 46, 75, 26, 94, 88, 82, 88, 27, 34, 40, 4]])
terracotta_HSV = np.array([[28, 95, 51, -9, 84, 22, 68, 60, 36, -7, 52, -2, 73, 26, 90, 104],
                           [11, 41, -18, -27, 70, 73, -1, 20, 10, 0, -19, -48, 32, 68, 15, 33],
                           [208, 160, 148, 136, 184, 115, 160, 52, 133, 88, 116, 88, 73, 79, 141, 28]])
terracotta_HSL = np.array([[41, 81, 32, -5, 73, 16, 47, 40, 21, -4, 34, -1, 54, 18, 70, 91],
                           [15, 35, -12, -16, 61, 52, -1, 13, 6, 0, -12, -29, 23, 47, 12, 29],
                           [184, 94, 117, 120, 105, 80, 117, 39, 114, 86, 90, 72, 50, 56, 90, 16]])
terracotta_L = np.array([184, 39, 112, 15])  # 陶瓦

concrete_RGB = np.array([[208, 225, 170, 31, 242, 94, 215, 52, 126, 14, 100, 41, 96, 72, 143, 1],
                         [214, 97, 45, 138, 176, 170, 101, 56, 126, 120, 26, 43, 58, 91, 27, 2],
                         [215, 0, 160, 200, 14, 17, 144, 60, 116, 137, 157, 144, 26, 31, 27, 6]])
concrete_HSV = np.array([[-4, 114, 53, -99, 88, 0, 62, -15, 5, -113, 7, -47, 82, 16, 103, -71],
                         [-1, 55, -77, -40, 81, 114, -26, -8, 9, -16, -106, -78, 43, 82, 0, -79],
                         [215, 225, 170, 200, 242, 170, 215, 60, 126, 137, 157, 144, 96, 91, 143, 6]])
concrete_HSL = np.array([[-10, 114, 42, -86, 84, 0, 69, -8, 3, -102, 6, -37, 65, 12, 87, -61],
                         [-2, 55, -61, -35, 77, 104, -29, -5, 5, -15, -91, -61, 34, 61, 0, -67],
                         [211, 112, 108, 116, 128, 94, 158, 56, 121, 76, 92, 92, 61, 61, 85, 4]])
concrete_L = np.array([212, 55, 125, 2])  # 混凝土


def rgb2h(rgb) -> tuple:
    """输入rgb列表，输出hsv或hsl的h值(rad)与rgb中的最大，最小值"""
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    max_value = max(r, g, b)
    min_value = min(r, g, b)
    if max_value == min_value:
        h = 0
    elif max_value == r:
        if g >= b:
            h = 60 * (g - b) / (max_value - min_value)
        else:
            h = 60 * (g - b) / (max_value - min_value) + 360
    elif max_value == g:
        h = 60 * (b - r) / (max_value - min_value) + 120
    else:  # max_value == b
        h = 60 * (r - g) / (max_value - min_value) + 240
    h_rad = np.deg2rad(h)
    return h_rad, max_value, min_value


def rgb2hsv_standardization(rgb) -> np.ndarray:
    """输入rgb列表，输出笛卡尔坐标化的hsv值，本项目中的hsv值是坐标化的，而不是原始的hsv值。"""
    h_rad, max_value, min_value = rgb2h(rgb)
    if max_value == 0:
        s = 0
    else:
        s = 1 - min_value / max_value
    s = s * 127
    return np.array((round(np.cos(h_rad) * s), round(np.sin(h_rad) * s), round(max_value * 255)))


def rgb2hsl_standardization(rgb) -> np.ndarray:
    """输入rgb列表，输出笛卡尔坐标化的hsl值，本项目中的hsl值是坐标化的，而不是原始的hsl值。"""
    h_rad, max_value, min_value = rgb2h(rgb)
    l = (max_value + min_value) / 2
    if max_value == min_value or l == 0:
        s = 0
    elif 0 < l <= 0.5:
        s = (max_value - min_value) / (2 * l)
    else:  # l > 0.5
        s = (max_value - min_value) / (2 - 2 * l)
    s = s * 127
    return np.array((round(np.cos(h_rad) * s), round(np.sin(h_rad) * s), round(l * 255)))


class Color:
    def __init__(self, color_space: str, using_blocks: Union[list, tuple]):
        self.color_space = color_space
        self.block = using_blocks
        self.temp_color_array = self.__initialization_array()

    def __initialization_array(self) -> np.ndarray:
        """这个初始化函数，用于创建一个临时的数组矩阵，这个数组矩阵即为所需要的颜色向量所组成的矩阵。类似于将多个分块矩阵合成一个大矩阵。
        例如我需要向量矩阵A[[255, 0, 255], [0, 255, 0]]T与向量矩阵B[[255, 0, 0], [0, 0, 255]]T，则这个函数会将这两个矩阵合起来，即
        输出向量矩阵AB[[255, 0, 255], [0, 255, 0], [255, 0, 0], [0, 0, 255]]T"""
        temp = eval(f"{self.block[0]}_{self.color_space}")
        for i in range(len(self.block) - 1):
            temp = np.hstack((temp, eval(f"{self.block[i + 1]}_{self.color_space}")))
        return temp

    def __color_space_change(self, color: np.ndarray, color_space: str) -> np.ndarray:
        """这个函数是用于将输入的颜色给转换成特定的格式，例如将输入的rgb转换为hsv并输出。"""
        if color_space == "L":
            return color
        else:
            color.resize((3,))
            if self.color_space == 'HSV':
                color = rgb2hsv_standardization(color)
            elif self.color_space == 'HSL':
                color = rgb2hsl_standardization(color)
            color.resize((3, 1))
            return color

    def similar_color(self, color: np.ndarray, color_space: str) -> int:
        """将颜色向量输入，输出与这个颜色最为接近的颜色的下标。
        例如输入的颜色是(192, 168, 1)T,则计算得出与其最接近的羊毛颜色是(241, 119, 13)T，
        也就是橘色，其下标是1，则输出值就是1。"""
        color_n = self.__color_space_change(color, color_space)
        difference = color_n - self.temp_color_array
        squ_difference = np.square(difference)
        if color_space == "L":
            the_column_sum = squ_difference
        else:
            the_column_sum = np.sum(squ_difference, axis=0)
        the_min_num = np.argmin(the_column_sum)
        return int(the_min_num)


class Structure:
    def __init__(self, version: float, direction: str, struct_size: Union[tuple[int, int], list[int, int]],
                 using_blocks: Union[list, tuple], color_space: str):
        """定义结构，需要输入结构的大小，结构大小为1*2的元组，为图片的长与宽。游戏版本，仅仅支持1.12与1.18。
        游戏中的观看方向，两种模式，南北'ns'与上下'ud'，其他的内容不接受"""
        self.size = struct_size
        self.block = using_blocks
        self.color_space = self.__check_color_space(color_space)
        self.version = self.__check_version(version)
        self.direction = self.__check_direction(direction)
        self.color = Color(self.color_space, self.block)

        self.block_dict = {"wool": "wool", "concrete": "concrete",
                           "terracotta": "stained_hardened_clay" if self.version <= 1.12 else "terracotta"}
        self.color_dict = {0: "white", 1: "orange", 2: "magenta", 3: "light_blue", 4: "yellow", 5: "lime", 6: "pink",
                           7: "gray", 8: "silver" if self.version <= 1.12 else "light_gray", 9: "cyan", 10: "purple",
                           11: "blue", 12: "brown", 13: "green", 14: "red", 15: "black"}

    def __check_version(self, version):
        """用于检测version是否是程序接受的类型"""
        try:
            return float(version)
        except ValueError:
            raise Exception(f"'Error:\n\t'{version}'似乎不是一个MC的大版本，请输入类似于'1.16'这样的版本号。'")

    def __check_direction(self, direction):
        """用于检测direction是否是程序接受的类型"""
        if direction.lower() in ["ud", "ns"]:
            return direction.lower()
        else:
            raise Exception(f"Error:\n\t未定义的方向'{direction}'。")

    def __check_color_space(self, color_space):
        """用于检测color_space是否是符合的类型"""
        if color_space.upper() in ("RGB", "HSV", "HSL", "L"):
            return color_space.upper()
        else:
            raise Exception(f"Error:\n\t未定义的色彩空间'{color_space}'。")

    def mk_struct(self, picture: np.ndarray, times=0, all_time=1) -> nbt.NBTFile:
        """将图片转换为nbt文件，图片输入为ndarray格式，返回的就是所转换的nbt文件
        话说下面这段东西也算是祖传代码了，从我第一次试验成功后就没怎么动过，只敢修修补补。
        现在都过去快一年了，我自己都快看不懂了。。。"""

        picture = picture[::-1, ::-1]  # 给图片转180°

        struction = nbt.NBTFile()
        struction.name = ""
        # 添加需要的大小
        my_size = nbt.TAG_List(name="size", type=nbt.TAG_Int)
        if self.direction == "ns":
            my_size.tags.extend([nbt.TAG_Int(self.size[0]), nbt.TAG_Int(self.size[1]), nbt.TAG_Int(1)])
        else:
            my_size.tags.extend([nbt.TAG_Int(self.size[0]), nbt.TAG_Int(1), nbt.TAG_Int(self.size[1])])
        struction.tags.append(my_size)
        # struction.tags.append(nbt.TAG_List(name="entities", type=nbt._TAG_End))        # 这个我真不知道是啥了，而且这个文件不是必要的，可以注释掉
        # 添加方块与方块的颜色
        my_blocks = nbt.TAG_List(name="blocks", type=nbt.TAG_Compound)
        t = trange(self.size[1], postfix={"Now file": times + 1, "Total": all_time})
        t.set_description("少女祈祷中...")
        for i in t:
            for j in range(self.size[0]):
                first = nbt.TAG_Compound(name='')
                pos = nbt.TAG_List(name="pos", type=nbt.TAG_Int)
                if self.direction == "ns":
                    pos.tags.extend([nbt.TAG_Int(j), nbt.TAG_Int(i), nbt.TAG_Int(0)])
                else:
                    pos.tags.extend([nbt.TAG_Int(j), nbt.TAG_Int(0), nbt.TAG_Int(i)])
                first.tags.append(pos)

                if self.color_space != "L":
                    block_num = self.color.similar_color(picture[i, j, :], self.color_space)
                    state = nbt.TAG_Int(name="state", value=block_num)
                else:
                    block_num = self.color.similar_color(picture[i, j], self.color_space)
                    temp_num = block_num % 4
                    temp_time = block_num // 4
                    num = (2 * temp_num ** 3 - 9 * temp_num ** 2 + 14 * temp_num) + (temp_time * 16)
                    state = nbt.TAG_Int(name="state", value=num)

                first.tags.append(state)
                my_blocks.append(first)
        struction.tags.append(my_blocks)
        # struction.tags.append(nbt.TAG_String(name="author", value="Dedicatus1979"))    # 作者，这个文件不是必要的，可以注释掉
        mypalette = nbt.TAG_List(name="palette", type=nbt.TAG_Compound)
        for i in range(len(self.block) * 16):
            root = nbt.TAG_Compound(name='')
            if self.version <= 1.12:
                properties = nbt.TAG_Compound(name='')
                properties.name = 'Properties'
                color = nbt.TAG_String(name='color', value=self.color_dict[i % 16])
                properties.tags.append(color)
                root.tags.append(properties)
                name_ = nbt.TAG_String(name='Name', value=("minecraft:" + self.block_dict[self.block[i // 16]]))

            else:
                name_ = nbt.TAG_String(name='Name', value=(
                            "minecraft:" + self.color_dict[i % 16] + "_" + self.block_dict[self.block[i // 16]]))
            root.tags.append(name_)
            mypalette.append(root)
        struction.tags.append(mypalette)
        # struction.tags.append(nbt.TAG_Int(name="DataVersion", value=2230))       # 版本，这个文件不是必要的，可以注释掉
        # print(struction.pretty_tree())
        # struction.write_file(out_path + '\\' + out_name)
        return struction


class Picture:
    def __init__(self, picture_file: Union[Path, str]):
        self.__picture_path = picture_file
        self.__picture = Image.open(picture_file)

    def get_image_picture(self) -> Image:
        """将self.picture返回Image的图片"""
        return self.__picture

    def get_ndarray_picture(self) -> np.ndarray:
        """将self.picture给ndarray化并返回ndarray化的图片"""
        return np.array(self.__picture)

    def picture_to_rgb(self):
        """将图片转换为rgb模式
        本方法需要Image的图片"""
        if self.__picture.mode == "RGBA":
            r, g, b, a = self.__picture.split()
            self.__picture = Image.merge('RGB', (r, g, b))
        elif self.__picture.mode == "RGB":
            pass
        else:
            raise Exception(f"Error:\n\t输入图片'{self.__picture_path}'的颜色空间超出了预期，请保证颜色为'RGBA'或'RGB'")

    def picture_to_L(self):
        """将图片转换为灰度模式
        本方法需要Image的图片"""
        self.picture_to_rgb()
        self.__picture = self.__picture.convert('L')

    def picture_resize(self, struct_size: Union[tuple[int, int], list[int, int]]):
        """转变图片的大小，也就是转换成所需要的结构的大小
        本方法需要Image的图片"""
        self.__picture = self.__picture.resize(struct_size)


class Maker:
    version: Union[float, str]
    direction: str
    color_space: str
    batch: bool

    def __init__(self):
        self.__size = None  # 生成的结构大小
        self.__file = []  # 所需要生成结构的文件
        self.__using_blocks = ['wool']  # 生成的像素画所使用的方块
        self.__file_path = self.__initialization_path()  # 输入文件地址
        self.__out_path = self.__initialization_path()  # 输出文件地址
        self.__allow_blocks = ("wool", "concrete", "terracotta")  # 像素画生成器允许使用的方块
        self.__allow_setting = ("version", "direction", "color_space", "batch")  # 生成器允许在外部设置中直接设置的参数名
        self.__allow_color_space = ("RGB", "HSV", "HSL", "L")       # 生成器允许的颜色空间
        self.version = 1.18  # 生成的结构的版本
        self.direction = 'ns'  # 生成的像素画的方向
        self.color_space = 'RGB'  # 生成的像素画的色彩空间
        self.batch = False  # 是否批量生成像素画

    def __initialization_path(self):
        """用于初始化文件的输入输出路径，如果文件是直接运行的情况下，会默认将当前文件所在的路径作为输入路径"""
        if __name__ == '__main__':
            # return Path(__file__).parent
            return Path(sys.argv[0]).parent
        else:
            return None

    def __update_files(self):
        """用于更新输入文件路径里的所有jpg、jpeg与png格式的图片"""
        if self.batch:
            for files in self.__file_path.iterdir():
                if files.suffix in [".png", ".jpg", ".jpeg"]:
                    self.__file.append(files)

    def __update_out_path(self):
        """用于更新输出文件路径"""
        if self.__out_path in [self.__file_path, None]:
            if not (self.__file_path / "file_out").exists():
                (self.__file_path / "file_out").mkdir()
            self.__out_path = self.__file_path / "file_out"

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

    def set_version(self, version: Union[float, str]):
        """本方法用于设置输出的结构的版本，仅仅支持1.12版本与非1.12版本，默认非1.12版本。
        所以参数version其实只由以1.12作为实参才有意义。。只要不是1.12就默认1.18"""
        self.version = version

    def set_direction(self, direction: str):
        """本方法用于设置像素画的方向，仅仅支持两种方法，一种是从北向南的方向，即ns；还有一种是从上至下的方向，即ud。
        默认为ns方向，所以本方法的参数direction接受的实参只有'ud'与'ns'。"""
        self.direction = direction

    def set_color_space(self, color_space: str):
        """用于设置颜色的色彩空间，可以设置rgb,hsv或L，默认rgb"""
        self.color_space = color_space

    def get_size(self):
        """用于获取结构大小"""
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

    def set_using_blocks(self, using_blocks: Union[str, list, tuple]):
        """本方法用于设置像素画的使用方块，方块使用字符串关键词，'wool'表示使用羊毛，'terracotta'表示陶瓦，
        'concrete'表示混凝土。默认使用'wool'。可以以列表形式传入多个方块，
        可是只有在传入1个2个或3个时是有效的，若超过3个，则会报错。可以输入关键词'all'表示使用3种方块。"""
        if type(using_blocks) in [list, tuple]:
            for block in using_blocks:
                if block not in self.__allow_blocks and block != "all":
                    raise Exception(f"Error:\n\t未定义的方块空间'{block}'。")
                elif len(using_blocks) == 1 and block == "all":
                    using_blocks = self.__allow_blocks
            self.__using_blocks = using_blocks
        elif using_blocks == '':
            pass
        elif type(using_blocks) == str:
            if using_blocks not in self.__allow_blocks and using_blocks != "all":
                raise Exception(f"Error:\n\t未定义的方块空间'{using_blocks}'。")
            elif using_blocks == "all":
                self.__using_blocks = self.__allow_blocks
            else:
                self.__using_blocks = [using_blocks]
        else:
            raise Exception(f"Error:\n\t参数'using_blocks'只接受str,list和tuple。'{using_blocks}'不属于以上任何一类。")

    def set_size(self, struct_size: Union[tuple[int, int], list[int, int]]):
        """本方法用于设置所需要生成的结构的大小，接受元组或列表，元组与列表里应该是两个元素作为所需要的长与宽。
        本参数没有默认值，必须需要设置！！！"""
        if type(struct_size) in [tuple, list]:
            self.__size = struct_size
        else:
            raise Exception(f"Error:\n\t结构大小仅接受tuple或list类型的参数。'{struct_size}'不是所能接受的参数。")

    def set_file_path(self, path: str):
        """本方法用于设置所输入的文件的绝对路径位置，输入类型为str，默认为本文件所在位置"""
        if path == '':
            pass
        else:
            if Path(path).exists():
                self.__file_path = Path(path)
            else:
                raise Exception(f"Error:\n\t路径'{path}'并不存在。")

    def set_out_path(self, path: str):
        """本方法用于设置输出的文件的绝对路径位置，输入类型为str，默认为本文件所在的位置下的file_out文件夹下"""
        if path == '':
            pass
        else:
            if Path(path).exists():
                self.__out_path = Path(path)
            else:
                raise Exception(f"Error:\n\t路径'{path}'并不存在。")

    def set_transformation_file(self, trans_file_name: str):
        """本方法仅仅在非批量生成的情况下才可使用，用于设置需要转换的文件名。
        本方法只需要设置文件名就行，例如：'badapple_1.png'，不需要设置路径，但需要保证文件在输入文件的路径下。"""
        if not trans_file_name:
            pass
        elif not self.__file_path:
            raise Exception("Error:\n\t未指定输入文件路径。")
        elif (self.__file_path / trans_file_name).exists():
            self.__file.append(self.__file_path / trans_file_name)
        else:
            raise Exception(f"Error:\n\t文件'{trans_file_name}'不存在。")

    def transformation(self, import_file: str = None):
        """用于转换文件的方法函数，基本只需要用这个函数就可以运行本程序了。
        参数file是用于方便单个文件的转换，不过如果batch是True的情况下并没有什么意义就是了。"""
        self.set_transformation_file(import_file)
        self.__update_files()
        self.__update_out_path()
        struct = Structure(self.version, self.direction, self.__size, self.__using_blocks,
                           self.color_space)
        i = 0
        while i < len(self.__file):
            pict = Picture(self.__file[i])
            pict.picture_resize(self.__size)
            pict.picture_to_L() if self.color_space.upper() == "L" else pict.picture_to_rgb()
            pict_arr = pict.get_ndarray_picture()
            # pict_img = pict.get_image_picture()
            # pict_img.save(self.__out_path / (self.__file[i].split(".")[0] + ".png"))
            out_struct = struct.mk_struct(pict_arr, i, len(self.__file))

            out_struct.write_file(self.__prevent_cover(self.__out_path, self.__file[i].stem, ".nbt"))
            i += 1


if __name__ == '__main__':
    try:
        maker = Maker()
        print("-------MCPixelArtMaker V1.0.0-------@Dedicatus1979-------感谢@御坂10703的耐心指导-------")
        print("更多使用方式可以可前往'https://github.com/Dedicatu1979/MCPixelArtMaker'中了解更多。")
        print("------以下是一些全局设置：------")
        path_in = input("请输入需要转换的图片所在的文件夹的路径。(仅需要输入文件夹的路径即可，跳过则以当前文件所在文件夹的路径作为输入)\n")
        maker.set_file_path(path_in)
        print("您当前输入的路径为:{}".format(path_in)) if path_in != '' else print("当前使用默认路径。")
        print("--*--*--#--*--*--")
        path_out = input("请输入转换后的文件保存的文件夹的路径。(仅需要输入文件夹的路径即可，跳过则文件保存至当前文件夹所在的路径下的\\file_out)\n")
        maker.set_out_path(path_out)
        print("您当前输入的路径为:{}".format(path_out)) if path_out != '' else print("当前使用默认路径。")
        print("--*--*--#--*--*--")
        using_block = input('请输入结构所使用的方块，限在["wool", "concrete", "terracotta"]中任选1-3个。默认使用wool.\n'
                            '如需多选请使用("圆括号","加引号")或["中括号","加引号"](元组或列表的形式)输入。\n'
                            '例如直接输入wool或输入["wool", "concrete"]，全部使用的话也可直接输入all。\n')
        if len(using_block) > 0 and (using_block[0] in ["[", "("]):
            maker.set_using_blocks(eval(using_block))
        else:
            maker.set_using_blocks(using_block)
        print("您当前输入的方块为:{}".format(using_block)) if using_block != '' else print("当前使用默认方块。")
        print("--*--*--#--*--*--")
        others = input("是否还有其他需要设置的，如有需要设置的话请以{'大括号': '冒号引号','的方式': '继续进行设置'}(字典形式)输入：\n"
                       f"{maker.get_allow_color_space()} 以上是允许继续设置的参数，如不需要的话可以直接跳过。\n")
        if others == '':
            pass
        elif type(eval(others)) == dict:
            for key, value in eval(others).items():
                if key not in maker.get_allow_setting():
                    raise Exception(f"Error:\n\t参数'{key}'无法被设置，可能是因为不存在，也可能是不允许设置这个参数。")
                exec(f"maker.{key} = '{value}'")
                print(f"您所设置的'{key}' = '{value}'.")
        else:
            raise Exception("Error:\n\t设置的格式有误，无法进行设置。")
        print("--*--*--#--*--*--")
        while True:
            if not (maker.batch and maker.get_size()):
                size = input("请输入所需要的结构的大小，格式为元组或列表的形式，例如(96, 72).\n")
                if size == '':
                    raise Exception("Error:\n\t结构大小没有默认值。请输入需要的结构大小。")
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
                print("运行结束。")
                break
    except Exception as result:
        print("\n\n", result, "\n\n")
    finally:
        os.system("pause")
