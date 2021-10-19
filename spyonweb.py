# Put your Python standard libraries here, for instance:
# import sys
# import json
import traceback,json
from urllib import request, parse
import ipaddress

# Put your external dependencies here, for instance:
# import requets

from tasks.tasks import celery_app
from server.entities.resource_types import ResourceType
from server.entities.plugin_result_types import PluginResultStatus
from server.entities.plugin_manager import PluginManager

# Does your plugin need APIKEYS ?
# <------ APIKEYS -------->
from tasks.api_keys import KeyRing

# replace "YOUR_PLUGIN_NAME" with the name of your plugin
#APP_ID = KeyRing().get("neutrino")

#API_KEY_IN_DDBB = bool(API_KEY)
# Put here the url of "how to get an apikey" instructions
#API_KEY_DOC = "https://www.neutrinoapi.com/signup/"
# Put here the key part of the tuple: "key:value". Some sites required you to have one or two kinds of secret and apikeys. Most of all just need the "apikey:value" tuple
# API_KEY_NAMES = ["name_of_the_apikey", "name_of_the_secret"]
# In case of single values, just:
# API_KEY_NAMES = ["name_of_the_apikey"]

API_NAME = KeyRing().get("spyonweb")
API_KEY_IN_DDBB = bool(API_NAME)
API_KEY_DOC = "https://api.spyonweb.com"
API_KEY_NAMES = ["spyonweb"]

# <------ /APIKEYS -------->
# If your plugin does not need APIKEYS just remove the last paragraph


# <------ RESOURCE_TARGET ------->

# What kind of resource can this plugin handle on?

# Choices are:

#     ResourceType.DOMAIN
#     ResourceType.HASH
#     ResourceType.IPv4
#     ResourceType.URL
#     ResourceType.USERNAME
#     ResourceType.EMAIL
#     ResourceType.FILE

# Example, we are going to process information for DOMAINs and EMAILs:

RESOURCE_TARGET = [ResourceType.IPv4, ResourceType.DOMAIN]
# <------ /RESOURCE_TARGET ------->


# <------ PLUGIN IDENTIFICATION ------>

PLUGIN_NAME = "spyonweb"
PLUGIN_DESCRIPTION = "Checks for all domain names that could be related to an IP address or another domain name"
# <------ /PLUGIN IDENTIFICATION ------>


# <------- PLUGIN CONFIGURATION ------->
# PLUGIN_IS_ACTIVE = True
#     Active as in launching probes. This is, your target will know you are knoing at their gates.
#  PLUGIN_AUTOSTART = False
#     If True, the plugin will be automatically ran when a new resource is added. Be careful with this if your API have a limited rate.
#  PLUGIN_DISABLE = False
#     If True, the plugin neither will be loaded nor will be shown in thethe.
#  PLUGIN_NEEDS_API_KEY = True
#     If True, the plugin needs an APIKEY to work, False otherwise
PLUGIN_IS_ACTIVE = False
PLUGIN_AUTOSTART = False
PLUGIN_DISABLE = False
PLUGIN_NEEDS_API_KEY = True

# <------- /PLUGIN CONFIGURATION ------->


class Plugin:
    def __init__(self, resource, project_id):
        self.project_id = project_id
        self.resource = resource

    def do(self):
        resource_type = self.resource.get_type()

        try:
            to_task = {
                "target": self.resource.get_data()["canonical_name"],
                "resource_id": self.resource.get_id_as_string(),
                "project_id": self.project_id,
                "resource_type": resource_type.value,
                "plugin_name": PLUGIN_NAME,
            }
            main.delay(**to_task)

        except Exception as e:
            tb1 = traceback.TracebackException.from_exception(e)
            print("".join(tb1.format()))


"""
    Main function.

        This is the function where all magic have to happen.

        If your plugin works in a different way for each resource type it
        handle do it like the snippet below.


"""


@celery_app.task
def main(plugin_name, project_id, resource_id, resource_type, target):
    result_status = PluginResultStatus.STARTED
    try:
        if PLUGIN_NEEDS_API_KEY:
            API_KEY = KeyRing().get(PLUGIN_NAME)
            if not (API_KEY):
              print("No App ID key...!")
              result_status = PluginResultStatus.NO_API_KEY

        query_result = None

        resource_type = ResourceType(resource_type)

        if resource_type == ResourceType.IPv4:
            query_result = cleanAndReturn(get_spyonweb_ip(target,API_KEY))
            
        elif resource_type == ResourceType.DOMAIN:
            query_result = cleanAndReturn(get_spyonweb_domain(target,API_KEY))
            print(query_result)
        else:
            print(f"[{PLUGIN_NAME}]: Resource type does not found")

        PluginManager.set_plugin_results(
            resource_id, plugin_name, project_id, query_result, result_status
        )

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))


"""
    Auxiliary functions.

        If you need (and you will) more functions feel free to put it below.
        Do not forget to NOT decorate them like main with @celery_app.task

"""


def get_spyonweb_domain(target,token):

  url = 'https://api.spyonweb.com/v1/domain/'+target+'?access_token='+token

  req = request.Request(url)
  response = request.urlopen(req)
  result = json.loads(response.read().decode("utf-8"))
  result['target'] = target

  return result

def get_spyonweb_ip(target,token):

  url = 'https://api.spyonweb.com/v1/ip/'+target+'?access_token='+token

  req = request.Request(url)
  response = request.urlopen(req)
  result = json.loads(response.read().decode("utf-8"))
  result['target'] = target

  return result

def cleanAndReturn(result):

  results_pruned = {}
  results_pruned['target'] = result['target']

  if(result['status'] == 'found'):
    
    results_pruned['ips'] = dict(result['result']['ip'].items())
    results_pruned['status'] = True

  else:

    results_pruned['status'] = False

  final_result = removeIPsFromIdFields(results_pruned)

  return final_result

# https://stackoverflow.com/questions/28664383/mongodb-not-allowing-using-in-key
# The API returns IPs in the key fields of the json dicts, mongo does not love that.
# Looks like the '.' and '$' characters can't be used as keys for dicts in MongoDB, so I will move the IPs to value fields
def removeIPsFromIdFields(dictToModify):

  stringifiedDict = json.dumps(dictToModify)
  splitDictString = stringifiedDict.split("\"")

  print(splitDictString)

  editedList = []

  for item in splitDictString:
    item = item.replace(".","__")
    editedList.append(item)
  
  
  stringifiedDict = "\"".join(editedList)

  print(stringifiedDict)
  return json.loads(stringifiedDict)