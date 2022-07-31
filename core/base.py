from platform import platform

def generate_base():
    if platform() == "Linux":
        ROOT = "home"
    else:
        ROOT = "Users"  # < Mac
    BASE = f"/{ROOT}/maxludden/dev/py/superforge"
    return BASE

BASE = generate_base()