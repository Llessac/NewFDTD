from math import radians
from typing import List, Tuple

from PySide6.QtCore import Qt, QPoint, Signal, Slot, QPointF
from PySide6.QtGui import QMatrix4x4, QVector3D, QWheelEvent, QOpenGLFunctions
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL import GL as gl





# 2D图形显示窗口基类
class ShowWidget2D(QOpenGLWidget):

    color_dict = {
        "red": (1.0, 0.0, 0.0),
        "green": (0.0, 1.0, 0.0),
        "blue": (0.0, 0.0, 1.0),
        "cyan": (0.0, 1.0, 1.0),
        "magenta": (1.0, 0.0, 1.0),
        "yellow": (1.0, 1.0, 0.0),
        "black": (0.0, 0.0, 0.0),
        "white": (1.0, 1.0, 1.0),
        "gray": (0.5, 0.5, 0.5),
        "orange": (1.0, 0.5, 0.0),
        "purple": (0.5, 0.0, 0.5),
        "brown": (0.6, 0.4, 0.2),
        "pink": (1.0, 0.75, 0.8),
        "teal": (0.0, 0.5, 0.5),
        "lime": (0.5, 1.0, 0.0),
        "silver": (0.75, 0.75, 0.75),
        "maroon": (0.5, 0.0, 0.0),
        "olive": (0.5, 0.5, 0.0),
        "navy": (0.0, 0.0, 0.5),
        "aqua": (0.5, 1.0, 0.5),
        "gold": (1.0, 0.84, 0.0),
        "indigo": (0.29, 0.0, 0.51),
        "violet": (0.93, 0.51, 0.93),
        }
    
    radio_x = 240 # radio为屏幕尺寸与真实尺寸之比，真实尺寸 × radio × zoom＝ 屏幕尺寸（不考虑单位（采用统一单位））
    radio_y = 240
    radio_z = 240
    zoom_xy = 1.0
    zoom_yz = 1.0
    zoom_xz = 1.0

    # 同步信号
    request_Repaint_Signal = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置初始参数
        self.num_rows = 10
        self.num_cols = 10
        self.row_spacing = 480 / (self.num_rows + 1)
        self.col_spacing = 480 / (self.num_cols + 1)

        # 打开文件标识
        self.isOpenFile = 0

        # 轴标识
        self.axis = ""
        
        # 选中组件标识
        self.isSelectComponent = 0
        # 变换框
        self.transformBox = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)



    # 初始化
    def initializeGL(self):
        # self.opengl_functions = QOpenGLFunctions(self.context())
        # self.opengl_functions.initializeOpenGLFunctions()
        # self.opengl_functions.glClearColor(0.0, 0.0, 0.0, 1.0) # 设置清屏颜色
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    



    # paintGL函数，每次更改图像调用
    def paintGL(self):
        self.makeCurrent()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, self.width(), 0, self.height(), -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        # 绘制网格
        gl.glClear(gl.GL_COLOR_BUFFER_BIT) 
        self.drawGrid()

        if self.isOpenFile == 0:
            return
        
        # 绘画具体结构
        if self.axis == "xy":
            self.paintXY()
        elif self.axis == "xz":
            self.paintXZ()
        elif self.axis == "yz":
            self.paintYZ()


    # 子类中重写
    def paintXY(self):
        pass

    def paintXZ(self):
        pass

    def paintYZ(self):
        pass


    # 绘制实心矩形
    def drawFillRect(self, x_min, y_min, l, w, c="grey", alpha=1.0):
        x_min = x_min + self.width() / 2
        y_min = y_min + self.height() / 2

        if c in self.color_dict:
            gl.glColor4f(*self.color_dict[c], alpha)
        else:
            gl.glColor4f(0.5, 0.5, 0.5, alpha)

        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(x_min, y_min)
        gl.glVertex2f(x_min + l, y_min)
        gl.glVertex2f(x_min + l, y_min + w)
        gl.glVertex2f(x_min, y_min + w)
        gl.glEnd()

    # 绘制空心矩形
    def drawRect(self, x_min, y_min, l, w, c="grey"):
        x_min = x_min + self.width() / 2
        y_min = y_min + self.height() / 2

        if c in self.color_dict:
            gl.glColor3f(*self.color_dict[c])
        else:
            gl.glColor3f(0.5, 0.5, 0.5)

        gl.glBegin(gl.GL_LINE_LOOP)
        gl.glVertex2f(x_min, y_min)
        gl.glVertex2f(x_min + l, y_min)
        gl.glVertex2f(x_min + l, y_min + w)
        gl.glVertex2f(x_min, y_min + w)
        gl.glEnd()


    # 绘制网格
    def drawGrid(self):
        if self.axis == "xy":
            self.row_spacing = self.height() / (self.num_rows + 1) * self.zoom_xy * self.zoom_xz
            self.col_spacing = self.width() / (self.num_cols + 1) * self.zoom_xy * self.zoom_yz
        elif self.axis == "xz":
            self.row_spacing = self.height() / (self.num_rows + 1) * self.zoom_xy * self.zoom_xz
            self.col_spacing = self.width() / (self.num_cols + 1) * self.zoom_xz * self.zoom_yz
        elif self.axis == "yz":
            self.row_spacing = self.height() / (self.num_rows + 1) * self.zoom_xy * self.zoom_yz
            self.col_spacing = self.width() / (self.num_cols + 1) * self.zoom_xz * self.zoom_yz
        
        gl.glColor3f(0.5, 0.5, 0.5)

        # 绘制水平线
        if self.height() / self.row_spacing < 50:
            for i in range(int(self.height() / self.row_spacing) + 1):
                y = self.row_spacing * (i + 1)
                gl.glBegin(gl.GL_LINES)
                gl.glVertex2f(0, y)
                gl.glVertex2f(self.width(), y)
                gl.glEnd()

        # 绘制垂直线
        if self.width() / self.col_spacing < 50:
            for j in range(int(self.width() / self.col_spacing) + 1):
                x = self.col_spacing * (j + 1)
                gl.glBegin(gl.GL_LINES)
                gl.glVertex2f(x, 0)
                gl.glVertex2f(x, self.height())
                gl.glEnd()




    # OpenGL窗口读取文件
    def loadFile(self, calculation):
        self.calculation = calculation
        if self.calculation.region.length != 0:
            self.radio_x = self.width() / self.calculation.region.length / 2
            self.radio_y = self.width() / self.calculation.region.width / 2
            self.radio_z = self.height() / self.calculation.region.height / 2
        self.isOpenFile = 1
        print("ShowWidget_Load_File_Success")
        self.repaint()


    # 关闭文件
    def closeFile(self):
        self.isOpenFile = 0
        self.radio_x = self.radio_y = self.radio_z = 240
        self.makeCurrent()
        try:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        except:
            pass

    










