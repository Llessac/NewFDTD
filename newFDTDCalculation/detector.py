"""
detector.py 创建探测器

Detector : 探测器基类
MovieDetector : 视频探测器, 用于探测光与结构相互作用随时间变化
"""

from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.animation import FuncAnimation
from matplotlib.cm import jet
import json
import copy
import cv2

from .mathTool import *

colors = [
        (-1, (0, 0, 128)),   # 深蓝色
        (-0.75, (0, 128, 255)), # 青色
        (-0.5, (0, 255, 255)), # 青绿色
        (-0.25, (0, 255, 0)),  # 绿色
        (0, (255, 255, 255)),  # 白色（中性过渡）
        (0.25, (255, 165, 0)), # 黄色
        (0.5, (255, 0, 0)),   # 红色
        (0.75, (128, 0, 0)),  # 深红色
        (1, (255, 0, 0)),    # 更深的红色，保持与1对应
    ]


class Detector:

    def __init__(self, x, y, z) -> None:

        self.name = ""
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.temp_x_start = 0
        self.temp_x_end = 0
        self.temp_y_start = 0
        self.temp_y_end = 0
        self.temp_z_start = 0
        self.temp_z_end = 0





class PointDetector(Detector):
    def __init__(self, x=0, y=0, z=0, name="pointOutput", field_component="Ez"):
        super().__init__(x, y, z)
        self.t = []
        self.data = []
        self.type = "PointDetector"
        self.axis = "point"
        self.name = name
        self.field_component = field_component

        self.length = 0
        self.width = 0
        self.height = 0

    def record(self, t, data_new):
        self.t.append(t)
        self.data.append(data_new)

    def show(self):
        plt.plot(self.t, self.data)
        plt.xlabel("t (x 10^-15 s)")
        if self.field_component in ["E", "Ex", "Ey", "Ez"]:
            plt.ylabel(self.field_component + " (N/C)")
        else:
            plt.ylabel(self.field_component + " (A/m)")
        plt.show()

    def save(self):
        data = json.dumps([self.t, self.data])
        with open("emulation/" + self.name + ".json", 'w') as f:
            f.write(data)

    def load(self, file):
        with open(file, 'r') as f:
            data = json.loads(f.read())
            self.t = data[0]
            self.data = data[1]



class MovieDetector(Detector):
    def __init__(self, x=0, y=0, z=0, l=0, w=0, h=0, axis="x_plane", name="output", field_component="Ez", horizontal_resolution=320, vertical_resolution=240, sampling_rate=1, frame_rate=30) -> None:
        """
        创建Movie探测器

        参数: 
        x : x轴中心点
        y : y轴中心点
        z : z轴中心点
        l : x轴上长度
        w : y轴上宽度
        h : z轴上高度
        axis : 探测器朝向
            x_plane : 与x轴垂直
            y_plane : 与y轴垂直
            z_plane : 与z轴垂直
        name : 输出视频命名
        field_component : 采样场分量
            E : 电场绝对值
            Ex : 电场x轴分量
            Ey : 电场y轴分量
            Ez : 电场z轴分量
            H : 磁场绝对值
            Hx : 磁场x轴分量
            Hy : 磁场y轴分量
            Hz : 磁场z轴分量
        sampling_rate : 采样率
        frame_rate : 视频帧率
        horizontal_resolution : 视频横向分辨率
        vertical_resolution : 视频纵向分辨率
        """
        
        super().__init__(x, y, z)
        
        self.type = "MovieDetector"
        self.name = name

        self.length = float(l)
        self.width = float(w)
        self.height = float(h)
        self.axis = axis
        if self.axis == "x_plane":
            self.length = 0
        elif self.axis == "y_plane":
            self.width = 0
        elif self.axis == "z_plane":
            self.height = 0

        self.field_component = field_component

        self.horizontal_resolution = horizontal_resolution
        self.vertical_resolution = vertical_resolution

        self.sampling_rate = sampling_rate # 采样率
        self.frame_rate = frame_rate # 帧率

        self.data = None


    def set_size(self, horizontal_resolution, vertical_resolution):
        self.horizontal_resolution = horizontal_resolution
        self.vertical_resolution = vertical_resolution


    def record(self, frame):
        self.data = np.concatenate((self.data, frame.copy()), axis=0)


    def save(self):
                
            
        # 初始化视频写入器，设定编码、尺寸、帧率等参数
        fourcc = cv2.VideoWriter_fourcc(*'H264')  # 视频编码
        video_out = cv2.VideoWriter(self.name + '.mp4', fourcc, self.frame_rate, (self.horizontal_resolution, self.vertical_resolution))

        max_ = abs(np.max(self.data))
        min_ = abs(np.min(self.data))

        self.data = np.where(self.data > 0, self.data / 2 / max_ + 0.5, np.where(self.data < 0, self.data / 2 / min_ + 0.5, 0.5))

        # 写入每一帧
        for frame in self.data:
            color_frame = color_map(frame).astype(np.uint8)
            resized_matrix = cv2.resize(color_frame, (self.horizontal_resolution, self.vertical_resolution), interpolation=cv2.INTER_LINEAR)
            # resized_matrix = np.expand_dims(resized_matrix, axis=-1)
            video_out.write(resized_matrix)  # 转换为无符号8位整型并写入

        # 释放资源
        video_out.release()
        print("\nVideo saved.")


