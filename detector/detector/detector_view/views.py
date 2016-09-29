from django.shortcuts import render
from django.http import HttpResponse
import json
import os
# Create your views here.


def index(request):
    return render(request, 'detector_view/detector.html')


def post_data(request):
    post_request = request.POST
    try:
        if post_request["ts"]:
            wave_data = get_data(waveforms=True)
            data = get_waveforms(wave_data, int(post_request["ts"]))
    except KeyError:
        data = get_data()
        scale_estimated(data)
    except:
        raise
    return return_json_response(data)


def scale_estimated(data, scale=1000):
    data["data"]["estimated"] = [est * scale for est in data["data"]["estimated"]]
    return data


def return_json_response(data):
    json_data = json.dumps(data)
    return HttpResponse(json_data)


def get_waveforms(data, ts):
    half_interval = 5
    return_data = {
        "timestamps": [],
        "data":
        {
         "waveforms": [],
         "diff": []
        }
    }
    position = data["timestamps"].index(ts)
    for count, position in enumerate(range(position - half_interval, position + half_interval)):
        return_data["timestamps"].append(data["timestamps"][position])
        return_data["data"]["waveforms"].append([])
        return_data["data"]["diff"].append([])
        for wave_count in range(64):
            return_data["data"]["waveforms"][count].append(data["data"]["waveforms"][position][wave_count])
            return_data["data"]["diff"][count].append(data["data"]["diff"][position][wave_count])

    return return_data


def get_data(waveforms=False):
    cdir = os.path.abspath(os.path.dirname(__file__))
    if waveforms:
        file_directory = os.path.join(cdir, 'waveforms.json')
    else:
        file_directory = os.path.join(cdir, 'power.json')
    f = open(file_directory, 'r')
    json_data = f.read()
    data = json.loads(json_data)
    f.close()
    return data
