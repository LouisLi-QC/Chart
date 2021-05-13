from PyQt5 import QtWidgets as widgets
import sys

from fileLoader import loading
from window import MainWindow
from config import ConfigManager
from handler import get_open_file_handler
from calculate import cal_differential, cal_integral


class Chart:
    def __init__(self):
        initInfo = widgets.QWidget()

        try:
            self.Data = None
            self.Names = ['Value', 'Differential', 'Integrate']
            self.CfgManager = ConfigManager()
            self.Content = self.load_ini()
            self.Window = MainWindow('Chart', self.Names, self.CfgManager.readConfig, self.Content, self.load)

        # catch异常并退出
        except:
            widgets.QMessageBox.information(initInfo, 'Message', "非正常情况，程序已退出")
            exit(-1)

    def load_ini(self):
        flag = True
        top = widgets.QWidget()
        while flag:
            path = get_open_file_handler(top, lambda x: x)()  # 调用get_open_file_handle打开文件
            if path == '':  # path = null, exit
                exit(0)
            data = self.load(path, auto=False)
            flag = (data is None)

        return data

    def load(self, path, auto=True):
        top = widgets.QWidget()

        try:
            vals = loading(path, self.CfgManager.get('MaxFileSize'))  # 调用loading来读取文件

        # 配置文件错误
        except AttributeError:
            widgets.QMessageBox.information(top, 'Message', "使用了破损的的配置文件！")
            exit(-1)

        # 其他load错误
        except ValueError as exception:
            message = str(exception)
            widgets.QMessageBox.information(top, 'Message', "%s，请选择其他文件！" % message)
            return None

        # calculate 微分和积分
        diffs = cal_differential(vals)
        ints = cal_integral(vals)

        # datas 包括三个，vals, diffs, ints
        datas = {name: val for name, val in zip(self.Names, [vals, diffs, ints])}

        # 画图，显示内容 Content
        if auto:
            self.Window.load_datas(datas)  # 调用window的load_datas来画图
            # update data
            self.Content = datas
        else:
            return datas


if __name__ == '__main__':
    app = widgets.QApplication(sys.argv)  # 实例化一个应用对象
    e = Chart()
    sys.exit(app.exec_())  # 确保主循环安全退出
