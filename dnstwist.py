import json
import traceback
import os
import subprocess

from server.entities.plugin_manager import PluginManager
from server.entities.resource_types import ResourceType
from server.entities.plugin_result_types import PluginResultStatus
from tasks.tasks import celery_app
from dns import resolver, reversename


# Which resources are this plugin able to work with
RESOURCE_TARGET = [ResourceType.DOMAIN]

# <------ PLUGIN IDENTIFICATION ------>

PLUGIN_NAME = "dnstwist"
PLUGIN_DESCRIPTION = "Detect suspiciously similar domain names trying to imitate the target one"
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
PLUGIN_NEEDS_API_KEY = False
# Plugin Metadata {a description, if target is actively reached and name}

API_KEY = False
API_KEY_IN_DDBB = False
API_KEY_DOC = None
API_KEY_NAMES = []

print("hello0")

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
    print("hello1")
    try:
        if PLUGIN_NEEDS_API_KEY:
            API_KEY = KeyRing().get(PLUGIN_NAME)
            if not (USER_ID and SECRET_KEY):
              print("No App ID key...!")
              result_status = PluginResultStatus.NO_API_KEY
        print("hello2")
        query_result = None

        resource_type = ResourceType(resource_type)

        if resource_type == ResourceType.DOMAIN:
            query_result = get_dnstwist(target)
            print("hello3")
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


def get_dnstwist(target):
  bashCmd = ["dnstwist", "-f", "json", "-r", target]
  process = subprocess.Popen(bashCmd, stdout=subprocess.PIPE)
  output, error = process.communicate()
  return json.loads(output)