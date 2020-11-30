import os
import time
import numpy as np
import pandas as pd
from math import exp

current_time = time.strftime('%d%m%Y_%H%M%S')
def log(record):
    print(record)
    try:
        file = open(f"scale_param_files\\log_sp_{current_time}.txt", "a")
    except:
        os.mkdir("scale_param_files")
        file = open(f"scale_param_files\\log_sp_{current_time}.txt", "a")
    file.write("\n"+str(record)); file.close()

def make_table(data, col_names=["Time", "WS"]):
    log(f"| {col_names[0]} | {col_names[1]} |")
    for dc1, dc2 in data.items():
        log(f"| {dc1} | {dc2} |")

def make_xcl_table(data, col_names=["Time", "WS"], name="ws", sheet_name="Wind Speed", i=""):
    df = pd.DataFrame({col_names[0]: list(data.keys()), col_names[1]: list(data.values())})
    writer = pd.ExcelWriter(f"scale_param_files\\{name}_{i}_{current_time}.xlsx", engine="openpyxl")
    df.to_excel(writer, sheet_name=sheet_name)
    writer.close()

def mlm(ws_time_dict, shape_param_arr):  # Maximum Likelihood Method for scale parameter
    speed_arr = list(ws_time_dict.values())
    shape_scale_params = dict()
    for i in range(len(shape_param_arr)):
        shape_param = shape_param_arr[i]; summ = 0
        for speed in speed_arr:
            s_pow_sp = speed ** shape_param
            summ += s_pow_sp
        scale_param = round((1/len(speed_arr) * summ) ** (1/shape_param), 4)
        shape_scale_params.update([(round(shape_param, 2), scale_param)])
    log("\nGot data:\n"); spa = shape_param_arr
    log(f"Shape parameter = [{round(spa[0], 2)}, {round(spa[-1], 2)}], step: {round(spa[1]-spa[0], 2)}\n")
    make_table(ws_time_dict)
    return shape_scale_params

def speed_estimation(ws_time_dict, shape_scale_params_dict, name=""):
    alpha = min(list(ws_time_dict.values()))
    shape_param = 2.85  # values taken by us
    scale_param = 4.9625
    est_speed = []
    for time, ws in ws_time_dict.items():
        f = (shape_param/scale_param)*((ws-alpha)/scale_param)**(shape_param-1)*exp(-((ws-alpha)/scale_param)**shape_param)
        est_speed.append(f)
    # values will be taken automatically
    # for shape_param, scale_param in shape_scale_params_dict.items():
    #     for time, ws in ws_time_dict.items():
    #         f = (shape_param/scale_param)*((ws-alpha)/scale_param)**(shape_param-1)*exp(-((ws-alpha)/scale_param)**shape_param)
    #         est_speed.append(f)
    df = pd.DataFrame(est_speed)
    writer = pd.ExcelWriter(f"scale_param_files\\se_{name}_{i + 1}.xlsx", engine="openpyxl")
    df.to_excel(writer)
    writer.close()
    return est_speed

ws_safed = {"01:00": 4.12, "02:00": 4.12, "03:00": 5.14, "04:00": 5.14, "05:00": 5.14, "06:00": 6.17, "07:00": 5.14,
            "08:00": 4.12, "09:00": 1.54, "10:00": 3.6, "11:00": 3.09, "12:00": 2.57, "13:00": 3.09, "14:00": 2.06,
            "15:00": 4.12, "16:00": 4.12, "17:00": 4.12, "18:00": 5.14, "19:00": 5.14, "20:00": 5.14, "21:00": 1.54,
            "22:00": 1.03, "23:00": 1.03}

ws_nairobi = {"01:00": 3.09, "02:00": 4.12, "03:00": 5.14, "04:00": 4.12, "05:00": 3.09, "06:00": 3.09, "07:00": 3.09,
              "08:00": 3.09, "09:00": 2.57, "10:00": 5.14, "11:00": 5.14, "12:00": 3.09, "13:00": 7.72, "14:00": 7.72,
              "15:00": 5.14, "16:00": 8.23, "17:00": 4.12, "18:00": 5.14, "19:00": 3.09, "20:00": 3.6, "21:00": 4.12,
              "22:00": 5.14, "23:00": 2.57}

e = 0.05; step = 0.01
b1 = np.arange(1, 1.75+step+e, step)  # b1 (3/2) = [1, 1.75+e]
b2 = np.arange(1.75-e, 2.5+step+e, step)  # b2 (2) = [1.75-e, 2.5+e]
b3 = np.arange(2.5-e, 3+step, step)  # b3 (3) = [2.5-e, 3]
intervals = [b1, b2, b3]

log("Calculations for Safed, Israel:")
for i in range(len(intervals)):
    shape_scale_params = mlm(ws_safed, intervals[i])
    log("\nResulted: ")
    make_table(shape_scale_params, col_names=["shape_p", "scale_p"])
    make_xcl_table(shape_scale_params, col_names=["shape_p", "scale_p"],
                   name="Safed", sheet_name="Shape and Scale", i=f"b{i+1}")
    est_speed = speed_estimation(ws_nairobi, shape_scale_params, name="Safed")

log("\nCalculations for Nairobi, Kenya:")
for i in range(len(intervals)):
    shape_scale_params = mlm(ws_nairobi, intervals[i])
    log("\nResulted: ")
    make_table(shape_scale_params, col_names=["shape_p", "scale_p"])
    make_xcl_table(shape_scale_params, col_names=["shape_p", "scale_p"],
                   name="Nairobi", sheet_name="Shape and Scale", i=f"b{i+1}")
    est_speed = speed_estimation(ws_nairobi, shape_scale_params, name="Nairobi")

# Wind Speed tables
make_xcl_table(ws_safed, i="Safed")
make_xcl_table(ws_nairobi, i="Nairobi")
