import os
import numpy as np


def loading(pth, maxSize):
    if os.path.os.path.getsize(pth) / 1024 > maxSize:
        raise ValueError('文件过大')
    elif os.path.os.path.getsize(pth) / 1024 == 0:
        raise ValueError('文件为空')
    try:
        with open(pth, 'rb') as reader:
            file = np.fromfile(reader, dtype=np.int16)  # 读取二进制文件，数据类型为四个字节
            return file
    except:
        raise ValueError('无法打开文件')
