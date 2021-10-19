# Put your Python standard libraries here, for instance:
# import sys
# import json
import traceback
from greynoise import GreyNoise
import json

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
API_KEY = KeyRing().get("greynoise")
API_KEY_IN_DDBB = bool(API_KEY)
# Put here the url of "how to get an apikey" instructions
API_KEY_DOC = "https://developer.greynoise.io/docs"
# Put here the key part of the tuple: "key:value". Some sites required you to have one or two kinds of secret and apikeys. Most of all just need the "apikey:value" tuple
# API_KEY_NAMES = ["name_of_the_apikey", "name_of_the_secret"]
# In case of single values, just:
API_KEY_NAMES = ["greynoise"]
#
# <------ /APIKEYS -------->
# If your plugin does not need APIKEYS just remove the last paragraph


# <------ RESOURCE_TARGET ------->

# What kind of resource can this plugin handle on?

# Choices are:

#     Resource.Type.DOMAIN
#     Resource.Type.HASH
#     Resource.Type.IPv4
#     Resource.Type.URL
#     Resource.Type.USERNAME
#     Resource.Type.EMAIL
#     Resource.Type.FILE

# Example, we are going to process information for DOMAINs and EMAILs:

# RESOURCE_TARGET = [ResourceType.DOMAIN, ResourceType.EMAIL]
RESOURCE_TARGET = [ResourceType.IPv4]

# <------ /RESOURCE_TARGET ------->


# <------ PLUGIN IDENTIFICATION ------>

PLUGIN_NAME = "greynoise"
PLUGIN_DESCRIPTION = "A service to detect suspicious behavior behind IPs related to APTs and more"
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
            if not API_KEY:
                print("No API key...!")
                result_status = PluginResultStatus.NO_API_KEY

        query_result = None
 
        resource_type = ResourceType(resource_type)

        if resource_type == ResourceType.IPv4:
            api_client = GreyNoise(api_key=API_KEY, timeout=20, use_cache=True, cache_max_size=1000, cache_ttl=3600)
            try:
                query_result = api_client.ip(target)
                #print(query_result, type(query_result))
                #query_result = format_empty_fields(query_result)
                #print(query_result, type(query_result))
                print(query_result)
                print("whateva")
            except Exception as e:
                tb1 = traceback.TracebackException.from_exception(e)
                query_result = str(tb1.__cause__)
            
        else:
            print(f"[{PLUGIN_NAME}]: Resource type not found")

        if query_result:
            result_status = PluginResultStatus.COMPLETED

        PluginManager.set_plugin_results(
            resource_id, plugin_name, project_id, query_result, result_status
        )

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("BEFORE", tb1)
        print(tb1.__cause__)
        print("".join(tb1.format()))


"""
    Auxiliary functions.

        If you need (and you will) more functions feel free to put it below.
        Do not forget to NOT decorate them like main with @celery_app.task

"""

"""
def format_empty_fields(target):
    for key in target:
        if target[key] == "[]" or target[key] == "{}":
            target[key] = None
        elif target[key]
    target = target.replace("[]", "None")
    target = target.replace("{}", "None")
    return json.loads(target)
"""