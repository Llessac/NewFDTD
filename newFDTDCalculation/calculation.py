"""
calculation.py
仿真程序主框架
"""


import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D, art3d
from matplotlib.animation import FuncAnimation

import json
import copy
import os
from os import path
import time
from mpi4py import MPI

from .mathTool import *
from .grid import *
from .object import *
from .source import *
from .detector import *
from .kernel import *
from .domain import *
from .mpi_domain import MPIDomain
from .mpi_kernel import MPIKernel

# FDTD计算主框架
class Calculation:
    def __init__(self, file_address=0):
        self.space_unit = 'μm'
        self.time_unit = 'fs'

        self.objectTree = []
        self.sources = []
        self.detectors = []

        self.region = Region()
        if file_address:
            self.load_file(file_address)


    # 保存json文件
    def save(self, name='fdtdNew'):
        saveCache = copy.deepcopy(self.__dict__)
        saveCache['region'] = copy.deepcopy(saveCache['region'].__dict__)
        for i in range(len(saveCache["region"]["mesh"])):
            saveCache["region"]["mesh"][i] = copy.deepcopy(saveCache["region"]["mesh"][i].__dict__)
        for i in range(len(saveCache['sources'])):
            saveCache['sources'][i] = copy.deepcopy(saveCache['sources'][i].__dict__)
        for i in range(len(saveCache['detectors'])):
            saveCache['detectors'][i] = copy.deepcopy(saveCache['detectors'][i].__dict__)
            if 'data' in saveCache["detectors"][i]:
                saveCache["detectors"][i].pop('data')
        for i in range(len(saveCache["objectTree"])):
            self._saveObject(saveCache["objectTree"], i)

        name = name.strip()
        # 使用 isabs 取代冒号判断
        if not os.path.isabs(name):
            # 去掉末尾 .json
            if name.endswith('.json'):
                name = name[:-5]
            save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "emulation")
            os.makedirs(save_dir, exist_ok=True)
            name = os.path.join(save_dir, name + ".json")

        # 确保父目录存在
        parent = os.path.dirname(name)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(name, 'w') as f:
            json.dump(saveCache, f, indent=2)
        print(f"*** 保存成功: {name}")

    # 递归存储ObjectTree信息
    def _saveObject(self, objectGroup, i):
        objectGroup[i] = copy.deepcopy(objectGroup[i].__dict__)
        if objectGroup[i]["type"] == "ObjectGroup":
            for i_ in range(len(objectGroup[i]["objects"])):
                self._saveObject(objectGroup[i]["objects"], i_)


    # 解析json文件
    def load_file(self, file_address):
        with open(file_address, 'r') as f:
            file = json.loads(f.read())
            for parameter in file:
                self.__dict__[parameter] = copy.deepcopy(file[parameter])

            self.region = Region()
            for parameter in file["region"]:
                self.region.__dict__[parameter] = copy.deepcopy(file["region"][parameter])
            for i in range(len(file["region"]["mesh"])):
                self.region.mesh[i] = Mesh()
                print(file["region"]["mesh"])
                for parameter in file["region"]["mesh"][i]:
                    self.region.mesh[i].__dict__[parameter] = file["region"]["mesh"][i][parameter]

            for i in range(len(file["sources"])):
                self.sources[i] = globals()[file["sources"][i]["type"]]()
                for parameter in file["sources"][i]:
                    self.sources[i].__dict__[parameter] = file["sources"][i][parameter]

            for i in range(len(file["detectors"])):
                self.detectors[i] = globals()[file["detectors"][i]["type"]]()
                for parameter in file["detectors"][i]:
                    self.detectors[i].__dict__[parameter] = file["detectors"][i][parameter]

            for i in range(len(file["objectTree"])):
                self._loadObject(self.objectTree, file["objectTree"], i)


    # 递归解析ObjectTree信息
    def _loadObject(self, objectGroup, file_objectGroup, i):
        objectGroup[i] = globals()[file_objectGroup[i]["type"]]()
        if objectGroup[i].type != "ObjectGroup":
            for parameter in file_objectGroup[i]:
                objectGroup[i].__dict__[parameter] = file_objectGroup[i][parameter]
        else:
            for i_ in range(len(file_objectGroup[i]["objects"])):
                objectGroup[i].append(0)
                self._loadObject(objectGroup[i].objects, file_objectGroup[i]["objects"], i_)


    # 设置空间单位
    def set_space_unit(self, unit):
        self.space_unit = unit


    # 设置时间单位
    def set_time_unit(self, time_unit):
        self.time_unit = time_unit


    # 添加网格
    def add_Region(self, region):
        self.region = region


    def add_Mesh(self, mesh):
        self.region.append(mesh)


    # 添加物体树
    def add_ObjectTree(self, *object):
        for i in object:
            self.objectTree.append(i)


    # 添加源
    def add_Source(self, *source):
        for i in source:
            self.sources.append(i)


    # 添加探测器
    def add_Detector(self, *detector):
        for i in detector:
            self.detectors.append(i)


    # 展示
    def show3D(self):
        self.region_max = max(self.region.length, self.region.width, self.region.height)
        self.region_d = 0.1 * self.region_max

        self.fig = plt.figure()
        # 3D设置
        self.ax0 = self.fig.add_subplot(222, projection='3d')
        self.ax0.set_xlabel('X')
        self.ax0.set_ylabel('Y')
        self.ax0.set_zlabel('Z')
        self.ax0.set_xlim3d([self.region.x_min - self.region_d, self.region.x_min + self.region_max + self.region_d])
        self.ax0.set_ylim3d([self.region.y_min - self.region_d, self.region.y_min + self.region_max + self.region_d])
        self.ax0.set_zlim3d([self.region.z_min - self.region_d, self.region.z_min + self.region_max + self.region_d])

        # Y-X设置
        self.ax1 = self.fig.add_subplot(221)
        self.ax1.set_xlabel('X')
        self.ax1.set_ylabel('Y')
        self.ax1.set_xlim([self.region.x_min - self.region_d, self.region.x_min + self.region_max + self.region_d])
        self.ax1.set_ylim([self.region.y_min - self.region_d, self.region.y_min + self.region_max + self.region_d])

        # Z-X设置
        self.ax2 = self.fig.add_subplot(223)
        self.ax2.set_xlabel('X')
        self.ax2.set_ylabel('Z')
        self.ax2.set_xlim([self.region.x_min - self.region_d, self.region.x_min + self.region_max + self.region_d])
        self.ax2.set_ylim([self.region.z_min - self.region_d, self.region.z_min + self.region_max + self.region_d])

        # Z-Y设置
        self.ax3 = self.fig.add_subplot(224)
        self.ax3.set_xlabel('Y')
        self.ax3.set_ylabel('Z')
        self.ax3.set_xlim([self.region.y_min - self.region_d, self.region.y_min + self.region_max + self.region_d])
        self.ax3.set_ylim([self.region.z_min - self.region_d, self.region.z_min + self.region_max + self.region_d])
        

        # Region
        self.ax1.add_patch(mpatches.Rectangle((self.region.x_min, self.region.y_min), self.region.length, self.region.width, fill=False, color="yellow", linewidth=5))
        self.ax2.add_patch(mpatches.Rectangle((self.region.x_min, self.region.z_min), self.region.length, self.region.height, fill=False, color="yellow", linewidth=5))
        self.ax3.add_patch(mpatches.Rectangle((self.region.y_min, self.region.z_min), self.region.width, self.region.height, fill=False, color="yellow", linewidth=5, label='Region'))
        drawRectangle(self.ax0, self.region.x_min + self.region.length / 2, self.region.y_min + self.region.width / 2, self.region.z_min + self.region.height / 2, self.region.length, self.region.width, self.region.height, "yellow")

        # Source
        for source in self.sources:
            if source.type == "GaussianSource":
                self.ax1.add_patch(mpatches.Rectangle((source.x - source.length / 2, source.y - source.width / 2), source.length, source.width, fill=True, color="Red", alpha = 0.5))
                self.ax2.add_patch(mpatches.Rectangle((source.x - source.length / 2, source.z - source.height / 2), source.length, source.height, fill=True, color="Red", alpha = 0.5))
                self.ax3.add_patch(mpatches.Rectangle((source.y - source.width / 2, source.z - source.height / 2), source.width, source.height, fill=True, color="Red", alpha = 0.5, label='Source'))
                drawPlane(self.ax0, source.axis, source.x, source.y, source.z, source.length, source.width, source.height, "Red", alpha = 0.5, direction=source.direction)

        # Object
        for object in self.objectTree:
            self._showObject(object)

        # Mesh
        for mesh in self.region.mesh:
            self.ax1.add_patch(mpatches.Rectangle((mesh.x_min, mesh.y_min), mesh.length, mesh.width, fill=False, color="blue"))
            self.ax2.add_patch(mpatches.Rectangle((mesh.x_min, mesh.z_min), mesh.length, mesh.height, fill=False, color="blue"))
            self.ax3.add_patch(mpatches.Rectangle((mesh.y_min, mesh.z_min), mesh.width, mesh.height, fill=False, color="blue", label='Mesh'))
            drawRectangle(self.ax0, mesh.x_min + mesh.length / 2, mesh.y_min + mesh.width / 2, mesh.z_min + mesh.height / 2, mesh.length, mesh.width, mesh.height, "blue")

        # Detector
        for detector in self.detectors:
            linewidth = 1 if detector.axis in {"x_plane", "y_plane", "z_plane", "3D"} else 5
            if detector.axis != "point":
                # x_line, y_line, z_line, x_plane, y_plane, z_plane
                self.ax1.add_patch(mpatches.Rectangle((detector.x - detector.length / 2, detector.y - detector.width / 2), detector.length, detector.width, fill=True, color="green", alpha=0.5, linewidth=linewidth))
                self.ax2.add_patch(mpatches.Rectangle((detector.x - detector.length / 2, detector.z - detector.height / 2), detector.length, detector.height, fill=True, color="green", alpha=0.5, linewidth=linewidth))
                self.ax3.add_patch(mpatches.Rectangle((detector.y - detector.width / 2, detector.z - detector.height / 2), detector.width, detector.height, fill=True, color="green", alpha=0.5, label='Detector', linewidth=linewidth))
                if detector.axis in {"x_plane", "y_plane", "z_plane"}:
                    drawPlane(self.ax0, detector.axis, detector.x, detector.y, detector.z, detector.length, detector.width, detector.height, "green", alpha=0.5)
                elif detector.axis in {"x_line", "y_line", "z_line"}:
                    self.ax0.plot((detector.x - detector.length / 2, detector.x + detector.length / 2), (detector.y - detector.width / 2, detector.y + detector.width / 2), (detector.z - detector.height / 2, detector.z + detector.height / 2), linewidth=linewidth, color="green")
                elif detector.axis == "3D":
                    drawRectangle(self.ax0, detector.x, detector.y, detector.z, detector.length, detector.width, detector.height, "green", linewidth=linewidth, fill=True, alpha=0.5)
            else:
                # point
                self.ax1.scatter(detector.x, detector.y, linewidth=linewidth, color="green")
                self.ax2.scatter(detector.x, detector.z, linewidth=linewidth, color="green")
                self.ax3.scatter(detector.y, detector.z, linewidth=linewidth, color="green", label='Detector')
                self.ax0.scatter(detector.x, detector.y, detector.z, linewidth=5, color="green")
        

        self.fig.legend()
        self.ax0.grid()
        self.ax1.grid()
        self.ax2.grid()
        self.ax3.grid()
        plt.show()


    # 辅助显示ObjectTree
    def _showObject(self, object):
        if object.type == "ObjectGroup":
            for object_ in object.objects:
                self._showObject(object_)
        else:
            if object.type == "Rectangle":
                self.ax1.add_patch(mpatches.Rectangle((object.x_min, object.y_min), object.length, object.width, fill=True, color=object.color, alpha = 0.5))
                self.ax2.add_patch(mpatches.Rectangle((object.x_min, object.z_min), object.length, object.height, fill=True, color=object.color, alpha = 0.5))
                self.ax3.add_patch(mpatches.Rectangle((object.y_min, object.z_min), object.width, object.height, fill=True, color=object.color, alpha = 0.5, label='Object'))
                drawRectangle(self.ax0, object.x, object.y, object.z, object.length, object.width, object.height, object.color, 1, True, 0.5)


    # 辅助运行时读取ObjectTree
    def _runAddObject(self, object, eps, domain):
        if object.type == "ObjectGroup":
            for object_ in object.objects:
                self._runAddObject(object_, eps, domain)
        else:
            if object.type == "Rectangle" and object.material == "Constant":
                x_center = object.x_min + object.length / 2
                y_center = object.y_min + object.width / 2
                z_center = object.z_min + object.height / 2

                xs, xe = self._grid_range(x_center, object.length / 2,
                                          self.region.x_min, domain.res, domain.length)      # ← 数组长度
                ys, ye = self._grid_range(y_center, object.width / 2,
                                          self.region.y_min, domain.res, domain.width)       # ← 数组长度
                zs, ze = self._grid_range(z_center, object.height / 2,
                                          self.region.z_min, domain.res, domain.height)      # ← 数组长度

                # _grid_range 返回的 xe/ye/ze 是包含的最后一个索引，
                # 因此切片终点需 +1 以包含该点。
                # 原 eps[xs:xe+1, ys:ye+1, zs:ze+1] = object.index ** 2
                if hasattr(domain, 'global_to_local_range'):
                    x_local = domain.global_to_local_range(xs, xe)
                    if x_local is not None:
                        lxs, lxe = x_local
                        eps[lxs:lxe+1, ys:ye+1, zs:ze+1] = object.index ** 2
                else:
                    eps[xs:xe+1, ys:ye+1, zs:ze+1] = object.index ** 2

    # 辅助运行时读取各部件位置
    def _runSetPosition(self, component, domain):
        component.temp_x_start, component.temp_x_end = self._grid_range(
            component.x, component.length/2, self.region.x_min, domain.res, domain.length)
        component.temp_y_start, component.temp_y_end = self._grid_range(
            component.y, component.width/2, self.region.y_min, domain.res, domain.width)
        component.temp_z_start, component.temp_z_end = self._grid_range(
            component.z, component.height/2, self.region.z_min, domain.res, domain.height)

    # 处理边界裁剪
    def _grid_range(self, center, half_size, axis_min, res, max_index):
        start = int((center - half_size - axis_min) / res)
        end   = int((center + half_size - axis_min) / res)
        start = max(0, start)
        end   = min(max_index - 1, end)
        return start, end

    # 处理探测器数组转换
    def _extract_movie_frame(self, detector, fields, xp):
        """提取探测器切片并转换为 shape=(1, H, W) 的 NumPy 数组"""
        xs, xe = detector.temp_x_start, detector.temp_x_end
        ys, ye = detector.temp_y_start, detector.temp_y_end
        zs, ze = detector.temp_z_start, detector.temp_z_end

        if detector.axis == 'x_plane':
            slice_xp = fields[detector.field_component][xs, ys:ye+1, zs:ze+1]
        elif detector.axis == 'y_plane':
            slice_xp = fields[detector.field_component][xs:xe+1, ys, zs:ze+1]
        elif detector.axis == 'z_plane':
            slice_xp = fields[detector.field_component][xs:xe+1, ys:ye+1, zs]
        else:
            slice_xp = fields[detector.field_component][xs:xe+1, ys:ye+1, zs:ze+1]

        frame_np = _to_numpy(slice_xp.T, xp)
        frame_np = np.flipud(frame_np)
        return np.expand_dims(frame_np, axis=0).copy()

    # 源预处理
    def _prepare_sources(self, domain, dt, Nt):
        sources_data = []
        for src in self.sources:
            if src.type != "GaussianSource":
                continue
            
            # 计算网格索引
            xs, xe = src.temp_x_start, src.temp_x_end
            ys, ye = src.temp_y_start, src.temp_y_end
            zs, ze = src.temp_z_start, src.temp_z_end
    
            # 相邻面切片
            shift = 1 if src.direction == "Backward" else -1
            if src.axis == 'x_plane':
                adj_slice = (slice(xs + shift, xe + shift + 1),
                             slice(ys, ye + 1), slice(zs, ze + 1))
                main_slice = (xs, slice(ys, ye + 1), slice(zs, ze + 1))
            elif src.axis == 'y_plane':
                adj_slice = (slice(xs, xe + 1),
                             slice(ys + shift, ye + shift + 1), slice(zs, ze + 1))
                main_slice = (slice(xs, xe + 1), ys, slice(zs, ze + 1))
            else:  # z_plane
                adj_slice = (slice(xs, xe + 1), slice(ys, ye + 1),
                             slice(zs + shift, ze + shift + 1))
                main_slice = (slice(xs, xe + 1), slice(ys, ye + 1), zs)
    
            cos_pol = math.cos(src.polarization_angle)
            sin_pol = math.sin(src.polarization_angle)
            dir_sign = -1 if src.direction == "Backward" else 1
    
            sources_data.append({
                'axis': src.axis,
                'pulse_seq': src.space_gaussian_pulse,   # 已预先生成的空间高斯脉冲列表
                'main_slice': main_slice,
                'adj_slice': adj_slice,
                'cos_pol': cos_pol,
                'sin_pol': sin_pol,
                'dir_sign': dir_sign,
            })
        return sources_data

    # 探测器预处理
    def _prepare_detectors(self, domain, dt):
        detectors_data = []
        for det in self.detectors:
            xs, xe = det.temp_x_start, det.temp_x_end
            ys, ye = det.temp_y_start, det.temp_y_end
            zs, ze = det.temp_z_start, det.temp_z_end

            if det.type == "PointDetector":
                detectors_data.append({
                    'obj': det,
                    'point_index': (xs, ys, zs),
                    'field': det.field_component,
                })
            else:  # MovieDetector 等
                if det.type == "MovieDetector":
                    if det.axis == 'x_plane':
                        idx = (xs, slice(ys, ye + 1), slice(zs, ze + 1))
                    elif det.axis == 'y_plane':
                        idx = (slice(xs, xe + 1), ys, slice(zs, ze + 1))
                    elif det.axis == 'z_plane':
                        idx = (slice(xs, xe + 1), slice(ys, ye + 1), zs)
                    else:
                        idx = (slice(xs, xe + 1), slice(ys, ye + 1), slice(zs, ze + 1))
                else:
                    idx = (slice(xs, xe + 1), slice(ys, ye + 1), slice(zs, ze + 1))

                detectors_data.append({
                    'obj': det,
                    'slice': idx,
                    'field': det.field_component,
                })
        return detectors_data

    # 处理探测器数组转换（并行）
    def _extract_movie_frame_from_slice(self, local_slice, field_name, fields, xp):
        """根据本地切片从 fields 中提取帧并转换为 NumPy (1,H,W) 数组"""
        slice_xp = fields[field_name][local_slice]
        frame_np = _to_numpy(slice_xp.T, xp)
        frame_np = np.flipud(frame_np)
        return np.expand_dims(frame_np, axis=0).copy()

    # 并行运行
    def run_mpi(self):
        # MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()

        # 设置仿真空间参数
        run_length = int(self.region.length / self.region.res + 1)
        run_width = int(self.region.width / self.region.res + 1)
        run_height = int(self.region.height / self.region.res + 1)
        res = self.region.res
        boundary_layers = self.region.boundary_layers


        domain = MPIDomain(run_length, run_width, run_height, res, boundary_layers, comm)


        if self.region.simulation_time == 0:
            Nt = 10000
            mode = 1 # 自动结束
        else:
            Nt = int(self.region.simulation_time / self.region.step_time)
            mode = 0
        dt = self.region.step_time
        dt_max = res / (math.sqrt(3) * c)
        step = 0
        print_interval = max(1, Nt // 50)   # 约2%进度更新一次
        boundary_type = self.region.boundary
        
        pml_sigma_d = 1.0
        if boundary_type == "PML":
            pml_sigma = self.region.boundary_sigma
            pml_sigma_d = xp.exp(-pml_sigma * dt)


        # 打印参数
        if rank == 0:
            print("Parameter table : ")
            print("run_length : " + str(domain.length))
            print("run_width : " + str(domain.width))
            print("run_height : " + str(domain.height))
            print("res : " + str(domain.res))
            print("Nt : " + str(Nt))
            print("dt : " + str(dt))
            print("dt_max : " + str(dt_max))
            print("boundary_type : " + boundary_type)
            print("boundary_layers : " + str(domain.boundary_layers))
            if boundary_type == "PML":
                print("pml_sigma : " + str(pml_sigma))
            if mode == 1:
                print("Mode : Automatic Mode.\nThe progress bar does not need to be completed.")
        if dt > dt_max:
            print("TIME STEP IS TOO LONG!")
            return


        nx, ny, nz = domain.local_size
        size = (nx + 2, ny, nz)


        # 设置初值
        size = domain.local_size
        eps   = xp.ones(size)
        mu    = xp.ones(size)
        sigma = xp.zeros(size)
        Ex = xp.zeros(size)
        Ey = xp.zeros(size)
        Ez = xp.zeros(size)
        Hx = xp.zeros(size)
        Hy = xp.zeros(size)
        Hz = xp.zeros(size)

        

        # 添加模型
        for object in self.objectTree:
            self._runAddObject(object, eps, domain)

        # 源预处理（生成本地化脉冲）
        max_ = 0.0
        all_sources_info = []   # 临时存储全局信息
        for src in self.sources:
            if src.type == "GaussianSource":
                t_ = np.arange(-int(src.offset / dt), Nt - int(src.offset / dt)) * dt
                src.gaussian_pulse = src.amplitude * gausspulse(t_, fc=src.frequency_center, bw=src.pulse_width_FWHM)
                if src.direction == "Forward":
                    src.gaussian_pulse *= -1

                pulse_abs = float(np.max(np.abs(src.gaussian_pulse)))
                if pulse_abs > max_:
                    max_ = pulse_abs

                self._runSetPosition(src, domain)   # 计算全局索引
                all_sources_info.append(src)

        min_ = 0.1 * max_

        # 二次处理：本地化源切片并生成空间脉冲
        sources_data = []
        for src in all_sources_info:
            xs, xe = src.temp_x_start, src.temp_x_end
            ys, ye = src.temp_y_start, src.temp_y_end
            zs, ze = src.temp_z_start, src.temp_z_end

            shift = 1 if src.direction == "Backward" else -1
            if src.axis == 'x_plane':
                glob_main = (xs, slice(ys, ye+1), slice(zs, ze+1))
                glob_adj  = (xs + shift, slice(ys, ye+1), slice(zs, ze+1))
            elif src.axis == 'y_plane':
                glob_main = (slice(xs, xe+1), ys, slice(zs, ze+1))
                glob_adj  = (slice(xs, xe+1), ys + shift, slice(zs, ze+1))
            else:  # z_plane
                glob_main = (slice(xs, xe+1), slice(ys, ye+1), zs)
                glob_adj  = (slice(xs, xe+1), slice(ys, ye+1), zs + shift)


            local_main = domain.localize_slice(glob_main)
            local_adj  = domain.localize_slice(glob_adj)
            if local_main is None:   # 源不在本进程，跳过
                continue


            # 通过任意一个场数组（如 Ey）获取本地切片形状，确保脉冲尺寸严格匹配
            slice_shape = Ey[local_main].shape   # 平面源会得到 (ny, nz) 或 (nx, nz) 等二维形状

            # 根据源轴构造 create_3d_gaussian 需要的三维尺寸（厚度方向置1）
            if src.axis == 'x_plane':
                size_3d = (1, slice_shape[0], slice_shape[1])      # (1, ny, nz)
            elif src.axis == 'y_plane':
                size_3d = (slice_shape[0], 1, slice_shape[1])      # (nx, 1, nz)
            else:  # z_plane
                size_3d = (slice_shape[0], slice_shape[1], 1)      # (nx, ny, 1)

            local_pulse_seq = []
            for val in src.gaussian_pulse:
                gauss = create_3d_gaussian(
                    size_3d,
                    sigma=src.space_sigma, res=domain.res, xp_backend=xp
                )
                local_pulse_seq.append(val * gauss)

            cos_pol = math.cos(src.polarization_angle)
            sin_pol = math.sin(src.polarization_angle)
            dir_sign = -1 if src.direction == "Backward" else 1

            sources_data.append({
                'axis': src.axis,
                'pulse_seq': local_pulse_seq,
                'main_slice': local_main,
                'adj_slice': local_adj,
                'cos_pol': cos_pol,
                'sin_pol': sin_pol,
                'dir_sign': dir_sign,
            })

        # 探测器预处理
        fields = {'Ex': Ex, 'Ey': Ey, 'Ez': Ez, 'Hx': Hx, 'Hy': Hy, 'Hz': Hz}
        detectors_data = []
        for det in self.detectors:
            self._runSetPosition(det, domain)   # 全局索引
            if det.type == "MovieDetector":
                xs, xe = det.temp_x_start, det.temp_x_end
                ys, ye = det.temp_y_start, det.temp_y_end
                zs, ze = det.temp_z_start, det.temp_z_end
                if det.axis == 'x_plane':
                    glob_slice = (xs, slice(ys, ye+1), slice(zs, ze+1))
                elif det.axis == 'y_plane':
                    glob_slice = (slice(xs, xe+1), ys, slice(zs, ze+1))
                elif det.axis == 'z_plane':
                    glob_slice = (slice(xs, xe+1), slice(ys, ye+1), zs)
                else:
                    glob_slice = (slice(xs, xe+1), slice(ys, ye+1), slice(zs, ze+1))


                local_slice = domain.localize_slice(glob_slice)
                if local_slice is None:
                    continue


                # 初始化第一帧
                det.data = self._extract_movie_frame_from_slice(local_slice, det.field_component, fields, xp)
                detectors_data.append({
                    'obj': det,
                    'slice': local_slice,
                    'field': det.field_component,
                })
            elif det.type == "PointDetector":
                gx, gy, gz = det.temp_x_start, det.temp_y_start, det.temp_z_start

                local_pt = domain.global_to_local(gx, gy, gz)
                if local_pt is None:
                    continue
                lx, ly, lz = local_pt

                detectors_data.append({
                    'obj': det,
                    'point_index': (lx, ly, lz),
                    'field': det.field_component,
                })

        # 设置计算参数
        # step_NA_temp = 1 - (2 * sigma[1:-1, 1:-1, 1:-1] * dt) / (2 * eps[1:-1, 1:-1, 1:-1] * eps0 + sigma[1:-1, 1:-1, 1:-1] * dt)
        # step_NB_temp = dt / res / (eps[1:-1, 1:-1, 1:-1] * eps0 + 0.5 * sigma[1:-1, 1:-1, 1:-1] * dt)
        # step_NC_temp = 1 - (2 * sigma[1:-1, 1:-1, 1:-1] * dt) / (2 * mu[1:-1, 1:-1, 1:-1] * mu0 + sigma[1:-1, 1:-1, 1:-1] * dt)
        # step_ND_temp = dt / res / (mu[1:-1, 1:-1, 1:-1] * mu0 + 0.5 * sigma[1:-1, 1:-1, 1:-1] * dt)
        step_NA_temp = 1
        step_NB_temp = dt / domain.res / (eps[1:-1, 1:-1, 1:-1] * eps0)
        step_NC_temp = 1
        step_ND_temp = - dt / domain.res / (mu[1:-1, 1:-1, 1:-1] * mu0)


        # 主循环
        kernel = MPIKernel(xp, comm, domain)

        start_time = time.time()
        while True:
            # 源注入
            for src in sources_data:
                pulse = src['pulse_seq'][step]
                if src['axis'] == 'x_plane':
                    Ey[src['main_slice']] = pulse * src['cos_pol']
                    Ez[src['main_slice']] = pulse * src['sin_pol'] * src['dir_sign']
                elif src['axis'] == 'y_plane':
                    Ez[src['main_slice']] = pulse * src['cos_pol']
                    Ex[src['main_slice']] = pulse * src['sin_pol'] * src['dir_sign']
                else:  # z_plane
                    Ex[src['main_slice']] = pulse * src['cos_pol']
                    Ey[src['main_slice']] = pulse * src['sin_pol'] * src['dir_sign']
                # 相邻面清零
                for f in (Ex, Ey, Ez, Hx, Hy, Hz):
                    f[src['adj_slice']] = 0.0

            # 探测器记录
            for d in detectors_data:
                det = d['obj']
                if det.type == "MovieDetector":
                    if step % det.sampling_rate == 0 and d['field'] not in ("E", "H"):
                        frame = self._extract_movie_frame_from_slice(d['slice'], d['field'], fields, xp)
                        det.record(frame)
                elif det.type == "PointDetector":
                    if d['field'] not in ("E", "H"):
                        val = fields[d['field']][d['point_index']]
                        val_float = float(_to_numpy(val, xp).item())
                        det.record(step * dt, val_float)

            # 电磁场布进
            kernel.fdtd_step(Ex, Ey, Ez, Hx, Hy, Hz, step_NA_temp, step_NB_temp, step_NC_temp, step_ND_temp)

            # 边界条件
            if boundary_type == "PML":
                kernel.pml_step(Ex, Ey, Ez, Hx, Hy, Hz, domain.boundary_layers, pml_sigma_d)

            # 进度条（每约2%进度更新一次）
            if rank == 0:
                if step % print_interval == 0 or step >= Nt - 1:
                    bar_length = min(50, int(50 * (step + 1) / Nt))
                    bar = '#' * bar_length + '-' * (50 - bar_length)
                    pct = int((step + 1) / Nt * 100)
                    print(f'\r[{bar}] {pct}%', end='', flush=True)

            # 循环判定
            step += 1
            if step >= Nt:
                print("\nDone.")
                print("step = " + str(step))
                print("simulation_time = " + str(step * dt))
                break
            if mode == 1:
                # 自动停止判断：MPI 需全局归约
                local_max = float(xp.max(xp.abs(Ez[1:-1, :, :])).item())
                global_max = comm.allreduce(local_max, op=MPI.MAX)

                if global_max > max_ * 10:
                    if rank == 0:
                        print("\nDivergent.")
                        print("step = " + str(step))
                        print("simulation_time = " + str(step * dt))
                    break
                elif global_max < min_ and step > 1000:
                    if rank == 0:
                        print("\nAuto Done.")
                        print("step = " + str(step))
                        print("simulation_time = " + str(step * dt))
                    break

        # ---------- 合并保存探测器数据 ----------
        for det in self.detectors:
            if det.type == "MovieDetector":
                if det.data is not None and det.data.size > 0:
                    # 传递本地数据及其全局 x 起始坐标、实际本地 x 宽度
                    local_info = (domain.x_start, det.data)
                else:
                    local_info = None
            elif det.type == "PointDetector":
                if len(det.data) > 0:
                    local_info = (det.t, det.data)
                else:
                    local_info = None
            else:
                continue

            all_info = comm.gather(local_info, root=0)

            if rank == 0:
                if det.type == "MovieDetector":
                    valid = [info for info in all_info if info is not None]
                    if not valid:
                        continue

                    # 按全局 x_start 排序，保证拼接顺序
                    valid.sort(key=lambda x: x[0])
                    sample_frame = valid[0][1][0]   # 第一帧形状 (H, W_local)
                    frame_height = sample_frame.shape[0]
                    num_frames = valid[0][1].shape[0]

                    if det.axis in ('y_plane', 'z_plane', 'x_line', '3D'):
                        # 全局 x 点数直接使用 domain.length
                        global_nx = domain.length
                        merged = np.zeros((num_frames, frame_height, global_nx),
                                          dtype=sample_frame.dtype)
                        for gx_start, data in valid:
                            w = data.shape[2]          # 实际本地 x 宽度
                            merged[:, :, gx_start:gx_start + w] = data
                        det.data = merged
                    else:  # x_plane 等
                        det.data = valid[0][1]

                    det.save()

                elif det.type == "PointDetector":
                    all_pts = [info for info in all_info if info is not None]
                    if not all_pts:
                        continue
                    merged_t, merged_val = [], []
                    for t_list, val_list in all_pts:
                        merged_t.extend(t_list)
                        merged_val.extend(val_list)
                    sorted_idx = np.argsort(merged_t)
                    det.t = list(np.array(merged_t)[sorted_idx])
                    det.data = list(np.array(merged_val)[sorted_idx])
                    det.save()
                    
        if rank == 0:
            print("cost_time = " + str(time.time() - start_time) + "s")

    # 串行运行
    def run(self):
        # 设置仿真空间参数
        run_length = int(self.region.length / self.region.res + 1)
        run_width = int(self.region.width / self.region.res + 1)
        run_height = int(self.region.height / self.region.res + 1)
        res = self.region.res
        if self.region.simulation_time == 0:
            Nt = 10000
            mode = 1 # 自动结束
        else:
            Nt = int(self.region.simulation_time / self.region.step_time)
            mode = 0
        dt = self.region.step_time
        dt_max = res / 1.7320508  / c
        step = 0
        print_interval = max(1, Nt // 50)   # 约2%进度更新一次
        boundary_type = self.region.boundary
        boundary_layers = self.region.boundary_layers
        if boundary_type == "PML":
            pml_sigma = self.region.boundary_sigma
            pml_sigma_d = xp.exp(-pml_sigma * dt)
        domain = Domain(run_length, run_width, run_height, res, boundary_layers)


        # 打印参数
        print("Parameter table : ")
        print("run_length : " + str(domain.length))
        print("run_width : " + str(domain.width))
        print("run_height : " + str(domain.height))
        print("res : " + str(domain.res))
        print("Nt : " + str(Nt))
        print("dt : " + str(dt))
        print("dt_max : " + str(dt_max))
        print("boundary_type : " + boundary_type)
        print("boundary_layers : " + str(domain.boundary_layers))
        if boundary_type == "PML":
            print("pml_sigma : " + str(pml_sigma))
        if mode == 1:
            print("Mode : Automatic Mode.\nThe progress bar does not need to be completed.")
        if dt > dt_max:
            print("TIME STEP IS TOO LONG!")
            return

        # 设置初值
        size = domain.local_size
        eps   = xp.ones(size)
        mu    = xp.ones(size)
        sigma = xp.zeros(size)
        Ex = xp.zeros(size)
        Ey = xp.zeros(size)
        Ez = xp.zeros(size)
        Hx = xp.zeros(size)
        Hy = xp.zeros(size)
        Hz = xp.zeros(size)

        

        # 添加模型
        for object in self.objectTree:
            self._runAddObject(object, eps, domain)

        # 设置源运行参数
        max_ = 0.0
        for src in self.sources:
            if src.type == "GaussianSource":
                t_ = np.arange(-int(src.offset / dt), Nt - int(src.offset / dt)) * dt
                src.gaussian_pulse = src.amplitude * gausspulse(t_, fc=src.frequency_center, bw=src.pulse_width_FWHM)
                if src.direction == "Forward":
                    src.gaussian_pulse *= -1

                pulse_abs = float(np.max(np.abs(src.gaussian_pulse)))
                if pulse_abs > max_:
                    max_ = pulse_abs

                self._runSetPosition(src, domain)
                src.space_gaussian_pulse = [
                    val * create_3d_gaussian((src.temp_x_end - src.temp_x_start + 1,
                                              src.temp_y_end - src.temp_y_start + 1,
                                              src.temp_z_end - src.temp_z_start + 1),
                                             sigma=src.space_sigma, res=domain.res, xp_backend=xp)
                    for val in src.gaussian_pulse
                ]

        min_ = 0.1 * max_
        sources_data = self._prepare_sources(domain, dt, Nt)

        # 设置探测器参数
        fields = {'Ex': Ex, 'Ey': Ey, 'Ez': Ez, 'Hx': Hx, 'Hy': Hy, 'Hz': Hz}
        for det in self.detectors:
            self._runSetPosition(det, domain)
            if det.type == "MovieDetector":
                det.data = self._extract_movie_frame(det, fields, xp)
        detectors_data = self._prepare_detectors(domain, dt)


        # 设置计算参数
        # step_NA_temp = 1 - (2 * sigma[1:-1, 1:-1, 1:-1] * dt) / (2 * eps[1:-1, 1:-1, 1:-1] * eps0 + sigma[1:-1, 1:-1, 1:-1] * dt)
        # step_NB_temp = dt / res / (eps[1:-1, 1:-1, 1:-1] * eps0 + 0.5 * sigma[1:-1, 1:-1, 1:-1] * dt)
        # step_NC_temp = 1 - (2 * sigma[1:-1, 1:-1, 1:-1] * dt) / (2 * mu[1:-1, 1:-1, 1:-1] * mu0 + sigma[1:-1, 1:-1, 1:-1] * dt)
        # step_ND_temp = dt / res / (mu[1:-1, 1:-1, 1:-1] * mu0 + 0.5 * sigma[1:-1, 1:-1, 1:-1] * dt)
        step_NA_temp = 1
        step_NB_temp = dt / domain.res / (eps[1:-1, 1:-1, 1:-1] * eps0)
        step_NC_temp = 1
        step_ND_temp = - dt / domain.res / (mu[1:-1, 1:-1, 1:-1] * mu0)


        # 主循环
        start_time = time.time()
        kernel = FDTDKernel(xp)
        while True:
            # 源注入
            for src in sources_data:
                pulse = src['pulse_seq'][step]
                if src['axis'] == 'x_plane':
                    Ey[src['main_slice']] = pulse * src['cos_pol']
                    Ez[src['main_slice']] = pulse * src['sin_pol'] * src['dir_sign']
                elif src['axis'] == 'y_plane':
                    Ez[src['main_slice']] = pulse * src['cos_pol']
                    Ex[src['main_slice']] = pulse * src['sin_pol'] * src['dir_sign']
                else:  # z_plane
                    Ex[src['main_slice']] = pulse * src['cos_pol']
                    Ey[src['main_slice']] = pulse * src['sin_pol'] * src['dir_sign']
                # 相邻面清零
                for f in (Ex, Ey, Ez, Hx, Hy, Hz):
                    f[src['adj_slice']] = 0.0

            # 探测器记录
            for d in detectors_data:
                det = d['obj']
                if det.type == "MovieDetector":
                    if step % det.sampling_rate == 0 and d['field'] not in ("E", "H"):
                        frame = self._extract_movie_frame(det, fields, xp)
                        det.record(frame)
                elif det.type == "PointDetector":
                    if d['field'] not in ("E", "H"):
                        val = fields[d['field']][d['point_index']]
                        val_float = float(_to_numpy(val, xp).item())
                        det.record(step * dt, val_float)

            # 电磁场布进
            kernel.fdtd_step(Ex, Ey, Ez, Hx, Hy, Hz, step_NA_temp, step_NB_temp, step_NC_temp, step_ND_temp)

            # 边界条件
            if boundary_type == "PML":
                kernel.pml_step(Ex, Ey, Ez, Hx, Hy, Hz, domain.boundary_layers, pml_sigma_d)

            # 进度条（每约2%进度更新一次）
            if step % print_interval == 0 or step >= Nt - 1:
                bar_length = min(50, int(50 * (step + 1) / Nt))
                bar = '#' * bar_length + '-' * (50 - bar_length)
                pct = int((step + 1) / Nt * 100)
                print(f'\r[{bar}] {pct}%', end='', flush=True)

            # 循环判定
            step += 1
            if step >= Nt:
                print("\nDone.")
                print("step = " + str(step))
                print("simulation_time = " + str(step * dt))
                print("cost_time = " + str(time.time() - start_time) + "s")
                for detector in self.detectors:
                    detector.save()
                break
            elif mode == 1:
                if (xp.max(xp.abs(Ez)) > max_ * 10):
                    print("\nDivergent.")
                    print("step = " + str(step))
                    print("simulation_time = " + str(step * dt))
                    print("cost_time = " + str(time.time() - start_time) + "s")
                    for detector in self.detectors:
                        detector.save()
                    break
                elif (xp.max(xp.abs(Ez)) < min_ and step > 1000):
                    print("\nAuto Done.")
                    print("step = " + str(step))
                    print("simulation_time = " + str(step * dt))
                    print("cost_time = " + str(time.time() - start_time) + "s")
                    for detector in self.detectors:
                        detector.save()
                    break

def drawRectangle(ax, x, y, z, l, w, h, color, linewidth=1, fill=False, alpha=1):
    canvas_temp = mpatches.Rectangle((x - l / 2, y - w / 2), l, w, fill=fill, color=color, linewidth=linewidth, alpha=alpha)
    ax.add_patch(canvas_temp)
    art3d.pathpatch_2d_to_3d(canvas_temp, z=z - h / 2, zdir='z')
    canvas_temp = mpatches.Rectangle((x - l / 2, y - w/ 2), l, w, fill=fill, color=color, linewidth=linewidth, alpha=alpha)
    ax.add_patch(canvas_temp)
    art3d.pathpatch_2d_to_3d(canvas_temp, z=z + h/ 2, zdir='z')
    canvas_temp = mpatches.Rectangle((x - l / 2, z - h/ 2), l, h, fill=fill, color=color, linewidth=linewidth, alpha=alpha)
    ax.add_patch(canvas_temp)
    art3d.pathpatch_2d_to_3d(canvas_temp, z=y - w/ 2, zdir='y')
    canvas_temp = mpatches.Rectangle((x - l / 2, z - h/ 2), l, h, fill=fill, color=color, linewidth=linewidth, alpha=alpha)
    ax.add_patch(canvas_temp)
    art3d.pathpatch_2d_to_3d(canvas_temp, z=y + w/ 2, zdir='y')
    canvas_temp = mpatches.Rectangle((y - w/ 2, z - h/ 2), w, h, fill=fill, color=color, linewidth=linewidth, alpha=alpha)
    ax.add_patch(canvas_temp)
    art3d.pathpatch_2d_to_3d(canvas_temp, z=x - l / 2, zdir='x')
    canvas_temp = mpatches.Rectangle((y - w/ 2, z - h/ 2), w, h, fill=fill, color=color, linewidth=linewidth, alpha=alpha)
    ax.add_patch(canvas_temp)
    art3d.pathpatch_2d_to_3d(canvas_temp, z=x + l / 2, zdir='x')

def drawPlane(ax, axis, x, y, z, l, w, h, color, fill=True, linewidth=1, alpha=1, direction=None):
    l_min = min(l, w, h)
    if axis == 'x_plane':
        canvas_temp = mpatches.Rectangle((y - w / 2, z - h / 2), w, h, fill=fill, color=color, linewidth=linewidth, alpha=alpha)
        ax.add_patch(canvas_temp)
        art3d.pathpatch_2d_to_3d(canvas_temp, z=x, zdir="x")
        if direction == "Forward":
            canvas_temp = mpatches.Arrow(x, y, l_min / 5, 0, color=color, linewidth=linewidth, alpha=alpha)
            ax.add_patch(canvas_temp)
            art3d.pathpatch_2d_to_3d(canvas_temp, z=z, zdir="z")
        elif direction == "Backward":
            canvas_temp = mpatches.Arrow(x, y, -l_min / 5, 0, color=color, linewidth=linewidth, alpha=alpha)
            ax.add_patch(canvas_temp)
            art3d.pathpatch_2d_to_3d(canvas_temp, z=z, zdir="z")
    elif axis == 'y_plane':
        canvas_temp = mpatches.Rectangle((x - l / 2, z - h / 2), l, h, fill=fill, color=color, linewidth=linewidth, alpha=alpha)
        ax.add_patch(canvas_temp)
        art3d.pathpatch_2d_to_3d(canvas_temp, z=y, zdir="y")
        if direction == "Forward":
            canvas_temp = mpatches.Arrow(y, z, l_min / 5, 0, color=color, linewidth=linewidth, alpha=alpha)
            ax.add_patch(canvas_temp)
            art3d.pathpatch_2d_to_3d(canvas_temp, z=x, zdir="x")
        elif direction == "Backward":
            canvas_temp = mpatches.Arrow(y, z, -1 / 5, 0, color=color, linewidth=linewidth, alpha=alpha)
            ax.add_patch(canvas_temp)
            art3d.pathpatch_2d_to_3d(canvas_temp, z=x, zdir="x")
    elif axis == 'z_plane':
        canvas_temp = mpatches.Rectangle((x - l / 2, y - w / 2), l, w, fill=fill, color=color, linewidth=linewidth, alpha=alpha)
        ax.add_patch(canvas_temp)
        art3d.pathpatch_2d_to_3d(canvas_temp, z=z, zdir="z")
        if direction == "Forward":
            canvas_temp = mpatches.Arrow(x, z, 0, l_min / 5, color=color, linewidth=linewidth, alpha=alpha)
            ax.add_patch(canvas_temp)
            art3d.pathpatch_2d_to_3d(canvas_temp, z=y, zdir="y")
        elif direction == "Backward":
            canvas_temp = mpatches.Arrow(x, z, 0, -l_min / 5, color=color, linewidth=linewidth, alpha=alpha)
            ax.add_patch(canvas_temp)
            art3d.pathpatch_2d_to_3d(canvas_temp, z=y, zdir="y")

def _to_numpy(arr, xp):
    """将 xp 数组安全转换为 NumPy 数组"""
    if hasattr(arr, 'get'):        # cupy
        return arr.get()
    return np.asarray(arr)         # numpy