"""
kernel.py 核心电磁场更新函数
"""


class FDTDKernel:
    """FDTD 场求解内核，封装场更新与 PML 边界"""
    def __init__(self, xp):
        self.xp = xp
    
    def fdtd_step(self, Ex, Ey, Ez, Hx, Hy, Hz, step_NA_temp, step_NB_temp, step_NC_temp, step_ND_temp):
        """电磁场更新"""
        Hx[1:-1, 1:-1, 1:-1] = step_NC_temp * Hx[1:-1, 1:-1, 1:-1] + step_ND_temp * ((Ey[1:-1, 1:-1, 2:] - Ey[1:-1, 1:-1, 1:-1]) - (Ez[1:-1, 2:, 1:-1] - Ez[1:-1, 1:-1, 1:-1]))
        Hy[1:-1, 1:-1, 1:-1] = step_NC_temp * Hy[1:-1, 1:-1, 1:-1] + step_ND_temp * ((Ez[2:, 1:-1, 1:-1] - Ez[1:-1, 1:-1, 1:-1]) - (Ex[1:-1, 1:-1, 2:] - Ex[1:-1, 1:-1, 1:-1]))
        Hz[1:-1, 1:-1, 1:-1] = step_NC_temp * Hz[1:-1, 1:-1, 1:-1] + step_ND_temp * ((Ex[1:-1, 2:, 1:-1] - Ex[1:-1, 1:-1, 1:-1]) - (Ey[2:, 1:-1, 1:-1] - Ey[1:-1, 1:-1, 1:-1]))
        Ex[1:-1, 1:-1, 1:-1] = step_NA_temp * Ex[1:-1, 1:-1, 1:-1] + step_NB_temp * ((Hy[1:-1, 1:-1, 1:-1] - Hy[1:-1, 1:-1, :-2]) - (Hz[1:-1, 1:-1, 1:-1] - Hz[1:-1, :-2, 1:-1]))
        Ey[1:-1, 1:-1, 1:-1] = step_NA_temp * Ey[1:-1, 1:-1, 1:-1] + step_NB_temp * ((Hz[1:-1, 1:-1, 1:-1] - Hz[:-2, 1:-1, 1:-1]) - (Hx[1:-1, 1:-1, 1:-1] - Hx[1:-1, 1:-1, :-2]))
        Ez[1:-1, 1:-1, 1:-1] = step_NA_temp * Ez[1:-1, 1:-1, 1:-1] + step_NB_temp * ((Hx[1:-1, 1:-1, 1:-1] - Hx[1:-1, :-2, 1:-1]) - (Hy[1:-1, 1:-1, 1:-1] - Hy[:-2, 1:-1, 1:-1]))

    def pml_step(self, Ex, Ey, Ez, Hx, Hy, Hz, boundary_layers, pml_sigma_d):
        """PML 吸收边界"""
        Hx[0:boundary_layers, :, :] *= pml_sigma_d
        Hy[0:boundary_layers, :, :] *= pml_sigma_d
        Hz[0:boundary_layers, :, :] *= pml_sigma_d

        Hx[- boundary_layers + 1:, :, :] *= pml_sigma_d
        Hy[- boundary_layers + 1:, :, :] *= pml_sigma_d
        Hz[- boundary_layers + 1:, :, :] *= pml_sigma_d

        Hx[:, 0:boundary_layers, :] *= pml_sigma_d
        Hy[:, 0:boundary_layers, :] *= pml_sigma_d
        Hz[:, 0:boundary_layers, :] *= pml_sigma_d

        Hx[:, - boundary_layers + 1:, :] *= pml_sigma_d
        Hy[:, - boundary_layers + 1:, :] *= pml_sigma_d
        Hz[:, - boundary_layers + 1:, :] *= pml_sigma_d

        Hx[:, :, 0:boundary_layers] *= pml_sigma_d
        Hy[:, :, 0:boundary_layers] *= pml_sigma_d
        Hz[:, :, 0:boundary_layers] *= pml_sigma_d

        Hx[:, :, - boundary_layers + 1:] *= pml_sigma_d
        Hy[:, :, - boundary_layers + 1:] *= pml_sigma_d
        Hz[:, :, - boundary_layers + 1:] *= pml_sigma_d

        Ex[0:boundary_layers, :, :] *= pml_sigma_d
        Ey[0:boundary_layers, :, :] *= pml_sigma_d
        Ez[0:boundary_layers, :, :] *= pml_sigma_d

        Ex[- boundary_layers + 1:, :, :] *= pml_sigma_d
        Ey[- boundary_layers + 1:, :, :] *= pml_sigma_d
        Ez[- boundary_layers + 1:, :, :] *= pml_sigma_d

        Ex[:, 0:boundary_layers, :] *= pml_sigma_d
        Ey[:, 0:boundary_layers, :] *= pml_sigma_d
        Ez[:, 0:boundary_layers, :] *= pml_sigma_d

        Ex[:, - boundary_layers + 1:, :] *= pml_sigma_d
        Ey[:, - boundary_layers + 1:, :] *= pml_sigma_d
        Ez[:, - boundary_layers + 1:, :] *= pml_sigma_d

        Ex[:, :, 0:boundary_layers] *= pml_sigma_d
        Ey[:, :, 0:boundary_layers] *= pml_sigma_d
        Ez[:, :, 0:boundary_layers] *= pml_sigma_d

        Ex[:, :, - boundary_layers + 1:] *= pml_sigma_d
        Ey[:, :, - boundary_layers + 1:] *= pml_sigma_d
        Ez[:, :, - boundary_layers + 1:] *= pml_sigma_d


        Hx[-1, :, :] = 0
        Hy[-1, :, :] = 0
        Hz[-1, :, :] = 0

        Hx[:, -1, :] = 0
        Hy[:, -1, :] = 0
        Hz[:, -1, :] = 0

        Hx[:, :, -1] = 0
        Hy[:, :, -1] = 0
        Hz[:, :, -1] = 0

        Ex[-1, :, :] = 0
        Ey[-1, :, :] = 0
        Ez[-1, :, :] = 0

        Ex[:, -1, :] = 0
        Ey[:, -1, :] = 0
        Ez[:, -1, :] = 0

        Ex[:, :, -1] = 0
        Ey[:, :, -1] = 0
        Ez[:, :, -1] = 0


        Hx[0, :, :] = 0
        Hy[0, :, :] = 0
        Hz[0, :, :] = 0

        Hx[:, 0, :] = 0
        Hy[:, 0, :] = 0
        Hz[:, 0, :] = 0

        Hx[:, :, 0] = 0
        Hy[:, :, 0] = 0
        Hz[:, :, 0] = 0

        Ex[0, :, :] = 0
        Ey[0, :, :] = 0
        Ez[0, :, :] = 0

        Ex[:, 0, :] = 0
        Ey[:, 0, :] = 0
        Ez[:, 0, :] = 0

        Ex[:, :, 0] = 0
        Ey[:, :, 0] = 0
        Ez[:, :, 0] = 0
