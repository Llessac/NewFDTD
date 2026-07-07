'''
domain.py 具体的计算域

'''


class Domain:
    """单进程仿真域：封装网格尺寸、分辨率、边界层数"""
    def __init__(self, length, width, height, res, boundary_layers):
        self.length = length
        self.width = width
        self.height = height
        self.res = res
        self.boundary_layers = boundary_layers

    @property
    def local_size(self):
        """返回本地域尺寸（单进程即全局尺寸）"""
        return self.length, self.width, self.height