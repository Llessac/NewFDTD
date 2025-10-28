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
from os import path
# import numba
import time

from .mathTool import *
from .grid import *
from .object import *
from .source import *
from .detector import *




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

        print(name)
        name = name.strip()
        if ":" in name:
            with open(name, "w") as f:
                f.write(json.dumps(saveCache))
                print("***")
        else:
            if ".json" in name:
                name = name.replace(".json", "")
            with open(path.dirname(path.dirname(__file__)) + "\\emulation\\" + name + ".json", 'w') as f:
                f.write(json.dumps(saveCache))

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
    def _runAddObject(self, object, eps):
        if object.type == "ObjectGroup":
            for object_ in object.objects:
                self._runAddObject(object_, eps)
        else:
            if object.type == "Rectangle":
                if object.material == "Constant":
                    start_x = int((object.x_min - self.region.x_min) / self.region.res)
                    end_x = int((object.x_min - self.region.x_min + object.length) / self.region.res)
                    start_y = int((object.y_min - self.region.y_min) / self.region.res)
                    end_y = int((object.y_min - self.region.y_min + object.width) / self.region.res)
                    start_z = int((object.z_min - self.region.z_min) / self.region.res)
                    end_z = int((object.z_min - self.region.z_min + object.height) / self.region.res)
                    eps[start_x:end_x, start_y:end_y, start_z:end_z] = object.index ** 2

    # 辅助运行时读取各部件位置
    def _runSetPosition(self, component, run_length, run_width, run_height, res):
        component.temp_x_start = int((component.x - component.length / 2 - self.region.x_min) / res)
        if component.temp_x_start < 0:
            component.temp_x_start = 0
        component.temp_x_end = int((component.x + component.length / 2 - self.region.x_min) / res)
        if component.temp_x_end > run_length - 1:
            component.temp_x_end = run_length - 1
        component.temp_y_start = int((component.y - component.width / 2 - self.region.y_min) / res)
        if component.temp_y_start < 0:
            component.temp_y_start = 0
        component.temp_y_end = int((component.y + component.width / 2 - self.region.y_min) / res)
        if component.temp_y_end > run_height - 1:
            component.temp_y_end = run_width - 1
        component.temp_z_start = int((component.z - component.height / 2 - self.region.z_min) / res)
        if component.temp_z_start < 0:
            component.temp_z_start = 0
        component.temp_z_end = int((component.z + component.height / 2 - self.region.z_min) / res)
        if component.temp_z_end > run_length - 1:
            component.temp_z_end = run_height - 1


    # 运行
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
        max_ = 0
        min_ = 0
        boundary_type = self.region.boundary
        boundary_layers = self.region.boundary_layers
        if boundary_type == "PML":
            pml_sigma = self.region.boundary_sigma
            pml_sigma_d = np.exp(-pml_sigma * dt)

        # t = np.arange(0, Nt) * dt  # 时间轴
        t = [i * dt for i in range(Nt)]

        # 打印参数
        print("Parameter table : ")
        print("run_length : " + str(run_length))
        print("run_width : " + str(run_width))
        print("run_height : " + str(run_height))
        print("res : " + str(res))
        print("Nt : " + str(Nt))
        print("dt : " + str(dt))
        print("dt_max : " + str(dt_max))
        print("boundary_type : " + boundary_type)
        print("boundary_layers : " + str(boundary_layers))
        if boundary_type == "PML":
            print("pml_sigma : " + str(pml_sigma))
        if mode == 1:
            print("Mode : Auto Mode.\nThe progress bar doesn't have to be complete.")
        if dt > dt_max:
            print("TIME STEP IS TOO LONG!")
            return

        # 设置初值
        eps = np.ones((run_length, run_width, run_height))
        mu = np.ones((run_length, run_width, run_height))
        sigma = np.zeros((run_length, run_width, run_height))
        Ex = np.zeros((run_length, run_width, run_height))
        Ey = np.zeros((run_length, run_width, run_height))
        Ez = np.zeros((run_length, run_width, run_height))
        Hx = np.zeros((run_length, run_width, run_height))
        Hy = np.zeros((run_length, run_width, run_height))
        Hz = np.zeros((run_length, run_width, run_height))

        # 添加模型
        for object in self.objectTree:
            self._runAddObject(object, eps)

        # 设置源运行参数
        for source in self.sources:
            if source.type == "GaussianSource":
                # 高斯脉冲
                t_ = np.arange(- int(source.offset / dt), Nt - int(source.offset / dt)) * dt
                source.gaussian_pulse = source.amplitude * gausspulse(t_, fc=source.frequency_center, bw=source.pulse_width_FWHM)
                if source.direction == "Forward":
                    for i in range(len(source.gaussian_pulse)):
                        source.gaussian_pulse[i] *= -1
                    
                self._runSetPosition(source, run_length, run_width, run_height, res)

                for i in range(len(source.gaussian_pulse)):
                    source.space_gaussian_pulse.append(source.gaussian_pulse[i] * 
                                                       create_3d_gaussian((source.temp_x_end - source.temp_x_start + 1, source.temp_y_end - source.temp_y_start + 1, source.temp_z_end - source.temp_z_start + 1), sigma=source.space_sigma, res=res))
                    # plt.title("space_gaussian_pulse")
                    # plt.imshow(source.space_gaussian_pulse[-1])
                    # plt.show()
                plt.title("gaussian_pulse")
                plt.plot(t, source.gaussian_pulse)
                plt.show()
                max_ = np.max(np.abs(source.gaussian_pulse)) if np.max(np.abs(source.gaussian_pulse)) > max_ else max_
                min_ = 0.1 * max_

        # 探测器设置
        for detector in self.detectors:
            if detector.type == "MovieDetector":
                self._runSetPosition(detector, run_length, run_width, run_height, res)
                if detector.axis == 'x_plane':
                    detector.data = np.expand_dims(np.flipud(locals()[detector.field_component][detector.temp_x_start, detector.temp_y_start:detector.temp_y_end + 1, detector.temp_z_start:detector.temp_z_end + 1].T), axis = 0).copy()
                elif detector.axis == 'y_plane':
                    detector.data = np.expand_dims(np.flipud(locals()[detector.field_component][detector.temp_x_start:detector.temp_x_end + 1, detector.temp_y_start, detector.temp_z_start:detector.temp_z_end + 1].T), axis = 0).copy()
                elif detector.axis == 'z_plane':
                    detector.data = np.expand_dims(np.flipud(locals()[detector.field_component][detector.temp_x_start:detector.temp_x_end + 1, detector.temp_y_start:detector.temp_y_end + 1, detector.temp_z_start].T), axis = 0).copy()
            elif detector.type == "PointDetector":
                self._runSetPosition(detector, run_length, run_width, run_height, res)


        # 计算参数
        # step_NA_temp = 1 - (2 * sigma[1:-1, 1:-1, 1:-1] * dt) / (2 * eps[1:-1, 1:-1, 1:-1] * eps0 + sigma[1:-1, 1:-1, 1:-1] * dt)
        # step_NB_temp = dt / res / (eps[1:-1, 1:-1, 1:-1] * eps0 + 0.5 * sigma[1:-1, 1:-1, 1:-1] * dt)
        # step_NC_temp = 1 - (2 * sigma[1:-1, 1:-1, 1:-1] * dt) / (2 * mu[1:-1, 1:-1, 1:-1] * mu0 + sigma[1:-1, 1:-1, 1:-1] * dt)
        # step_ND_temp = dt / res / (mu[1:-1, 1:-1, 1:-1] * mu0 + 0.5 * sigma[1:-1, 1:-1, 1:-1] * dt)
        step_NA_temp = 1
        step_NB_temp = dt / res / (eps[1:-1, 1:-1, 1:-1] * eps0)
        step_NC_temp = 1
        step_ND_temp = - dt / res / (mu[1:-1, 1:-1, 1:-1] * mu0)


        # 主循环
        while True:
            # 源
            for source in self.sources:
                # 高斯脉冲
                if source.type == "GaussianSource":
                    if source.axis == 'x_plane':
                        Ey[source.temp_x_start, source.temp_y_start:source.temp_y_end + 1, source.temp_z_start:source.temp_z_end + 1] = source.space_gaussian_pulse[step] * math.cos(source.polarization_angle)
                        Ez[source.temp_x_start, source.temp_y_start:source.temp_y_end + 1, source.temp_z_start:source.temp_z_end + 1] = source.space_gaussian_pulse[step] * math.sin(source.polarization_angle) * (-1 if source.direction == "Backward" else 1)
                        Ex[source.temp_x_start + (1 if source.direction == "Backward" else -1), source.temp_y_start:source.temp_y_end + 1, source.temp_z_start:source.temp_z_end + 1] = 0
                        Ey[source.temp_x_start + (1 if source.direction == "Backward" else -1), source.temp_y_start:source.temp_y_end + 1, source.temp_z_start:source.temp_z_end + 1] = 0
                        Ez[source.temp_x_start + (1 if source.direction == "Backward" else -1), source.temp_y_start:source.temp_y_end + 1, source.temp_z_start:source.temp_z_end + 1] = 0
                        Hx[source.temp_x_start + (1 if source.direction == "Backward" else -1), source.temp_y_start:source.temp_y_end + 1, source.temp_z_start:source.temp_z_end + 1] = 0
                        Hy[source.temp_x_start + (1 if source.direction == "Backward" else -1), source.temp_y_start:source.temp_y_end + 1, source.temp_z_start:source.temp_z_end + 1] = 0
                        Hz[source.temp_x_start + (1 if source.direction == "Backward" else -1), source.temp_y_start:source.temp_y_end + 1, source.temp_z_start:source.temp_z_end + 1] = 0
                    elif source.axis == 'y_plane':
                        Ez[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start, source.temp_z_start:source.temp_z_end + 1] = source.space_gaussian_pulse[step] * math.cos(source.polarization_angle)
                        Ex[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start, source.temp_z_start:source.temp_z_end + 1] = source.space_gaussian_pulse[step] * math.sin(source.polarization_angle) * (1 if source.direction == "Backward" else -1)
                        Ex[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start + (1 if source.direction == "Backward" else -1), source.temp_z_start:source.temp_z_end + 1] = 0
                        Ey[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start + (1 if source.direction == "Backward" else -1), source.temp_z_start:source.temp_z_end + 1] = 0
                        Ez[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start + (1 if source.direction == "Backward" else -1), source.temp_z_start:source.temp_z_end + 1] = 0
                        Hx[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start + (1 if source.direction == "Backward" else -1), source.temp_z_start:source.temp_z_end + 1] = 0
                        Hy[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start + (1 if source.direction == "Backward" else -1), source.temp_z_start:source.temp_z_end + 1] = 0
                        Hz[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start + (1 if source.direction == "Backward" else -1), source.temp_z_start:source.temp_z_end + 1] = 0
                    elif source.axis == 'z_plane':
                        Ex[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start:source.temp_y_end + 1, source.temp_z_start] = source.space_gaussian_pulse[step] * math.cos(source.polarization_angle)
                        Ey[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start:source.temp_y_end + 1, source.temp_z_start] = source.space_gaussian_pulse[step] * math.sin(source.polarization_angle) * (1 if source.direction == "Backward" else -1)
                        Ex[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start:source.temp_y_end + 1, source.temp_z_start + (1 if source.direction == "Backward" else -1)] = 0
                        Ey[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start:source.temp_y_end + 1, source.temp_z_start + (1 if source.direction == "Backward" else -1)] = 0
                        Ez[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start:source.temp_y_end + 1, source.temp_z_start + (1 if source.direction == "Backward" else -1)] = 0
                        Hx[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start:source.temp_y_end + 1, source.temp_z_start + (1 if source.direction == "Backward" else -1)] = 0
                        Hy[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start:source.temp_y_end + 1, source.temp_z_start + (1 if source.direction == "Backward" else -1)] = 0
                        Hz[source.temp_x_start:source.temp_x_end + 1, source.temp_y_start:source.temp_y_end + 1, source.temp_z_start + (1 if source.direction == "Backward" else -1)] = 0


            # 探测器记录
            for detector in self.detectors:
                if detector.type == "MovieDetector":
                    if step % detector.sampling_rate == 0:
                        if detector.field_component not in ["E", "H"]:
                            if detector.axis == 'x_plane':
                                detector.record(np.expand_dims(np.flipud(locals()[detector.field_component][detector.temp_x_start, detector.temp_y_start:detector.temp_y_end + 1, detector.temp_z_start:detector.temp_z_end + 1].T), axis = 0))
                            elif detector.axis == 'y_plane':
                                detector.record(np.expand_dims(np.flipud(locals()[detector.field_component][detector.temp_x_start:detector.temp_x_end + 1, detector.temp_y_start, detector.temp_z_start:detector.temp_z_end + 1].T), axis = 0))
                            elif detector.axis == 'z_plane':
                                detector.record(np.expand_dims(np.flipud(locals()[detector.field_component][detector.temp_x_start:detector.temp_x_end + 1, detector.temp_y_start:detector.temp_y_end + 1, detector.temp_z_start].T), axis = 0))
                        else:
                            pass
                elif detector.type == "PointDetector":
                    if detector.field_component not in ["E", "H"]:
                        detector.record(step * dt, locals()[detector.field_component][detector.temp_x_start, detector.temp_y_start, detector.temp_z_start])
                    else:
                        pass



            # 边界条件
            if boundary_type == "PML":
                pml_step(Ex, Ey, Ez, Hx, Hy, Hz, boundary_layers, pml_sigma_d)
                
            # 电磁场布进
            fdtd_step(Ex, Ey, Ez, Hx, Hy, Hz, step_NA_temp, step_NB_temp, step_NC_temp, step_ND_temp)






            # 进度条
            bar_length = int(50 * step / Nt)
            bar = '#' * bar_length + '-' * (50 - bar_length)
            print(f'\r[{bar}] {int((step + 1) / Nt * 100)}%', end='', flush=True)




            # 循环判定
            step += 1
            if step >= Nt:
                print("\nDone.")
                print("step = " + str(step))
                print("simulation_time = " + str(step * dt))
                for detector in self.detectors:
                    detector.save()
                break
            elif mode == 1:
                if (np.max(np.abs(Ez)) > max_ * 10):
                    print("\nDivergent.")
                    print("step = " + str(step))
                    print("simulation_time = " + str(step * dt))
                    for detector in self.detectors:
                        detector.save()
                    break
                elif (np.max(np.abs(Ez)) < min_ and step > 1000):
                    print("\nAuto Done.")
                    print("step = " + str(step))
                    print("simulation_time = " + str(step * dt))
                    for detector in self.detectors:
                        detector.save()
                    break




