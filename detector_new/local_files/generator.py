import json
from random import random, randint
import time

power_consumption = {
   "data_type": 7,
   "version": 1,
   "mac_address": "00000000000000009",
   "time_zone": "Asia/Tokyo",
   "time_unit_id":10,
   "timestamps":[],
   "data":
        {
         "root_powers":[],
         "estimated":[],
         "probability":[]
      }
}


ts = int(time.time())
for count in range(3600):
    power_consumption["timestamps"].append(ts + count)
    power_consumption["data"]["root_powers"].append(random() * 1000)
    if random() >= 0.5:
        power_consumption["data"]["estimated"].append(1)
    else:
        power_consumption["data"]["estimated"].append(0)
    power_consumption["data"]["probability"].append(randint(1, 100)/100.0)

data = json.dumps(power_consumption)
f = open('power.json', 'w')
f.write(data)
f.close()

waves = {
   "data_type": 8,
   "version": 1,
   "mac_address": "0000000000000009",
   "time_zone": "Asia/Tokyo",
   "time_unit_id":10,
   "timestamps":[],
   "data":
      {
         "waveforms":[],
         "diff":[]
      }

}

for count in range(3600):
    waves["timestamps"].append(ts + count)
    waves["data"]["waveforms"].append([])
    waves["data"]["diff"].append([])
    for count2 in range(64):
        waves["data"]["waveforms"][count].append(random() * 1000)
        waves["data"]["diff"][count].append(random() * 200)


data = json.dumps(waves)
f = open('waveforms.json', 'w')
f.write(data)
f.close()
