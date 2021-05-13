"""
    用于“main”的实用函数，计算微分和积分
"""


def cal_differential(vals):
    minuend = vals[:-1]  # the next one of vlas
    subtrahend = vals[1:]  # the previous one of vlas

    # 对于离散的值，微分就是减法
    diff = (subtrahend - minuend).tolist()
    # 第一个值从0开始
    diff.insert(0, 0)
    return diff


def cal_integral(vals):
    integral = []
    sum = 0

    # 对于积分，就是加起来
    for val in vals:
        sum += val
        integral.append(sum)

    return integral
