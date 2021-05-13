from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core


def resize_plots_adaptively(plot_widgets, plot_total_cnt, plot_cnt, plot_w, plot_h):
    """
        调整plot小部件的大小以适应更改。
        提供了小部件和大小
    """
    if plot_cnt != 0:
        plotHeight = plot_h * plot_total_cnt / plot_cnt
        for plot in plot_widgets:
            plot.resize(plot_w, plotHeight)
            plot.setFixedSize(plot_w, plotHeight)


def visible_panel_onchange(widget, label, state, cnt):
    """
        重置小组件和标签的可见性
    """
    if state == core.Qt.Checked:
        widget.setVisible(True)
        label.setVisible(True)
        return cnt + 1
    else:
        widget.setVisible(False)
        label.setVisible(False)
        return cnt - 1


def get_open_file_handler(window, processor):
    """
        在窗口中打开文件
    """
    def showFileDialog():
        filename = widgets.QFileDialog.getOpenFileName(window, 'Open file', '/')  # 第一个返回值是文件路径，第二个是文件类型
        return processor(filename[0])

    return showFileDialog
