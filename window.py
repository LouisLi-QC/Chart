from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core
import pyqtgraph as pg
import numpy as np

from handler import resize_plots_adaptively, visible_panel_onchange, get_open_file_handler


class MainWindow(widgets.QMainWindow):
    """
        该类提供了显示值的窗口，并且内部集成了处理逻辑以提供交互
    """

    def __init__(self, title, names, cfg, datas, reloadProcessor):
        super(MainWindow, self).__init__()
        self.Cfg = cfg
        self.setWindowTitle(title)

        self.PlotNames = names
        self.PlotWidgets = {}.fromkeys(self.PlotNames)
        self.PlotCheckBoxes = {}.fromkeys(self.PlotNames)
        self.PlotLabels = {}.fromkeys(self.PlotNames)
        self.PlotItems = {}.fromkeys(self.PlotNames)
        self.VisiblePlotCnt = 0
        self.Datas = datas
        self.ReloadProcessor = reloadProcessor  # the handler processing file loading event

        self.UIinit()

    def UIinit(self):
        """
            UI 组件初始化
        """

        # resize the window and fix
        self.resize(self.Cfg['WindowWidth'], self.Cfg['WindowHeight'])
        self.setFixedSize(self.Cfg['WindowWidth'], self.Cfg['WindowHeight'])

        # global layout
        self.global_layout()

        # add plot widget to plot layout
        for name in self.PlotNames:
            self.add_plot_widget(name, self.Cfg['PlotWidth'], self.Cfg['PlotHeight'])

        # loading data before control panel constructed, after widgets ready
        self.load_datas(self.Datas)

        # add visible widget to panel layout
        self.add_visible_widget()

        # add opening file menu
        self.add_file_menu()

        self.show()

    def global_layout(self):
        """
            全局布局设置，包含两个布局:
            plotLayout用于保存绘图小部件，panelLayout用于保存面板小部件
        """
        self.plotLayout = widgets.QVBoxLayout()
        self.panelLayout = widgets.QVBoxLayout()
        self.globalLayout = widgets.QHBoxLayout()

        self.globalLayout.addLayout(self.panelLayout)
        self.globalLayout.addLayout(self.plotLayout)

        self.Widget = widgets.QWidget()
        self.Widget.setLayout(self.globalLayout)
        self.setCentralWidget(self.Widget)

    def add_visible_widget(self):
        """
            将Options设置面板添加到panelLayout
        """

        visLayout = widgets.QVBoxLayout()

        # 创建面板组件的标签，名称样式位置
        visLabel = widgets.QLabel('Options', self)
        visLabel.setStyleSheet(self.Cfg['LabelTwoFontStyle'])
        visLabel.setAlignment(core.Qt.AlignBottom | core.Qt.AlignLeft)
        visLayout.addWidget(visLabel)
        visLayout.setAlignment(core.Qt.AlignTop)

        # 创建勾选框
        for name in self.PlotNames:
            self.add_checkbox_widget(label=name,
                                     checked=self.Cfg[name + 'Visible'],
                                     handler=self.visible_panel_onchange_adapter,
                                     parent=visLayout)

        self.panelLayout.addLayout(visLayout)

    def add_plot_widget(self, label, w, h):
        """
            向plotLayout添加一个绘图小部件，但不需要在其中填充plotItem
            Showgrid属性和样式是根据configs设置的
            “label”参数是plot小部件的名称，而w、h分别指由configs决定plot的宽度和高度
        """

        plotWidget = pg.PlotWidget()
        plotLabel = widgets.QLabel(label, self)

        # 设置 grid
        showGrid = self.Cfg['ShowGrid']
        plotWidget.showGrid(x=showGrid, y=showGrid)

        # 设置 background color
        plotWidget.setBackground(self.Cfg['PlotBgColor'])

        # plot label 的大小样式以及位置
        plotLabel.setStyleSheet(self.Cfg['LabelOneFontStyle'])
        plotLabel.setAlignment(core.Qt.AlignBottom | core.Qt.AlignCenter)

        # 调整 plot 的大小
        plotWidget.resize(w, h)
        plotWidget.setFixedSize(w, h)

        # 可见性设置
        isVisible = self.Cfg[label + 'Visible']
        if isVisible:
            plotWidget.setVisible(True)
            self.VisiblePlotCnt += 1

        # 添加到布局
        self.plotLayout.addWidget(plotLabel)
        self.PlotLabels[label] = plotLabel
        self.plotLayout.addWidget(plotWidget)
        self.PlotWidgets[label] = plotWidget

    def add_checkbox_widget(self, label, checked, handler, parent):
        """
            用模板创建一个复选框小部件，提供了标签、处理程序和父布局
        """
        checkBox = widgets.QCheckBox(label, self)
        checkBox.setChecked(checked)
        checkBox.stateChanged.connect(handler)
        parent.addWidget(checkBox)

    def add_file_menu(self):
        """
            将文件选项添加到菜单中，并与处理文件更改事件的插槽功能绑定
            “get_open_file_handler”提供的槽函数只启动一个对话框
            具体的处理逻辑应由上层调用者“main”提供的ReloadProcessor提供
        """
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileOpenAction = widgets.QAction('&Open', self)
        fileOpenAction.triggered.connect(get_open_file_handler(self, self.ReloadProcessor))
        fileMenu.addAction(fileOpenAction)

    def visible_panel_onchange_adapter(self, s):
        """
            适配器方法更改绘图小部件的可见性。因为调用此方法后plotcount值会更新
            所以很难采用extern slot函数，因此由此适配器替代

            这个适配器使用两个外部处理函数来完成主要的逻辑工作
            实际上，用这种方法做功。采取两步:
            改变图表的可见性
            调整图表的大小以适应变化
        """

        label = self.sender().text()

        # set plot visibility of plot and update count
        self.VisiblePlotCnt = visible_panel_onchange(self.PlotWidgets[label],
                                                     self.PlotLabels[label],
                                                     s,
                                                     self.VisiblePlotCnt)

        # resize the plot size after the size changing
        resize_plots_adaptively(self.PlotWidgets.values(),
                                len(self.PlotWidgets.values()),
                                self.VisiblePlotCnt,
                                self.Cfg['PlotWidth'],
                                self.Cfg['PlotHeight'])
        widgets.QApplication.processEvents()

    def load_datas(self, plotDatas):
        """
            从“main”加载数据到绘图，填充数据到相应的PlotItem
            如果这个方法在文件已经加载时被调用，它将不会构造新的PlotItems，只更新其中的数据
            第一次加载将使用configs来绘图
        """

        for name in plotDatas.keys():
            length = len(plotDatas[name])
            x = np.linspace(0, length, length)  # x坐标

            if self.PlotItems[name] is None:
                # 组合PlotCurveItem和ScatterPlotItem，显示给定x，y数据的绘图线和点
                plotItem = pg.PlotDataItem(x, plotDatas[name], symbol=self.Cfg['Marker'])
                # 填充符号时使用的画笔
                plotItem.setSymbolBrush(pg.mkBrush(color=self.Cfg['MarkerColor']))

                self.PlotItems[name] = plotItem
                self.PlotWidgets[name].addItem(self.PlotItems[name])

                # 初始化可见性
                self.PlotWidgets[name].setVisible(self.Cfg[name + "Visible"])
                self.PlotLabels[name].setVisible(self.Cfg[name + 'Visible'])

            # 已经存在的情况，只需要更新呢内容
            else:
                self.PlotItems[name].setData(x, plotDatas[name])
