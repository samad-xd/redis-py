from executor import executor
from storage import kv_store
from resp import build_simple_string


@executor("TYPE")
def type(command_parts):
    if kv_store.exists(key=command_parts[0]):
        return build_simple_string("string")
    return build_simple_string("none")
