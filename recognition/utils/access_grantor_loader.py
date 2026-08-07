import importlib
import os
from recognition.accessGrantor import AccessGrantor

def load_access_grantor_impl() -> AccessGrantor:
    path = os.environ["ACCESS_GRANTOR"]
    module_name, class_name = path.split(":")
    module = importlib.import_module(module_name)
    grantor_class = getattr(module,class_name)
    grantor_instance = grantor_class()
    if not isinstance(grantor_instance,AccessGrantor):
        raise TypeError(f"{class_name} not AccessGrantor instance")
    return grantor_instance