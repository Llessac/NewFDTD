"""
object.py 创建仿真物体

ObjectGroup : 物体组
Object : 物体基类
Rectangle : 长方体
Circle : 圆柱
Polygon : 多边形柱
Triangle : 三角柱

"""

from .mathTool import *


# 物体组
class ObjectGroup:
    def __init__(self, name:str="New"):
        self.name = name
        self.type = "ObjectGroup"
        self.objects = []

    def append(self, *object):
        for i in object:
            self.objects.append(i)

    def delete(self, *object):
        for i in object:
            self.objects.remove(i)

    def set_constant_index(self, index):
        for object in self.objects:
            object.set_constant_index(index)


# 物体基类
class Object:
    def __init__(self, x:float=0, y:float=0, z:float=0, theta:float=0, phi:float=0, angle_type:str="degree"):
        self.name = "NewObject"
        self.color = "Grey"

        self.material = "Constant"
        self.index = 1.4

        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

        self.x_min = 0.0
        self.y_min = 0.0
        self.z_min = 0.0


        if angle_type == "degree":
            self.theta = float(theta) * degree_to_radian
            self.phi = float(phi) * degree_to_radian
        elif angle_type == "radian":
            self.theta = float(theta)
            self.phi = float(phi)

    def set_x(self, x:float):
        self.x = float(x)
    
    def set_y(self, y:float):
        self.y = float(y)

    def set_z(self, z:float):
        self.z = float(z)

    def set_angle(self, theta, phi, angle_type:str="degree"):
        if angle_type == "degree":
            self.theta = float(theta) * degree_to_radian
            self.phi = float(phi) * degree_to_radian
        elif angle_type == "radian":
            self.theta = float(theta)
            self.phi = float(phi)

    def rotate_z(self, plus:float, angle_type:str="degree"):
        if angle_type == "degree":
            self.phi += float(plus) * degree_to_radian
        elif angle_type == "radian":
            self.phi += float(plus)

    def rotate_x(self, plus:float, angle_type:str="degree"):
        if angle_type == "degree":
            self.phi += float(plus) * degree_to_radian
        elif angle_type == "radian":
            self.phi += float(plus)

    def set_material(self, m):
        self.index = None
        self.material = m

    def set_constant_index(self, i):
        self.index = float(i)
        self.material = "Constant"

    def set_gradient_index(self, func):
        self.index = func
        self.material = None


# 长方体
class Rectangle(Object):
    def __init__(self, x:float=0, y:float=0, z:float=0, l:float=1, w:float=1, h:float=1):
        super().__init__(x, y, z)
        self.length = float(l)
        self.width = float(w)
        self.height = float(h)
        self.x_min = self.x - self.length / 2
        self.y_min = self.y - self.width / 2
        self.z_min = self.z - self.height / 2

        self.type = "Rectangle"

    def set_length(self, l:float):
        self.length = float(l)
        self.x_min = self.x - self.length / 2

    def set_width(self, w:float):
        self.width = float(w)
        self.y_min = self.y - self.width / 2
    
    def set_height(self, h:float):
        self.height = float(h)
        self.z_min = self.z - self.height / 2

    def set_x_min(self, x_min:float):
        self.length = self.x_min - x_min + self.length
        self.x_min = x_min
        self.x = self.x_min + self.length / 2

    def set_x_max(self, x_max:float):
        self.length = x_max - self.x_min
        self.x = self.x_min + self.length / 2

    def set_y_min(self, y_min:float):
        self.width = self.y_min - y_min + self.width
        self.y_min = y_min
        self.y = self.y_min + self.width / 2
    
    def set_y_max(self, y_max:float):
        self.width = y_max - self.y_min
        self.y = self.y_min + self.width / 2

    def set_z_min(self, z_min:float):
        self.height = self.z_min - z_min + self.height
        self.z_min = z_min
        self.z = self.z_min + self.height / 2
    
    def set_z_max(self, z_max:float):
        self.height = z_max - self.z_min
        self.z = self.z_min + self.height / 2


