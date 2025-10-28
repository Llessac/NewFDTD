"""
mathTool.py
包含运算中所用到的物理常数、计算工具库
单位为国际标准单位制
长度单位暂时为μm 时间单位暂时为fs
"""


import numpy as np
from scipy.signal import gausspulse
import math

eps0 = 8.854187817 # 真空介电常数 pC^2 / N / μm^2
mu0 = 1.2566370614359 # 真空磁导率 N * fs^2 / pC^2
c = 0.299792458  # 真空光速 μm/fs
# 电场强度为N/pC
# 磁场强度为pC/fs/μm


pi = np.pi
e = np.e

# eps0 = 8.854187817e-12
# mu0 = 4e-7 * pi
# c = 2.99792458e8



degree_to_radian = 0.0174532925199 # 度转换弧度
radian_to_degree = 57.295779513082 # 弧度转换度

# 开根号
def sqrt(x):
    return np.sqrt(x)


def gradient_index(x1, x2, p1, p2):
    def judge(x):
        if 0 <= x < x1:
            index = p1
        elif x1 <= x < x2:
            index = (p2 - p1) / (x2 - x1) * (x - x1)
        elif x2 <= x <= 1:
            index = p2
        else:
            index = 0
        return index
    return judge


def create_3d_gaussian(size, sigma, res):
    """
    创建一个三维中二维高斯分布的数组。
    
    参数:
    - size: 高斯分布数组的大小(x, y, z)，例如(10, 10)表示10x10的矩阵。
    - sigma: 高斯分布的标准差。
    - mu_x, mu_y: 高斯分布中心的坐标。
    """
    sigma_ = sigma / res
    if size[0] == 1:
        x, y = np.meshgrid(np.linspace(0, size[1], size[1]), np.linspace(0, size[2], size[2]))
        d = np.sqrt((x - size[1] / 2) ** 2 + (y - size[2] / 2) ** 2)
        g = np.exp(- d ** 2 / (2 * sigma_ ** 2)).reshape((size[2], size[1])).T
        return g
    elif size[1] == 1:
        x, y = np.meshgrid(np.linspace(0, size[0], size[0]), np.linspace(0, size[2], size[2]))
        d = np.sqrt((x - size[0] / 2) ** 2 + (y - size[2] / 2) ** 2)
        g = np.exp(- d ** 2 / (2 * sigma_ ** 2)).reshape((size[2], size[0])).T
        return g
    elif size[2] == 1:
        x, y = np.meshgrid(np.linspace(0, size[0], size[0]), np.linspace(0, size[1], size[1]))
        d = np.sqrt((x - size[0] / 2) ** 2 + (y - size[1] / 2) ** 2)
        g = np.exp(- d ** 2 / (2 * sigma_ ** 2)).reshape((size[1], size[0])).T
        return g



if __name__ == "__main__":
    a = create_3d_gaussian((101, 1, 110), 1, 0.01)
    import matplotlib.pyplot as plt
    plt.imshow(a)
    plt.show()