# @numba.njit()
def fdtd_step(Ex, Ey, Ez, Hx, Hy, Hz, step_NA_temp, step_NB_temp, step_NC_temp, step_ND_temp):

    Hx[1:-1, 1:-1, 1:-1] = step_NC_temp * Hx[1:-1, 1:-1, 1:-1] + step_ND_temp * ((Ey[1:-1, 1:-1, 2:] - Ey[1:-1, 1:-1, 1:-1]) - (Ez[1:-1, 2:, 1:-1] - Ez[1:-1, 1:-1, 1:-1]))
    Hy[1:-1, 1:-1, 1:-1] = step_NC_temp * Hy[1:-1, 1:-1, 1:-1] + step_ND_temp * ((Ez[2:, 1:-1, 1:-1] - Ez[1:-1, 1:-1, 1:-1]) - (Ex[1:-1, 1:-1, 2:] - Ex[1:-1, 1:-1, 1:-1]))
    Hz[1:-1, 1:-1, 1:-1] = step_NC_temp * Hz[1:-1, 1:-1, 1:-1] + step_ND_temp * ((Ex[1:-1, 2:, 1:-1] - Ex[1:-1, 1:-1, 1:-1]) - (Ey[2:, 1:-1, 1:-1] - Ey[1:-1, 1:-1, 1:-1]))
    Ex[1:-1, 1:-1, 1:-1] = step_NA_temp * Ex[1:-1, 1:-1, 1:-1] + step_NB_temp * ((Hy[1:-1, 1:-1, 1:-1] - Hy[1:-1, 1:-1, :-2]) - (Hz[1:-1, 1:-1, 1:-1] - Hz[1:-1, :-2, 1:-1]))
    Ey[1:-1, 1:-1, 1:-1] = step_NA_temp * Ey[1:-1, 1:-1, 1:-1] + step_NB_temp * ((Hz[1:-1, 1:-1, 1:-1] - Hz[:-2, 1:-1, 1:-1]) - (Hx[1:-1, 1:-1, 1:-1] - Hx[1:-1, 1:-1, :-2]))
    Ez[1:-1, 1:-1, 1:-1] = step_NA_temp * Ez[1:-1, 1:-1, 1:-1] + step_NB_temp * ((Hx[1:-1, 1:-1, 1:-1] - Hx[1:-1, :-2, 1:-1]) - (Hy[1:-1, 1:-1, 1:-1] - Hy[:-2, 1:-1, 1:-1]))





# @numba.njit()
def pml_step(Ex, Ey, Ez, Hx, Hy, Hz, boundary_layers, pml_sigma_d):
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
