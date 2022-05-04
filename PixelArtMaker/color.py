# -*- coding:utf-8 -*-
# @Time : 2022/5/3 下午 5:31
# @Author : Dedicatus1979
# @File : color.py
# @Software : PyCharm

"""这个类主要就是用于寻找与输入像素颜色最为类似的颜色，对外接口只有一个，不建议直接导入这个类、使用这个类。
但这个文件中有些常数组与两个rgb转其他色彩空间的函数，如果有必要的话，也不是不能直接导入文件使用。"""

from typing import Union

import numpy as np

"""
这个文件内的内容可以说是这整个生成器中技术力最高的一个文件了，需要理解的话需要一点点线性代数的知识，其实也不难，我们先来讲讲rgb转hsv吧。
rgb转hsv或hsl的算法其实并不难，而且可以在维基百科中直接找到，我也不过多介绍了，主要说明一点，hsv或hsl的三个分量h、s、v或l的值域，分别应该为
[0, 360)°, [0, 1], [0, 1]。但这里所使用的三个分量的值域却分别为[-127, 127], [-127, 127], [0, 255]。
原因是因为rgb的三个分量可以简单的看作是三维笛卡尔坐标系中第一卦限的一个点。而hsv由于第一个量是角度的关系，将其直接当点计算较为复杂，
所以这里是将hsv本身的三维圆柱坐标系转换为三维笛卡尔坐标系上第1至第4卦限上的一个点。具体的转换关系是：
x = s cos(h); y = s sin(h); z = v
这样就将圆柱坐标系转换为笛卡尔坐标系了。这对之后的计算也会方便许多。
好了我们接下来来说明如何给定一个rgb值，在另外有限个rgb中寻找与这个rgb值最接近的rgb值。
空间中两个点的接近程度其实就是两个点的空间距离，a[x1, y1, z1], b[x2, y2, z2]。那|ab| = √[(x1-x2)^2+(y1-y2)^2+(z1-z2)^2]。
如果将a,b两点看作是两个向量的话，那a-b = [x1-x2, y1-y2, z1-z2]，此时再将里面的值给平方求和，不需要开根号，因为我们求的是最为接近的向量，
而不是两向量之间的距离，所以最小的那条向量就是我们想要的向量。
例如向量a = [[3],    b = [[1, 3, 5],       我们将列向量看作是一个rgb值（这里为了方便以2*1的向量表示一个rgb值）
            [2]]         [2, 4, 6]]       a是已知rgb，b是有限个向量，我们想从b中找到与a最接近的rgb值
一般来说a-b是不允许的，因为a与b并不同型，需要将a扩充为[[3, 3, 3],  才可以进行计算，
                                                [2, 2, 2]]  可numpy中可以实现这种不同型的矩阵(数组)计算
计算结果为: [[2, 0, -2],  每项平方后就是[[4, 0, 4],  每列再求和，就是s = [4, 4, 20]，
           [0, -2, -4]]               [0, 4, 16]]  
很容易发现s[0]的值与s[1]的值是一样的，也就是说a与b[0]与b[1]的距离是相同且都是最短的。那我们便找到了与a最为接近的rgb值了。
我们可以取第一个，也就是取b[0]作为a的近似rgb值。"""

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
