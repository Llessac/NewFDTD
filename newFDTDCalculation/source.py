"""
source.py 提供源的设置

Source : 源的基类
DipoleSource : 偶极子源
GaussianSource : 高斯源
PlaneSource : 平面源

"""
from .mathTool import *


# 源
class Source:
    def __init__(self, x, y, z, l, w, h, amplitude, phase) -> None:
        self.name = ""
        self.x = float(x)
        self.length = float(l)
        self.y = float(y)
        self.width = float(w)
        self.z = float(z)
        self.height = float(h)
        self.angle_theta = 0
        self.angle_phi = 0
        self.amplitude = amplitude
        self.phase = phase

        self.temp_x_start = 0
        self.temp_x_end = 0
        self.temp_y_start = 0
        self.temp_y_end = 0
        self.temp_z_start = 0
        self.temp_z_end = 0


# 偶极子源
class DipoleSource(Source):
    def __init__(self) -> None:
        super().__init__()


# 高斯源
class GaussianSource(Source):
    def __init__(self, x=0, y=0, z=0, l=0, w=0, h=0, axis="x_plane", amplitude=1, phase=0, direction="Forward", polarization_angle=0) -> None:
        """
        创建高斯源

        参数：
        x : x轴中心点
        y : y轴中心点
        z : z轴中心点
        l : x轴上长度
        w : y轴上宽度
        h : z轴上高度
        axis : 源基面朝向
            x_plane : 与x轴垂直
            y_plane : 与y轴垂直
            z_plane : 与z轴垂直
        amplitude : 电场振幅
        phase : 电场相位
        direction : 源方向
            Forward : 沿轴正向
            Backward : 沿轴负向
        polarization_angle : 极化方向, 迎着波的朝向逆时针旋转, 默认按照x-axis -> y, y-axis -> z, z-axis -> x的方向

        """
        super().__init__(x, y, z, l, w, h, amplitude, phase)

        self.type = "GaussianSource"
        self.name = "GaussianSource"

        self.axis = axis
        if self.axis == "z_plane":
            self.height = 0
        elif self.axis == "y_plane":
            self.width = 0
        elif self.axis == "x_plane":
            self.length = 0

        # 朝向
        self.direction = direction
        self.phase = 0 if self.direction == "Forward" else pi

        
        self.polarization_angle = polarization_angle

        # 束腰
        self.waist_radius = 1.01818
        self.distance_from_waist = 0
        self.space_sigma = self.waist_radius / 1.41421356

        self.set_frequency(1.59889, 0.799447)

        self.gaussian_pulse = []
        self.space_gaussian_pulse = []
        self.pulse_mask = []


    def set_waist(self, waist_radius, distance_from_waist):
        """
        设定束腰

        参数：
        waist_radius : 束腰半径
        distance_from_waist : 束腰与源中心距离

        """
        self.waist_radius = waist_radius
        self.distance_from_waist = distance_from_waist
        self.space_sigma = self.waist_radius / 1.41421356


        
    def set_frequency(self, frequency_center, frequency_span):
        """
        设定频率

        参数：
        frequency_center : 频率中心
        frequency_span : 频率半高宽

        """
        self.frequency_center = frequency_center
        self.frequency_span = frequency_span
        self.pulse_width_FWHM = self.frequency_span / self.frequency_center
        self.pulse_sigma = self.pulse_width_FWHM / (2*np.sqrt(np.log(2)))
        self.pulse_length = 0.994724
        self.offset = 2.82037


# 平面源
class PlaneSource(Source):
    def __init__(self, x=0, y=0, z=0, l=0, w=0, h=0, axis="x_plane", amplitude=10, phase=0, direction="Forward", polarization_angle=0) -> None:
        """
        创建平面波源

        参数：
        x : x轴中心点
        y : y轴中心点
        z : z轴中心点
        l : x轴上长度
        w : y轴上宽度
        h : z轴上高度
        axis : 源基面朝向
            x_plane : 与x轴垂直
            y_plane : 与y轴垂直
            z_plane : 与z轴垂直
        amplitude : 电场振幅
        phase : 电场相位
        direction : 源方向
            Forward : 沿轴正向
            Backward : 沿轴负向
        polarization_angle : 极化方向, 迎着波的朝向逆时针旋转, 默认按照x-axis -> y, y-axis -> z, z-axis -> x的方向

        """
        super().__init__(x, y, z, l, w, h, amplitude, phase)

        self.type = "PlaneSource"

        self.axis = axis
        if self.axis == "z_plane":
            self.height = 0
        elif self.axis == "y_plane":
            self.width = 0
        elif self.axis == "x_plane":
            self.length = 0

        self.direction = direction
        self.polarization_angle = polarization_angle

        self.plane_wave_type = "Bloch/periodic"

        self.set_wavelength(0.4, 0.7)

    # μm
    def set_wavelength(self, wavelength_start, wavelength_end):
        self.wavelength_start = wavelength_start
        self.wavelength_end = wavelength_end
        self.frequency_start = c / wavelength_end * 1000
        self.frequency_end = c / wavelength_start * 1000


    def set_frequency(self, frequency_start, frequency_end):
        """
        设定频率

        参数：
        frequency_start : 频率起点
        frequency_end : 频率终点

        """
        self.frequency_start = frequency_start
        self.frequency_end = frequency_end
        self.wavelength_start = c / frequency_end * 1000
        self.wavelength_end = c / frequency_start * 1000


# 
class TFSFSource(Source):
    def __init__(self) -> None:
        super().__init__()


#
class ImportSource(Source):
    def __init__(self) -> None:
        super().__init__()