# 圆柱
class Circle(Object):
    def __init__(self, x:float=0, y:float=0, z:float=0, r:float=1, h:float=1):
        super().__init__(x, y, z)
        self.r = float(r)
        self.height = float(h)

        self.type = "Circle"

    def set_r(self, r:float):
        self.r = float(r)

    def set_height(self, h:float):
        self.height = float(h)

    def set_z_min(self, z_min:float):
        self.z = z_min + self.height / 2
    
    def set_z_max(self, z_max:float):
        self.z = z_max - self.height / 2


# 多边形
class Polygon(Object):
    def __init__(self, points:list, x:float=0, y:float=0, z:float=0, h:float=1):
        super().__init__(x, y, z)
        self.points = points
        self.height = float(h)

        self.type = "Polygon"

    def set_height(self, h:float):
        self.height = float(h)

    def set_z_min(self, z_min:float):
        self.z = z_min + self.height / 2
    
    def set_z_max(self, z_max:float):
        self.z = z_max - self.height / 2

    def add_point(self, point:list):
        self.points.append(point)

    def del_point(self, i):
        self.points.pop(i)


# 三角柱
class Triangle(Polygon):
    def __init__(self, points:list=[[0.0, -0.577350], [0.5, 0.288675], [-0.5, 0.288675]], x:float=0, y:float=0, z:float=0, h:float=1):
        super().__init__(points, x, y, z, h)


# 环
class Ring(Object):
    def __init__(self, x:float=0, y:float=0, z:float=0, h:float=1, outer_radius:float=1, inner_radius:float=0.5, start_theta:float=0, end_theta:float=0, angle_type:str="degree"):
        super().__init__(x, y, z)
        self.height = float(h)
        self.outer_radius = float(outer_radius)
        self.inner_radius = float(inner_radius)
        if angle_type == "degree":
            self.start_theta = float(start_theta) * degree_to_radian
            self.end_theta = float(end_theta) * degree_to_radian
        elif angle_type == "radian":
            self.start_theta = float(start_theta)
            self.end_theta = float(end_theta)

        self.type = "Ring"

    def set_height(self, h:float):
        self.height = float(h)

    def set_z_min(self, z_min:float):
        self.z = z_min + self.height / 2
    
    def set_z_max(self, z_max:float):
        self.z = z_max - self.height / 2

    def set_outer_radius(self, outer_radius:float):
        self.outer_radius = outer_radius

    def set_inner_radius(self, inner_radius:float):
        self.inner_radius = inner_radius

    def set_start_theta(self, start_theta:float, angle_type:str="degree"):
        if angle_type == "degree" and 0 <= start_theta <= 360:
            self.start_theta = float(start_theta) * degree_to_radian
        elif angle_type == "radian" and 0 <= start_theta <= 2 * pi:
            self.start_theta = float(start_theta)

    def set_end_theta(self, end_theta:float, angle_type:str="degree"):
        if angle_type == "degree" and 0 <= end_theta <= 360:
            self.end_theta = float(end_theta) * degree_to_radian
        elif angle_type == "radian" and 0 <= end_theta <= 2 * pi:
            self.end_theta = float(end_theta)


# 自定义对象
class Custom(Rectangle):
    def __init__(self, x:float=0, y:float=0, z:float=0, l:float=1, w:float=1, h:float=1):
        super().__init__(x, y, z, l, w, h)
        self.equation1 = ""
        self.equation2 = ""
        self.symmetric = True

        self.type = "Custom"


# 表面
class Surface:
    def __init__(self) -> None:
        pass


# 波导
class Waveguide:
    def __init__(self) -> None:
        pass


# 椭球
class Sphere:
    def __init__(self) -> None:
        pass


# 方台
class Pyramid:
    def __init__(self) -> None:
        pass


# 平面实体
class PlanerSolid:
    def __init__(self) -> None:
        pass


# 平面矩形
class Rectangle2D:
    def __init__(self) -> None:
        pass


# 平面多边形
class Polygon2D:
    def __init__(self) -> None:
        pass
