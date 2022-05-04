# -*- coding:utf-8 -*-
# @Time : 2022/5/3 下午 5:32
# @Author : Dedicatus1979
# @File : __init__.py
# @Software : PyCharm

"""关于这个模块的更多信息，可以在 https://github.com/Dedicatu1979/MCPixelArtMaker 里查看更多"""

__version__ = "1.1.1"

from .color import Color
from .maker import Maker
from .picture import Picture
from .structure import Structure

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
    应该这些地方还有很多可以去掉的语句之类的。
2022.5.3 又去掉了几个冗余的方法。话说为什么我感觉我明明在去掉多余的代码，可代码量却一直没变啊。。。
    把文件进行了拆分，打包。说实话这是我第一次把一个程序给拆分打包。以前都是全写一个文件里的。。
    把maker.py里的方法基本又重写了好多，真的累。。。。
    已知bug1: 在exe中或直接使用本文件时，Maker.batch无论设置的是什么，只要设置了就一定会变成True。不想修这个bug，主要是没意义。。(这个bug已经修掉了)
    bug2: 在非批量模式下依旧可以批量生成文件，方法是在Maker.transformation()之前多设置几个set_transformation_file()，这个bug也没有多大修的必要。。
        (我其实觉得这个可以当个特性用，没必要修)
2022.5.4 又把maker给删删改改了下，顺带给这些文件通通加了些介绍。"""
