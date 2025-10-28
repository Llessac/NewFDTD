"""

grid.py 提供仿真区域的设置

Region : 仿真区域设置
Mesh : 额外的精细仿真网格

"""
from .mathTool import *

class Region:
    def __init__(self, x_min:float=0, length:float=0, y_min:float=0,width:float=0, z_min:float=0, height:float=0, temperate=300, background_index=1.0, boundary="PML"):
        """
        创建仿真区域

        参数：
        x_min : x轴最小值
        length : x轴上长度
        y_min : y轴最小值
        width : y轴上宽度
        z_min : z轴最小值
        height : z轴上高度
        temperate : 温度(K)
        background_index : 背景折射率
        boundary : 边界条件
            PML

        """
        self.x_min = float(x_min)
        self.length = float(length)
        self.y_min = float(y_min)
        self.width = float(width)
        self.z_min = float(z_min)
        self.height = float(height)

        self.res = min(self.length, self.width, self.height) / 100

        self.name = "FDTD"

        self.step_time_factor = 0.8
        self.step_time = self.res / 1.7320508  / c * self.step_time_factor
        self.simulation_time = 0
        self.temperate = temperate

        self.background_material = "Constant"
        self.background_index = background_index

        self.boundary = boundary
        self.boundary_layers = 8
        self.boundary_sigma = 1

        self.mesh = []

    def append(self, mesh):
        self.mesh.append(mesh)

    def delete(self, mesh):
        self.mesh.remove(mesh)

    def set_res(self, r):
        self.res = float(r)
        self.step_time = self.res / 1.7320508  / c * self.step_time_factor
        self.simulation_time = 0

    def set_step_time_factor(self, step_time_factor):
        if 0 < step_time_factor < 1:
            self.step_time = self.res / 1.7320508  / c * self.step_time_factor
        else:
            print("Step_time_factor must be between 0 and 1!")
        
    def set_simulation_time(self, simulation_time):
        self.simulation_time = simulation_time


class Mesh:
    def __init__(self, res:float=0, x_min:float=0, length:float=0, y_min:float=0, width:float=0, z_min:float=0, height:float=0):
        """
        创建精细网格

        参数：
        res : 精细网格分辨率
        x_min : x轴最小值
        length : x轴上长度
        y_min : y轴最小值
        width : y轴上宽度
        z_min : z轴最小值
        height : z轴上高度

        """
        self.x_min = float(x_min)
        self.length = float(length)
        self.y_min = float(y_min)
        self.width = float(width)
        self.z_min = float(z_min)
        self.height = float(height)
        self.name = ""
