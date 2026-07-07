import sys
import json
from typing import Optional
from subprocess import run

from PySide6 import QtWidgets
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from qt_material import apply_stylesheet
from mainwindow_ui import Ui_MainWindow
from NewFile_ui import Ui_NewFile

from newFDTDCalculation import grid, object, source, detector, calculation






# 主窗口
class MainWindow(QMainWindow):
    # 更新全局信号
    request_Update_Signal = Signal()
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 初始化窗口设定
        # self.setFixedSize(1600, 900)

        self.isOpenFile = 0
        self.isSetRegion = 0

        # 初始化文件容器
        new_file_address = "emulation/default.json"
        new_file = {"space_unit":"μm", "time_unit":"fs", "objectTree":[], "sources":[], "detectors":[], "region":{"mesh":{}}}
        self.calculation = None
        with open(new_file_address, 'w') as f:
            f.write(json.dumps(new_file))
        self.openFile(new_file_address)


        # 设置ObjectTree
        self.setObjectTree()
        
    def refresh(self):
        self.ui.objectTree.reset()

    def refresh_(self):
        self.setObjectTree()
        self.ui.openGLWidget_XY.paintGL()
        self.ui.openGLWidget_YZ.paintGL()
        self.ui.openGLWidget_XZ.paintGL()


    # File 
    # 点击NewFile按钮 打开新建文件设置界面NewFile
    def setNewFile(self):
        print("Create_New_File")
        win_newfile.show()



    # File 
    # 在NewFile界面创建文件成功返回，读取新创建的文件
    def createNewFile(self, new_file_name): 
        self.openFile(new_file_name)
        print("Create_File_Success")



    # File 
    # 打开新文件
    def openFile(self, new_file=None):
        self.closeFile()
        if (new_file == None) or (new_file == False): # 手动选择读取文件
            file_address ,file_type = QFileDialog.getOpenFileNames(self, 'Open Emulation Files', 'emulation/', 'Json files (*.json)')
        else: # 新建文件后自动读取文件
            file_address = [new_file]
        self.file_now = file_address[0]
        self.calculation = calculation.Calculation(self.file_now)
        self.isOpenFile = 1
        if self.calculation.region.length != 0:
            self.isSetRegion = 1
        print("Load_File_Success")
        self.show3D()
        self.setObjectTree()
        self.request_Update_Signal.emit()



    # File 
    # 保存当前文件
    def saveFile(self):
        if self.isOpenFile == 0:
            print("Not_Open_File")
            return
        if self.file_now != "emulation/default.json":
            self.calculation.save(self.file_now)
            print("Save_File_Success")
        else:
            self.saveFileAs()



    # File 
    # 将当前文件保存为
    def saveFileAs(self): 
        if self.isOpenFile == 0:
            print("Not_Open_File")
            return
        file_address ,file_type = QFileDialog.getSaveFileName(self, 'Open Emulation Files', 'emulation/', 'Json files (*.json)')
        self.calculation.save(file_address)
        self.file_now = file_address
        print("Save_File_Success")



    # File 
    # 关闭当前文件
    def closeFile(self): 
        self.file_now = None
        self.calculation = None
        self.ui.openGLWidget_XY.closeFile()
        self.ui.openGLWidget_YZ.closeFile()
        self.ui.openGLWidget_XZ.closeFile()
        # self.ui.openGLWidget_3D.closeFile()
        self.isOpenFile = 0
        self.isSetRegion = 0
        print("Close_File_Success")





    # Run
    # 运行仿真
    def runFile(self): 
        self.calculation.show3D()
        self.calculation.run()
        print("Run_File")





    # OpenGLWidget
    # 显示文件 openGL窗口读取现有文件
    def show3D(self):
        if self.isOpenFile == 0:
            print("Not_Open_File")
            return
        self.ui.openGLWidget_XY.loadFile(self.calculation)
        self.ui.openGLWidget_YZ.loadFile(self.calculation)
        self.ui.openGLWidget_XZ.loadFile(self.calculation)
        # self.ui.openGLWidget_3D.loadFile(self.calculation)







    # ObjectTree
    # 设置ObjectTree
    def setObjectTree(self):
        self.ui.objectTree.expandAll()
        self.objectTreeModel = QStandardItemModel()
        self.objectTreeRoot = self.objectTreeModel.invisibleRootItem()
        self.ui.objectTree.setModel(self.objectTreeModel)

        if self.isOpenFile == 0:
            print("Not_Open_File")
            return


        if self.calculation.region.length != 0:
            self.objectTreeRoot.appendRow(CustomStandardItem("(FDTD)  " + self.calculation.region.name, self.calculation.region))
            for mesh in self.calculation.region.mesh:
                self.objectTreeRoot.appendRow(CustomStandardItem("(mesh)  " + mesh.name, mesh))


        for source in self.calculation.sources:
            self.objectTreeRoot.appendRow(CustomStandardItem("(" + source.type + ")  " + source.name, source))

        for object in self.calculation.objectTree:
            self._loadObject(object, self.objectTreeRoot)

        for detector in self.calculation.detectors:
            self.objectTreeRoot.appendRow(CustomStandardItem("(" + detector.type + ")  " + detector.name, detector))

        self.refresh()
        print("Set_Object_Tree_Success")


    # ObjectTree
    # 递归解析ObjectTree信息
    def _loadObject(self, object, root):
        if object.type == "ObjectGroup":
            group = CustomStandardItem("(" + object.type + ")  " + object.name, object)
            root.appendRow(group)
            for object_ in object.objects:
                self._loadObject(object_, group)
        else:
            root.appendRow(CustomStandardItem("(" + object.type + ")  " + object.name, object))
                





    # ToolBox
    # 添加仿真区域
    def addRegion(self):
        if self.isSetRegion == 1:
            return
        
        if self.isOpenFile == 0:
            print("Not_Open_File")
            return
        
        self.calculation.add_Region(grid.Region(-0.5, 1, -0.5, 1, -0.5, 1))

        self.isSetRegion = 1
        self.request_Update_Signal.emit()
        self.setObjectTree()



    # ToolBox
    # 添加物体
    def addObject(self):
        if self.isOpenFile == 0:
            print("Not_Open_File")
            return
        
        self.calculation.add_ObjectTree(object.Rectangle(0, 0, 0, 0.1, 0.1, 0.1))

        self.request_Update_Signal.emit()
        self.setObjectTree()



    # ToolBox
    # 添加物体组
    def addObjectGroup(self):
        if self.isOpenFile == 0:
            print("Not_Open_File")
            return
        
        self.calculation.add_ObjectTree(object.ObjectGroup())

        self.request_Update_Signal.emit()
        self.setObjectTree()



    # ToolBox
    # 添加源
    def addSource(self):
        if self.isOpenFile == 0:
            print("Not_Open_File")
            return
        
        self.calculation.add_Source(source.GaussianSource(0, 0.4, 0, 2, 0, 2, "y_plane", direction="Backward"))

        self.request_Update_Signal.emit()
        self.setObjectTree()



    # ToolBox
    # 添加监视器
    def addDetector(self):
        if self.isOpenFile == 0:
            print("Not_Open_File")
            return
        
        self.calculation.add_Detector(detector.MovieDetector(0, 0, 0, 1, 1, 0, "z_plane","output", field_component="Ez"))

        self.request_Update_Signal.emit()
        self.setObjectTree()



    # ToolBox
    # 添加细化仿真区域
    def addMesh(self):
        return 
    
        if self.isOpenFile == 0:
            print("Not_Open_File")
            return
        
        self.calculation.add_Mesh(grid.Mesh(0.001, -0.1, 0.2, -0.1, 0.2, -0.1, 0.2))
        self.request_Update_Signal.emit()







    # ObjectParameterTable
    # 设置变量参数表
    def setObjectParameterTable(self):
        self.objectParameterModel = QStandardItemModel()
        self.ui.objectParameterTable.setModel(self.objectParameterModel)
        
        if len(self.ui.objectTree.selectedIndexes()) == 0:
            return
        else:
            model = self.ui.objectTree.model()
            index = self.ui.objectTree.selectedIndexes()[0]
            item = model.itemFromIndex(index).item
        i = 0
        model_ = self.ui.objectParameterTable.model()
        for o in item.__dict__:
            model_.setItem(i, 0, QStandardItem(o))
            model_.setItem(i, 1, QStandardItem(str(item.__dict__[o])))
            i += 1
        model_.dataChanged.connect(self.changeObjectParameterTable)


    # ObjectParameterTable
    # 修改变量参数表
    def changeObjectParameterTable(self):
        if len(self.ui.objectTree.selectedIndexes()) == 0:
            return
        model = self.ui.objectTree.model()
        index = self.ui.objectTree.selectedIndexes()[0]
        item = model.itemFromIndex(index).item

        model_ = self.ui.objectParameterTable.model()
        index_ = self.ui.objectParameterTable.selectedIndexes()[0]
        row = index_.row()
        col = index_.column()
        if col == 1:
            item.__dict__[model_.itemData(model_.index(row, 0))[0]] = convert_to_number_if_possible(model_.itemFromIndex(index_).data(0))

        self.refresh_()

        


        
        
    
















    # test
    # 测试使用*****************************************
    def test(self): 
        print(self.calculation.__dict__["objectTree"][0].__dict__)
        
        





