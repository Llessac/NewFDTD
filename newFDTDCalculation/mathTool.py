"""
mathTool.py
包含运算中所用到的物理常数、计算工具库
单位为国际标准单位制
长度单位暂时为μm 时间单位暂时为fs
"""


import numpy as np
from scipy.signal import gausspulse
import math
import os


# -------------------- 后端选择 --------------------
# 根据环境变量 FDTD_GPU 决定 xp 是 CuPy 还是 NumPy
_use_gpu = os.environ.get('FDTD_GPU', '0') == '1'
if _use_gpu:
    try:
        import cupy as xp
    except ImportError:
        xp = np  # 回退到 NumPy
        print("警告: CuPy 未安装，已回退到 NumPy。")
else:
    xp = np  # 默认使用 NumPy


# -------------------- 物理常数 --------------------
eps0 = 8.854187817 # 真空介电常数 pC^2 / N / μm^2
mu0 = 1.2566370614359 # 真空磁导率 N * fs^2 / pC^2
c = 0.299792458  # 真空光速 μm/fs
# 电场强度为N/pC
# 磁场强度为pC/fs/μm
# eps0 = 8.854187817e-12
# mu0 = 4e-7 * pi
# c = 2.99792458e8

pi = np.pi
e = np.e

degree_to_radian = 0.0174532925199 # 度转换弧度
radian_to_degree = 57.295779513082 # 弧度转换度


# -------------------- 工具函数 --------------------
def sqrt(x):
    '''
    开根号
    '''
    return np.sqrt(x)


def gradient_index(x1, x2, p1, p2):
    """渐变折射率分布生成器"""
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


# -------------------- 三维高斯分布生成（支持后端选择） --------------------
def create_3d_gaussian(size, sigma, res, xp_backend=None):
    """
    创建一个厚度方向为1的二维高斯分布(在三维网格中)。
    
    参数:
    - size: (x, y, z) 网格点数,厚度方向为1。
    - sigma: 高斯标准差（物理单位）
    - res: 网格分辨率
    - xp_backend: 可选后端模块(numpy或cupy),默认使用本文件的np(NumPy)
    """
    if xp_backend is None:
        xp_backend = np          # 默认CPU，保持向后兼容

    sigma_ = sigma / res
    if size[0] == 1:
        x, y = xp_backend.meshgrid(
            xp_backend.linspace(0, size[1], size[1]),
            xp_backend.linspace(0, size[2], size[2])
        )
        d = xp_backend.sqrt((x - size[1]/2)**2 + (y - size[2]/2)**2)
        g = xp_backend.exp(- d**2 / (2 * sigma_**2)).reshape((size[2], size[1])).T
        return g
    elif size[1] == 1:
        x, y = xp_backend.meshgrid(
            xp_backend.linspace(0, size[0], size[0]),
            xp_backend.linspace(0, size[2], size[2])
        )
        d = xp_backend.sqrt((x - size[0]/2)**2 + (y - size[2]/2)**2)
        g = xp_backend.exp(- d**2 / (2 * sigma_**2)).reshape((size[2], size[0])).T
        return g
    elif size[2] == 1:
        x, y = xp_backend.meshgrid(
            xp_backend.linspace(0, size[0], size[0]),
            xp_backend.linspace(0, size[1], size[1])
        )
        d = xp_backend.sqrt((x - size[0]/2)**2 + (y - size[1]/2)**2)
        g = xp_backend.exp(- d**2 / (2 * sigma_**2)).reshape((size[1], size[0])).T
        return g



if __name__ == "__main__":
    a = create_3d_gaussian((101, 1, 110), 1, 0.01)
    import matplotlib.pyplot as plt
    plt.imshow(a)
    plt.show()
