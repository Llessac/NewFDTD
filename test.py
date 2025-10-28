"""
test.py
这个文件提供newFDTDCalculation的使用示例
"""

# 导入模块
from newFDTDCalculation.grid import *
from newFDTDCalculation.object import *
from newFDTDCalculation.source import *
from newFDTDCalculation.detector import *
from newFDTDCalculation.calculation import *


# 加载并设置仿真程序主框架
a = Calculation()
a.set_space_unit('μm')


# 设置仿真区域与边界条件
g = Region(-0.5, 1, -0.5, 1, -0.5, 1,
            temperate=300, background_index=1.0, boundary="PML")
g.set_res(0.01) # 设置分辨率
a.add_Region(g) # 添加该区域到仿真程序中



# 设置物体树
# 物体树为混合嵌套列表， 可包含物体组ObjectGroup和物体Object，物体组ObjectTree中可包含物体Object和物体组ObjectTree
# 设置单个物体
o1 = Rectangle(0, -0.05, 0, 0.9, 0.1, 0.2) 
o1.color="pink"
o1.set_constant_index(2)
# 设置物体组
o = ObjectGroup()
for i in range(5):
    o.append(Rectangle(-0.4 + i * 0.2, 0.1, 0, 0.1, 0.2, 0.2)) # 物体组添加物体
    o.objects[-1].color = 'blue'
o.set_constant_index(1.4) # 物体组整体设置折射率
a.add_ObjectTree(o, o1) # 添加物体和物体组到物体树中



# 设置源
s = GaussianSource(0, 0.4, 0, 2, 0, 2, "y_plane", direction="Backward")
a.add_Source(s)



# 设置监视器
m1 = MovieDetector(0, 0, 0, 1, 1, 0, "z_plane","MovieOutput", field_component="Ez")
m2 = PointDetector(0, 0, 0, "PointOutput", field_component="Ez")
a.add_Detector(m1)



# 保存仿真文件
a.save("fdtdNew")

# 显示3D图
a.show3D()

# 仿真计算
a.run()
