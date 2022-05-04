# -*- coding:utf-8 -*-
# @Time : 2022/5/3 下午 5:31
# @Author : Dedicatus1979
# @File : picture.py
# @Software : PyCharm

"""这个类其实就是把PIL库中的一些功能给重新调用封装了一下，基本内容就是转换色彩模式与改变图片大小。
如果有需要的话，也可以导入这个类而直接使用这个类中的内容，但不建议这么做，因为PIL库已经封装得很简单了。。"""

from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image


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
            raise TypeError(f"TypeError:\n\t输入图片'{self.__picture_path}'的颜色空间超出了预期，请保证颜色为'RGBA'或'RGB'")

    def picture_to_L(self):
        """将图片转换为灰度模式
        本方法需要Image的图片"""
        self.picture_to_rgb()
        self.__picture = self.__picture.convert('L')

    def picture_resize(self, struct_size: Union[tuple[int, int], list[int, int]]):
        """转变图片的大小，也就是转换成所需要的结构的大小
        本方法需要Image的图片"""
        self.__picture = self.__picture.resize(struct_size)