# 图形显示窗口X-Y
class ShowWidgetXY(ShowWidget2D):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.axis = "xy"
        

    def paintXY(self):
        # Region
        gl.glLineWidth(5.0)
        if self.calculation.region.length != 0:
            self.drawRect(self.calculation.region.x_min * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        self.calculation.region.y_min * self.radio_y * self.zoom_xy * self.zoom_yz, 
                        self.calculation.region.length * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        self.calculation.region.width * self.radio_y * self.zoom_xy * self.zoom_yz, c="yellow")
        gl.glLineWidth(1.0)

        # Sources
        for source in self.calculation.sources:
            if source.type == "GaussianSource":
                self.drawFillRect((source.x - source.length / 2) * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        (source.y - source.width / 2) * self.radio_y * self.zoom_xy * self.zoom_yz, 
                        source.length * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        source.width * self.radio_y * self.zoom_xy * self.zoom_yz, c="red", alpha=0.5)

        # Object
        for object in self.calculation.objectTree:
            self._showObject(object)

        # Mesh
        for mesh in self.calculation.region.mesh:
            self.drawRect(mesh.x_min * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        mesh.y_min * self.radio_y * self.zoom_xy * self.zoom_yz, 
                        mesh.length * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        mesh.width * self.radio_y * self.zoom_xy * self.zoom_yz, c="blue")
            
    
    # 递归辅助显示ObjectTree
    def _showObject(self, object):
        if object.type == "ObjectGroup":
            for object_ in object.objects:
                self._showObject(object_)
        else:
            if object.type == "Rectangle":
                self.drawFillRect(object.x_min * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        object.y_min * self.radio_y * self.zoom_xy * self.zoom_yz, 
                        object.length * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        object.width * self.radio_y * self.zoom_xy * self.zoom_yz, c=object.color, alpha=0.5)

    # 处理滚轮事件
    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()

        # 更新当前的缩放因子 ******修改实例的类变量不能修改类的类变量，系统会重新分配一个实例的类变量*********
        ShowWidget2D.zoom_xy *= 1.1 if delta > 0 else 0.9

        self.update()
        self.request_Repaint_Signal.emit()



