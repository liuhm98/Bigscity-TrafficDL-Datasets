import numpy as np
import pandas as pd
import json
import os
import util
import time


outputdir = 'output/PeMSD7(M)'
util.ensure_dir(outputdir)

dataurl = 'input/PeMSD7(M)/'
dataname = outputdir+'/PeMSD7(M)'

dataset = pd.read_csv(dataurl+'PeMSD7_W_228.csv', header=None)
geo = []
for i in range(dataset.shape[0]):
    geo.append([i, 'Point', '[]'])
geo = pd.DataFrame(geo, columns=['geo_id', 'type', 'coordinates'])
geo.to_csv(dataname+'.geo', index=False)


rel = []
reldict = dict()
# dataset = pd.read_csv(dataurl+'PeMSD7_W_228.csv', header=None)
for i in range(dataset.shape[0]):
    for j in range(dataset.shape[1]):
        sid = i
        eid = j
        cost = dataset[i][j]
        if (sid, eid) not in reldict:
            reldict[(sid, eid)] = len(reldict)
            rel.append([len(reldict) - 1, 'geo', sid, eid, cost])
rel = pd.DataFrame(rel, columns=['rel_id', 'type', 'origin_id', 'destination_id', 'weight'])
rel.to_csv(dataname+'.rel', index=False)


dataset = pd.read_csv(dataurl+'PeMSD7_V_228.csv', header=None)

start_time = util.datetime_timestamp('2012-05-01T00:00:00Z')
end_time = util.datetime_timestamp('2012-07-01T00:00:00Z')
timeslot = []
while start_time < end_time:
    if time.localtime(start_time).tm_wday == 5:  # 只考虑周一-周五 遇到周六直接跳到下周一
        start_time = start_time + 2*24*60*60
        if start_time >= end_time:
            break
    timeslot.append(util.timestamp_datetime(start_time))
    start_time = start_time + 5*60

# dyna = []
dyna_id = 0
dyna_file = open(dataname+'.dyna', 'w')
dyna_file.write('dyna_id' + ',' + 'type' + ',' + 'time' + ',' + 'entity_id' + ',' + 'traffic_speed' + '\n')
for j in range(dataset.shape[1]):
    entity_id = j  # 这个数据集的id是0-227
    for i in range(dataset.shape[0]):
        time = timeslot[i]
        # dyna.append([dyna_id, 'state', time, entity_id, dataset[i][j][0], dataset[i][j][1], dataset[i][j][2]])
        dyna_file.write(str(dyna_id) + ',' + 'state' + ',' + str(time)
                        + ',' + str(entity_id) + ',' + str(dataset.iloc[i][j]) + '\n')
        dyna_id = dyna_id + 1
        if dyna_id % 10000 == 0:
            print(str(dyna_id) + '/' + str(dataset.shape[0]*dataset.shape[1]))
dyna_file.close()
# dyna = pd.DataFrame(dyna, columns=['dyna_id', 'type', 'time', 'entity_id', 'traffic_flow'])
# dyna.to_csv(dataname+'.dyna', index=False)


config = dict()
config['geo'] = dict()
config['geo']['including_types'] = ['Point']
config['geo']['Point'] = {}
config['usr'] = dict()
config['usr']['properties'] = {}
config['rel'] = dict()
config['rel']['including_types'] = ['geo']
config['rel']['geo'] = {'weight': 'num'}
config['dyna'] = dict()
config['dyna']['including_types'] = ['state']
config['dyna']['state'] = {'entity_id': 'geo_id', 'traffic_speed': 'num'}
json.dump(config, open(outputdir+'/config.json', 'w', encoding='utf-8'), ensure_ascii=False)