def convert_to_number_if_possible(s):
    # 首先尝试转换为整数
    try:
        return int(s)
    except ValueError:
        pass  # 如果不是整数，继续尝试
    
    # 尝试转换为浮点数
    try:
        return float(s)
    except ValueError:
        pass  # 如果也不是浮点数，最后保持原样
    
    # 如果以上都失败了，说明s是非数字字符串，直接返回
    return s





class CustomStandardItem(QStandardItem):
    def __init__(self, text, item):
        super().__init__(text)
        self.item = item
















# 创建新文件选项窗口
class NewFileWindow(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_NewFile()
        self.ui.setupUi(self)

        # 初始默认选择
        self.ui.radioButton_mum.setChecked(1)
        self.ui.radioButton_fs.setChecked(1)


    def accept(self): # 确认新建文件，创建新文件
        new_file = {"space_unit":"", "time_unit":"", "objectTree":[], "sources":[], "detectors":[], "region":{"mesh":{}}}
        new_file_address = "emulation/" + self.ui.textEdit_name.toPlainText() + ".json"
        with open(new_file_address,'w') as f:
            if self.ui.radioButton_mum.isChecked():
                new_file["space_unit"] = "μm"
            elif self.ui.radioButton_mm.isChecked():
                new_file["space_unit"] = "mm"
            if self.ui.radioButton_fs.isChecked():
                new_file['time_unit'] = "fs"
            elif self.ui.radioButton_ps.isChecked():
                new_file['time_unit'] = "ps"
            elif self.ui.radioButton_ns.isChecked():
                new_file['time_unit'] = "ns"
            # new_file['backend'] = self.ui.comboBox_backend.currentText()
            f.write(json.dumps(new_file))   
        win.createNewFile(new_file_address)
        return super().accept()










if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    screen = QGuiApplication.primaryScreen().geometry()
    app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.Ceil)
    win = MainWindow()
    win.setWindowTitle("NewFDTD")
    win.setGeometry(0, 0, screen.width(), screen.height())
    win_newfile = NewFileWindow()
    apply_stylesheet(app, theme='dark_cyan.xml')
    win.show()
    app.exit(app.exec())