"""
mpi_kernel.py  并行的电磁场更新内核（沿 x 方向分解）
"""
from .kernel import FDTDKernel

class MPIKernel(FDTDKernel):
    def __init__(self, xp, comm, domain):
        super().__init__(xp)
        self.comm = comm
        self.rank = comm.Get_rank()
        self.size = comm.Get_size()
        self.domain = domain

    def _exchange(self, F):
        """沿 x 方向交换一个场分量的 ghost 层"""
        comm = self.comm
        rank = self.rank
        size = self.size

        send_left = F[1, :, :].copy()
        recv_right = F[0, :, :].copy()
        if rank > 0:
            comm.Sendrecv(send_left, dest=rank-1, recvbuf=recv_right, source=rank-1)
            F[0, :, :] = recv_right

        send_right = F[-2, :, :].copy()
        recv_left = F[-1, :, :].copy()
        if rank < size-1:
            comm.Sendrecv(send_right, dest=rank+1, recvbuf=recv_left, source=rank+1)
            F[-1, :, :] = recv_left

    def _exchange_E(self, Ex, Ey, Ez):
        self._exchange(Ey)
        self._exchange(Ez)

    def _exchange_H(self, Hx, Hy, Hz):
        self._exchange(Hy)
        self._exchange(Hz)

    def fdtd_step(self, Ex, Ey, Ez, Hx, Hy, Hz,
                  step_NA_temp, step_NB_temp, step_NC_temp, step_ND_temp):
        # 1. 交换电场 ghost
        self._exchange_E(Ex, Ey, Ez)
        # 2. 更新磁场（公式与父类完全一致）
        Hx[1:-1, 1:-1, 1:-1] = step_NC_temp * Hx[1:-1, 1:-1, 1:-1] + step_ND_temp * (
            (Ey[1:-1, 1:-1, 2:] - Ey[1:-1, 1:-1, 1:-1]) -
            (Ez[1:-1, 2:, 1:-1] - Ez[1:-1, 1:-1, 1:-1]))
        Hy[1:-1, 1:-1, 1:-1] = step_NC_temp * Hy[1:-1, 1:-1, 1:-1] + step_ND_temp * (
            (Ez[2:, 1:-1, 1:-1] - Ez[1:-1, 1:-1, 1:-1]) -
            (Ex[1:-1, 1:-1, 2:] - Ex[1:-1, 1:-1, 1:-1]))
        Hz[1:-1, 1:-1, 1:-1] = step_NC_temp * Hz[1:-1, 1:-1, 1:-1] + step_ND_temp * (
            (Ex[1:-1, 2:, 1:-1] - Ex[1:-1, 1:-1, 1:-1]) -
            (Ey[2:, 1:-1, 1:-1] - Ey[1:-1, 1:-1, 1:-1]))
        # 3. 交换磁场 ghost
        self._exchange_H(Hx, Hy, Hz)
        # 4. 更新电场
        Ex[1:-1, 1:-1, 1:-1] = step_NA_temp * Ex[1:-1, 1:-1, 1:-1] + step_NB_temp * (
            (Hy[1:-1, 1:-1, 1:-1] - Hy[1:-1, 1:-1, :-2]) -
            (Hz[1:-1, 1:-1, 1:-1] - Hz[1:-1, :-2, 1:-1]))
        Ey[1:-1, 1:-1, 1:-1] = step_NA_temp * Ey[1:-1, 1:-1, 1:-1] + step_NB_temp * (
            (Hz[1:-1, 1:-1, 1:-1] - Hz[:-2, 1:-1, 1:-1]) -
            (Hx[1:-1, 1:-1, 1:-1] - Hx[1:-1, 1:-1, :-2]))
        Ez[1:-1, 1:-1, 1:-1] = step_NA_temp * Ez[1:-1, 1:-1, 1:-1] + step_NB_temp * (
            (Hx[1:-1, 1:-1, 1:-1] - Hx[1:-1, :-2, 1:-1]) -
            (Hy[1:-1, 1:-1, 1:-1] - Hy[:-2, 1:-1, 1:-1]))

    def pml_step(self, Ex, Ey, Ez, Hx, Hy, Hz, boundary_layers, pml_sigma_d):
        """
        仅对全局物理边界施加 PML 衰减。
        场数组包含 ghost 层，内部有效区域为 [1:-1, :, :]。
        """
        dom = self.domain
        # 辅助函数：对某个场分量的特定面进行衰减并置零最外层
        def apply_pml_face(F, axis, side):
            """ axis: 'x','y','z' ; side: 0 表示低端, 1 表示高端 """
            if axis == 'x':
                if side == 0:  # x 低端
                    if dom.is_global_xmin():
                        F[1 : 1+boundary_layers, :, :] *= pml_sigma_d
                        F[1, :, :] = 0  # 最外层置零
                else:  # x 高端
                    if dom.is_global_xmax():
                        F[-1-boundary_layers : -1, :, :] *= pml_sigma_d
                        F[-2, :, :] = 0
            elif axis == 'y':
                if side == 0:
                    if dom.is_global_ymin():
                        F[1:-1, 1 : 1+boundary_layers, :] *= pml_sigma_d
                        F[1:-1, 1, :] = 0
                else:
                    if dom.is_global_ymax():
                        F[1:-1, -1-boundary_layers : -1, :] *= pml_sigma_d
                        F[1:-1, -2, :] = 0
            else:  # 'z'
                if side == 0:
                    if dom.is_global_zmin():
                        F[1:-1, :, 1 : 1+boundary_layers] *= pml_sigma_d
                        F[1:-1, :, 1] = 0
                else:
                    if dom.is_global_zmax():
                        F[1:-1, :, -1-boundary_layers : -1] *= pml_sigma_d
                        F[1:-1, :, -2] = 0
    
        # 对六个场分量分别处理六个面
        for F in (Ex, Ey, Ez, Hx, Hy, Hz):
            apply_pml_face(F, 'x', 0)
            apply_pml_face(F, 'x', 1)
            apply_pml_face(F, 'y', 0)
            apply_pml_face(F, 'y', 1)
            apply_pml_face(F, 'z', 0)
            apply_pml_face(F, 'z', 1)