# 图形显示窗口X-Z
class ShowWidgetXZ(ShowWidget2D):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.axis = "xz"
        

    def paintXZ(self):
        # Region
        gl.glLineWidth(5.0)
        if self.calculation.region.length != 0:
            self.drawRect(self.calculation.region.x_min * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        self.calculation.region.z_min * self.radio_z * self.zoom_xz * self.zoom_yz, 
                        self.calculation.region.length * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        self.calculation.region.height * self.radio_z * self.zoom_xz * self.zoom_yz, c="yellow")
        gl.glLineWidth(1.0)

        # Sources
        for source in self.calculation.sources:
            if source.type == "GaussianSource":
                self.drawFillRect((source.x - source.length / 2) * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        (source.z - source.height / 2) * self.radio_z * self.zoom_xz * self.zoom_yz, 
                        source.length * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        source.height * self.radio_z * self.zoom_xz * self.zoom_yz, c="red", alpha=0.5)

        # Object
        for object in self.calculation.objectTree:
            self._showObject(object)

        # Mesh
        for mesh in self.calculation.region.mesh:
            self.drawRect(mesh.x_min * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        mesh.z_min * self.radio_z * self.zoom_xz * self.zoom_yz, 
                        mesh.length * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        mesh.height * self.radio_z * self.zoom_xz * self.zoom_yz, c="blue")
            
    # 递归辅助显示ObjectTree
    def _showObject(self, object):
        if object.type == "ObjectGroup":
            for object_ in object.objects:
                self._showObject(object_)
        else:
            if object.type == "Rectangle":
                self.drawFillRect(object.x_min * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        object.z_min * self.radio_z * self.zoom_xz * self.zoom_yz, 
                        object.length * self.radio_x * self.zoom_xy * self.zoom_xz, 
                        object.height * self.radio_z * self.zoom_xz * self.zoom_yz, c=object.color, alpha=0.5)
                

    # 处理滚轮事件
    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()

        # 更新当前的缩放因子
        ShowWidget2D.zoom_xz *= 1.1 if delta > 0 else 0.9

        self.update()
        self.request_Repaint_Signal.emit()


# 图形显示窗口Y-Z
class ShowWidgetYZ(ShowWidget2D):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.axis = "yz"
        

    def paintYZ(self):
        # Region
        gl.glLineWidth(5.0)
        if self.calculation.region.length != 0:
            self.drawRect(self.calculation.region.y_min * self.radio_y * self.zoom_xy * self.zoom_yz, 
                        self.calculation.region.z_min * self.radio_z * self.zoom_xz * self.zoom_yz, 
                        self.calculation.region.width * self.radio_y * self.zoom_xy * self.zoom_yz, 
                        self.calculation.region.height * self.radio_z * self.zoom_xz * self.zoom_yz, c="yellow")
        gl.glLineWidth(1.0)

        # Sources
        for source in self.calculation.sources:
            if source.type == "GaussianSource":
                self.drawFillRect((source.y - source.width / 2) * self.radio_y * self.zoom_xy * self.zoom_yz, 
                        (source.z - source.height / 2) * self.radio_z * self.zoom_xz * self.zoom_yz, 
                        source.width * self.radio_y * self.zoom_xy * self.zoom_yz, 
                        source.height * self.radio_z * self.zoom_xz * self.zoom_yz, c="red", alpha=0.5)

        # Object
        for object in self.calculation.objectTree:
            self._showObject(object)

        # Mesh
        for mesh in self.calculation.region.mesh:
            self.drawRect(mesh.y_min * self.radio_y * self.zoom_xy * self.zoom_yz, 
                        mesh.z_min * self.radio_z * self.zoom_xz * self.zoom_yz, 
                        mesh.width * self.radio_y * self.zoom_xy * self.zoom_yz, 
                        mesh.height * self.radio_z * self.zoom_xz * self.zoom_yz, c="blue")

    # 递归辅助显示ObjectTree
    def _showObject(self, object):
        if object.type == "ObjectGroup":
            for object_ in object.objects:
                self._showObject(object_)
        else:
            if object.type == "Rectangle":
                self.drawFillRect(object.y_min * self.radio_y * self.zoom_xy * self.zoom_yz, 
                        object.z_min * self.radio_z * self.zoom_xz * self.zoom_yz, 
                        object.width * self.radio_y * self.zoom_xy * self.zoom_yz, 
                        object.height * self.radio_z * self.zoom_xz * self.zoom_yz, c=object.color, alpha=0.5)

    # 处理滚轮事件
    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()

        # 更新当前的缩放因子
        ShowWidget2D.zoom_yz *= 1.1 if delta > 0 else 0.9

        self.update()
        self.request_Repaint_Signal.emit()

# 3D图形显示窗口
class ShowWidget3D(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)