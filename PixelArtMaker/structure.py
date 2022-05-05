# -*- coding:utf-8 -*-
# @Time : 2022/5/3 下午 5:31
# @Author : Dedicatus1979
# @File : structure.py
# @Software : PyCharm

"""这个类主要就是用于生成nbt结构的，对外接口也只有一个，不建议直接导入这个类、使用这个类。"""

from typing import Union

import numpy as np
from nbt import nbt
from tqdm import trange

from .color import Color

"""
大致说下mc结构里的内容吧，一个mc中的nbt结构文件的结构类似于如下：
    name.nbt
        |---size[List]          结构的大小
        |---palette[List]       结构中的方块的编号
        |---blocks[List]        结构中的方块坐标与方块编号
        |---entities[List]      结构中的实体
        |---author[String]      结构的作者
        |---DataVersion[Int]    结构的数据版本？（这个我也不是很清楚）
其中中括号内的是这个文件的类型，author是1.13扁平化更新之前才有文件。新版本已经取消了。
    size[List]
        |--- [Int]
      ......
size内存储的是三个整型数，三个数据从上至下编号为0, 1, 2; 分别为游戏的 x, y, z 三根轴。其表示的是这个结构总的大小。
    palette[List]
        |--- [Compound]
                |---Properties[Compound]
                        |---color[String]
                      ......
                |---Name[String]
              ......
      ......
palette内存有n个Compound类型的文件夹，其中每个文件夹内的内容便是方块的数据。文件夹从上至下从0开始编号，这个编号就是这个方块在这个文件中的编号。
在这个文件内还又一个文件夹与一个String类型的数据，Name即是这这个方块在mc中的名称，例如黑色羊毛方块就是minecraft:black_wool。
Properties这个文件夹内存放的是这个方块的一些特殊状态。例如在1.13扁平化更新之前羊毛方块统一使用的名称是minecraft:wool，
想要表示黑色羊毛方块的话就得在Properties这个文件夹内再放一个名为color的String类型的数据，里面写上black，这样表示的才是一个黑色的羊毛方块。
当然Properties里可以放的东西也绝不止color一个东西。也可以什么都不放（也就是这个文件夹不创也没事）
    blocks[List]
        |--- [Compound]
                |---pos[List]
                        |--- [Int]
                      ......
                |---state[Int]
                |---nbt[Compound] 
                        |--- ......
                      ......
              ......
      ......
blocks内也存有多个Compound类型的文件夹，其中每个文件夹内的内容便是方块的位置信息与其他信息的调用。
pos内存放有三个整型数，这就是这个方块在这个结构中的位置，数据格式与size中的一样，这里就不多啰嗦了。
state内存放的数据就是这个方块的方块编号，例如某个位置应该放黑色的羊毛方块，通过palette内存放的数据，我们就能知道黑色羊毛方块的编号是多少了，
假设黑色羊毛方块在palette内的编号是0，那这里的state的数据也就是0了。
nbt文件夹是存放这个方块自带的nbt值，例如这个方块是一个箱子，那箱子内本身也可能有东西，那箱子里的东西就写在这个文件夹内。
entities我就不过多介绍了，因为这个像素画生成器根本就没用到实体。
author与DataVersion我也不介绍了，因为这两个数据属于是可有可无的那种，没有的话照样能用。"""


class Structure:
    def __init__(self, version: float, direction: str, struct_size: Union[tuple[int, int], list[int, int]],
                 using_blocks: Union[list, tuple], color_space: str):
        """定义结构，需要输入结构的大小，结构大小为1*2的元组，为图片的长与宽。游戏版本，仅仅支持1.12与1.18。
        游戏中的观看方向，两种模式，南北'ns'与上下'ud'，其他的内容不接受"""
        self.version = version
        self.direction = direction
        self.color_space = color_space
        self.block = self.__check_using_block(using_blocks)
        self.struct_size = self.__check_struct_size(struct_size)
        self.color = Color(self.color_space, self.block)

        self.block_dict = {"wool": "wool", "concrete": "concrete",
                           "terracotta": "stained_hardened_clay" if self.version <= 1.12 else "terracotta"}
        self.color_dict = {0: "white", 1: "orange", 2: "magenta", 3: "light_blue", 4: "yellow", 5: "lime", 6: "pink",
                           7: "gray", 8: "silver" if self.version <= 1.12 else "light_gray", 9: "cyan", 10: "purple",
                           11: "blue", 12: "brown", 13: "green", 14: "red", 15: "black"}

    def __check_using_block(self, block):
        """用于将列表或元组using_block去重并小写化"""
        temp = list(set(block))
        for i in range(len(temp)):
            temp[i] = temp[i].lower()
        return temp

    def __check_struct_size(self, struct_size):
        """用于检测struct_size是否正确，且是否超过最大值"""
        if not isinstance(struct_size, (list, tuple)):
            raise ValueError(f"ValueError:\n\t未设置结构大小，或设置的内容不是list或tuple类型。")
        if self.direction == "ns":
            if struct_size[1] <= 256:
                return struct_size
            elif self.version >= 1.18 and struct_size[1] <= 383:
                return struct_size
            else:
                raise ValueError(f"ValueError:\n\t建筑高度'{struct_size[1]}'超过了'{self.version}'版本的最大建筑高度。")
        else:
            return struct_size

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
            my_size.tags.extend([nbt.TAG_Int(self.struct_size[0]), nbt.TAG_Int(self.struct_size[1]), nbt.TAG_Int(1)])
        else:
            my_size.tags.extend([nbt.TAG_Int(self.struct_size[0]), nbt.TAG_Int(1), nbt.TAG_Int(self.struct_size[1])])
        struction.tags.append(my_size)
        # struction.tags.append(nbt.TAG_List(name="entities", type=nbt._TAG_End))        # 这个我真不知道是啥了，而且这个文件不是必要的，可以注释掉
        # 添加方块与方块的颜色
        my_blocks = nbt.TAG_List(name="blocks", type=nbt.TAG_Compound)
        t_range = trange(self.struct_size[1], postfix={"Now file": times + 1, "Total": all_time})
        t_range.set_description("少女祈祷中...")
        for i in t_range:
            for j in range(self.struct_size[0]):
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
