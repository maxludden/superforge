# superforge/core/max_yaml.py
import yaml


from pathlib import Path
import oyaml as yaml


from core.base import BASE
from core.log import log

#. Flags

yaml_classes: bool = True
cyamllist = []
yamllist= []


#> Import UnsafeLoader
try:
    from yaml import CUnsafeLoader as Loader
    log.debug("Imported CUnsafeLoader from yaml.")
    unsafe_loader = "CUnsafeLoader"
except ImportError:
    from yaml import UnsafeLoader as Loader
    log.debug("Imported UnsafeLoader from yaml.")
    unsafe_loader = "UnsafeLoader"
    yaml_classes = False


#> Import SafeLoader
try:
    from yaml import CSafeLoader as SafeLoader
    log.debug("Imported CSafeLoader from yaml.")
    safe_loader = "CSafeLoader"
except ImportError:
    from yaml import SafeLoader
    log.debug("Imported SafeLoader from yaml.")
    yamllist.append("SaferLoader")
    yaml_classes = False


#> Import Dumper
try:
    from yaml import CDumper as Dumper
    log.debug("Imported CDumper from yaml.")
    dumper_class = "CDumper"
except ImportError:
    from yaml import Dumper
    log.debug("Imported Dumper from yaml.")
    dumper_class = "Dumper"
    dumper_class = False


#> Import SafeDumper
try:
    from yaml import CSafeDumper as SafeDumper
    log.debug("Imported CDumper from yaml.")
    safe_dumper = "CSafeDumper"
except ImportError:
    from yaml import SafeDumper
    log.debug("Imported Dumper from yaml.")
    safe_dumper = "SafeDumper"
    yaml_classes = False

pyyaml_len = len(yamllist)
if pyyaml_len == 0:
    msg = "Imported YAML with C-Lib bindings from PyYAML. Enhanced performance working with YAML"
else:
    msg = "Imported YAML from PyYAML."
yaml_msg = f"""{msg}

    Unsafe Loader:  {unsafe_loader}
    Safe Loader:    {safe_loader}
    
    Dumper:         {dumper_class}
    SafeDumper:     {safe_dumper}\n"""

def generate_html_path(book: int):
    book_str = str(book).zfill(2)
    html_path = f"{BASE}/books/book{book_str}/html/sg{book}.yaml"
    return html_path

def safe_load(yaml_to_load: str):
    result = yaml.load(yaml_to_load, Loader=SafeLoader)
    return result

def load(yaml_to_load: str):
    result = yaml.load(yaml_to_load, Loader=yaml.UnsafeLoader)
    return result
    
def safe_dump(yaml_to_dump: str, book: int):
    html_path = generate_html_path(book)
    result = yaml.dump(yaml_to_dump, html_path, Dumper=SafeDumper, indent=2)
    return result

def dump(yaml_to_dump: str):
    result = yaml.dump(yaml_to_dump, Dumper=Dumper, indent=2)
    return result
    