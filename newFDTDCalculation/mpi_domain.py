"""
mpi_domain.py  沿 x 方向一维分解的 MPI 计算域
"""
from .domain import Domain

class MPIDomain(Domain):
    def __init__(self, length, width, height, res, boundary_layers, comm):
        super().__init__(length, width, height, res, boundary_layers)
        self.comm = comm
        self.rank = comm.Get_rank()
        self.size = comm.Get_size()

        total = length
        base = total // self.size
        rem = total % self.size
        if self.rank < rem:
            self.local_nx = base + 1
            self.x_start = self.rank * (base + 1)
        else:
            self.local_nx = base
            self.x_start = self.rank * base + rem
        self.x_end = self.x_start + self.local_nx - 1

        self.local_offset = 1       # ghost 偏移，本地有效数据从索引1开始

    @property
    def local_size(self):
        return (self.local_nx, self.width, self.height)

    def global_to_local(self, ix, iy, iz):
        if self.x_start <= ix <= self.x_end:
            return (ix - self.x_start + self.local_offset, iy, iz)
        return None

    def is_local(self, global_slice):
        x_slice = global_slice[0]
        if isinstance(x_slice, slice):
            start, stop, step = x_slice.indices(self.length)
            if step != 1:
                raise ValueError("仅支持 step=1 的切片")
            g_start = start
            g_end = stop - 1
        else:
            g_start = x_slice
            g_end = x_slice
        return not (g_end < self.x_start or g_start > self.x_end)

    def global_to_local_range(self, global_start, global_end):
        if global_end < self.x_start or global_start > self.x_end:
            return None
        local_start = max(global_start, self.x_start) - self.x_start + self.local_offset
        local_end   = min(global_end, self.x_end) - self.x_start + self.local_offset
        return (local_start, local_end)

    def localize_slice(self, global_slice_tuple):
        """
        将全局切片三元组（可以是整数/切片，厚度方向为整数或切片）转换为本地切片三元组。
        若完全不与本进程相交，返回 None。
        """
        x = global_slice_tuple[0]
        y = global_slice_tuple[1]
        z = global_slice_tuple[2]

        # 处理 x 维度
        if isinstance(x, slice):
            start, stop, step = x.indices(self.length)
            if step != 1:
                raise ValueError("不支持 step!=1 的切片")
            g_start = start
            g_end = stop - 1
        else:  # 整数
            g_start = x
            g_end = x

        x_range = self.global_to_local_range(g_start, g_end)
        if x_range is None:
            return None

        local_start, local_end = x_range
        # 重建 x 切片，保持 int/slice 风格一致
        if isinstance(x, slice):
            new_x = slice(local_start, local_end + 1)
        else:
            new_x = local_start   # 厚度方向仍然是单个整数索引

        # y 和 z 维度不变（未分解）
        return (new_x, y, z)
    
    def is_global_xmin(self):
        """本进程是否包含全局 x 方向的最小边界"""
        return self.x_start == 0

    def is_global_xmax(self):
        """本进程是否包含全局 x 方向的最大边界"""
        return self.x_end == self.length - 1

    def is_global_ymin(self):
        """y 方向未分解，始终是全局边界"""
        return True

    def is_global_ymax(self):
        return True

    def is_global_zmin(self):
        return True

    def is_global_zmax(self):
        return True