"""
    此模块用于通过配置管理器配置程序设置
    管理器负责从配置文件中读取配置并将更改保存到文件中
    配置值可以通过ConfigManager访问
    可用的设置包含在一个名为ConfigSet的独立类中
"""

import json


class ConfigSet:

    def __init__(self):
        self.MaxFileSize = 200  # the max size of a binary file
        self.ValueVisible = True
        self.DifferentialVisible = True
        self.IntegrateVisible = True
        self.ValueMarker = True
        self.DifferentialMarker = True
        self.IntegrateMarker = True
        self.ShowGrid = True
        self.PlotBgColor = [0, 0, 0]  # black bg in default
        self.PlotCurveColor = [255, 255, 255]  # white curve in default
        self.Marker = 'o'
        self.MarkerColor = [0, 255, 0]
        self.WindowWidth = 2000
        self.WindowHeight = 1000
        self.PlotWidth = 1800
        self.PlotHeight = 250
        self.LabelOneFontStyle = "QLabel{color:rgb(0,0,200);font-size:20px;font-weight:normal;font-family:Arial;}"
        self.LabelTwoFontStyle = "QLabel{color:rgb(0,0,0);font-size:15px;font-weight:normal;font-family:Arial;}"
        self.LabelThreeFontStyle = "QLabel{color:rgb(0,0,0);font-size:18px;font-weight:normal;font-family:Arial;}"

    def isVisible(self, plotName):

        # assert plotName in ['Value','Differential', 'Integrate']
        return self.__getattribute__(plotName + 'Visible')

    def items(self):
        return self.__dict__.items()

    def keys(self):
        return self.__dict__.keys()

    def set(self, k, v):
        self.__dict__[k] = v


class ConfigManager:

    # read config
    def __init__(self, configPath='config.json'):
        self.defaultConfig = ConfigSet()
        self.readConfig = self.loadConfig(configPath)

    def loadConfig(self, path):
        if not path.endswith('.json'):
            return ConfigSet().__dict__
        try:
            with open(path, 'r') as f:
                configs = json.load(f)
                configs = self.checkAndCorrectConfig(configs)
                return configs
        except:
            return ConfigSet().__dict__

    def checkAndCorrectConfig(self, config):
        """
            检查read config中的属性和值，纠正非法值并补充缺失的属性
        """
        checkedConfig = config

        for k, dv in self.defaultConfig.items():
            if k not in checkedConfig.keys():  # expected value not exist in read configs
                checkedConfig[k] = dv

            elif type(checkedConfig[k]) != type(dv):  # illegal data type found in read configs
                print('illegal key in config', k)
                checkedConfig[k] = dv

        for ck in checkedConfig.keys():
            if ck not in self.defaultConfig.keys():  # remove the redundant items
                del checkedConfig[ck]

        return checkedConfig

    def get(self, name):
        return self.readConfig[name]