# FrequencyDomainFieldProfile探测器，用于探测给定空间内频域分布
# x, y, z, l, w, h为位置、大小
# axis为探测器探测空间类型，可选项:point, x_line, y_line, z_line, x_plane, y_plane, z_plane, 3D
class FrequencyDomainFieldProfile(Detector):
    def __init__(self, x=0, y=0, z=0, l=0, w=0, h=0, axis="point", delta=30):
        super().__init__(x, y, z)

        self.type = "FrequencyDomainFieldProfile"

        self.length = float(l)
        self.width = float(w)
        self.height = float(h)
        self.axis = axis
        if self.axis in {"point", "y_line", "z_line", "x_plane"}:
            self.length = 0
        if self.axis in {"point", "x_line", "z_line", "y_plane"}:
            self.width = 0
        if self.axis in {"point", "x_line", "y_line", "z_plane"}:
            self.height = 0

        self.delta = float(delta)

        

# FrequencyDomainFieldAndPower探测器
# x, y, z, l, w, h为位置、大小
# axis为探测器探测空间类型，可选项:point, x_line, y_line, z_line, x_plane, y_plane, z_plane, 3D
class FrequencyDomainFieldAndPower(Detector):
    def __init__(self, x=0, y=0, z=0, l=0, w=0, h=0, axis="point"):
        super().__init__(x, y, z)
        self.axis = axis







# 颜色映射函数
def color_map(frame):
    """将灰度值映射到RGB颜色, 正值为暖, 负值为冷色, 绝对值越大颜色越饱和"""

    rgb_image = jet(frame)
    rgb_image = (rgb_image[:, :, :3] * 255).astype(np.uint8)
    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)


    return bgr_image

    m = 0.00001 * max_abs


    # zero_mask = (value <= m and value >= -m)
    positive_data = np.maximum(value, m)
    negative_data = np.minimum(value, -m)
    
    # 对正负值使用对数缩放，确保非零值
    log_positive = np.log1p( positive_data / 1000)  # log1p(x) = log(1 + x), 避免对数中出现0或负值的问题
    log_negative = np.log1p(-negative_data / 1000)  # 负数取对数后翻转以保持冷暖色调的对应关系

    log_max_abs = np.log1p(max_abs / 1000)
    log_min_abs = np.log1p(- min_abs / 1000)

    # 归一化处理，确保数据在0到1之间
    norm_positive = Normalize(vmin=log_positive.min(), vmax=log_max_abs, clip=True)(log_positive)
    norm_negative = - Normalize(vmin=log_negative.min(), vmax=log_min_abs, clip=True)(log_negative)
    
    # 合并正负值
    norm_matrix = np.where(value > m, norm_positive, np.where(value < -m, norm_negative, 0))

    rgb_image = seismic(norm_matrix)
    rgb_image = (rgb_image[:, :, :3] * 255).astype(np.uint8)
    
    # 将RGB图像转换为OpenCV期望的BGR格式
    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

    return bgr_image

