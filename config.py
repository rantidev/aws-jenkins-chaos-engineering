import urllib
import sys
import os
import json
import io
import requests

project = os.environ['ProjectName']
envi = os.environ['EnvironmentName']
expt = os.environ['ExperimentName']

def read_config_file():
    json_config_path = os.path.join(sys.path[0], project + "/config_"  + envi + ".json")
    return json_config_path
  
def load_config_file():
    config_file_name = read_config_file()
    file = open(config_file_name)
    config_data = json.load(file)
    return config_data
  
data = load_config_file()
print(data['litmus'])
print('DATA : ')
print(data)

