import numpy as np
import pandas as pd
import json
import sys
import os
# import util
import h5py
import pickle


def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


outputdir = 'output/LOS-LOOP-SMALL'
ensure_dir(outputdir)

dataurl = 'input/LOS-LOOP/'
dataname = outputdir + '/LOS-LOOP-SMALL'

# los_dataset = h5py.File(dataurl+'Los_traffic.h5','r')
# los_speed = los_dataset.get('df')['axis0']
geo_id_list = pd.read_csv(dataurl + 'los_speed.csv', header=None, nrows=1)
geo_id_list = np.array(geo_id_list)[0]
los_speed = pd.read_csv(dataurl + 'los_speed.csv')

# -------------------- Create .geo table--------------------------------------
geo = []
for i in range(len(geo_id_list)):
    #            id            type
    geo.append([geo_id_list[i], 'LineString'])
geo = pd.DataFrame(geo, columns=['geo_id', 'type'])
geo.to_csv(dataname + '.geo', index=False)

# -------------------- Create .rel table--------------------------------------
los_adj = pd.read_csv(dataurl + "los_adj.csv", header=None)
adj = np.mat(los_adj)
rel = []
rel_id_counter = 0
for i in range(adj.shape[0]):
    for j in range(adj.shape[1]):
        ###        'rel_id',       'type', 'origin_id',   'destination_id', 'link_weight'
        rel.append([rel_id_counter, 'geo', geo_id_list[i], geo_id_list[j], adj[i, j]])
        rel_id_counter += 1
rel = pd.DataFrame(rel, columns=['rel_id', 'type', 'origin_id', 'destination_id', 'link_weight'])
rel.to_csv(dataname + '.rel', index=False)
# -----------------------------------------------------------------------------------------

# --------------------------Create .dyna table---------------------------------------------
los_speed = pd.read_csv(dataurl + 'los_speed.csv')
speed = np.mat(los_speed)
dyna = []
dyna_id_counter = 0


def num2time(num):
    if num < 288 * 31:
        month = 3
        day = (num) // 288 + 1
    elif num < 288 * (31 + 30):
        month = 4
        day = (num - 288 * 31) // 288 + 1
    elif num < 288 * (31 + 30 + 31):
        month = 5
        day = (num - 288 * (31 + 30)) // 288 + 1
    else:
        month = 6
        day = (num - 288 * (31 + 30 + 31)) // 288 + 1

    hour = (num % 288) // 12
    minute = num % 12

    if (day > 31):
        print(num)
        sys.exit()
    month += 2
    month = '0' + str(month)
    day = str(day) if day > 9 else '0' + str(day)
    hour = str(hour) if hour > 9 else '0' + str(hour)
    minute = str(5 * minute) if 5 * minute > 9 else '0' + str(5 * minute)

    if (minute == '01'):
        print(num)
        sys.exit()
    time = '2012-' + month + '-' + day + 'T' + hour + ':' + minute + ':' + '00Z'
    return time


for j in range(speed.shape[1]):
    for i in range(speed.shape[0]):
        time = num2time(i)
        #               dyna_id,      type,    time, entity_id,     traffic_speed
        dyna.append([dyna_id_counter, 'state', time, geo_id_list[j], speed[i, j]])
        dyna_id_counter += 1
dyna = pd.DataFrame(dyna, columns=['dyna_id', 'type', 'time', 'entity_id', 'traffic_speed'])
dyna.to_csv(dataname + '.dyna', index=False)

# --------------------------Create .json table---------------------------------------------
config = dict()
config['geo'] = dict()
config['geo']['including_types'] = ['LineString']
config['geo']['LineString'] = {}
config['usr'] = dict()
config['usr']['properties'] = {}
config['rel'] = dict()
config['rel']['including_types'] = ['geo']
config['rel']['geo'] = {'link_weight': 'num'}
config['dyna'] = dict()
config['dyna']['including_types'] = ['state']
config['dyna']['state'] = {'entity_id': 'geo_id', 'traffic_speed': 'num'}
json.dump(config, open(outputdir + '/config.json', 'w', encoding='utf-8'), ensure_ascii=False)
