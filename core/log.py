# core/log.py
import functools
import os
import sys
from json import dump, load
from platform import platform
from subprocess import run
from typing import Optional

from loguru import logger
from tqdm.auto import tqdm, trange
from pymongo import monitoring

try:
    from core.base import BASE
except ImportError:
    from base import BASE





#.############################################################
#.                                                          .#
#.      888                                                 .#
#.      888  e88 88e   e88 888     888 88e  Y8b Y888P       .#
#.      888 d888 888b d888 888     888 888b  Y8b Y8P        .#
#.      888 Y888 888P Y888 888 d8b 888 888P   Y8b Y         .#
#.      888  "88 88"   "88 888 Y8P 888 88"     888          .#
#.                      ,  88P     888         888          .#
#.                     "8",P"      888         888          .#
#.                                                          .#
#.############################################################




#>┌─────────────────────────────────────────────────────────────────┐<#
#>│                           Chapter                               │<#
#>└─────────────────────────────────────────────────────────────────┘<#


RUN_PATH = f"{BASE}/json/run.json"
LOG_DIR = "logs/"
MAIN_LOG = "logs.log.md"
LOGGING_LOG = "logs/logging.log"
vertical='│'
horizontal='─'
top_left='┌'
top_right='┐'
bottom_left='└'
bottom_right='┘'
divider_left='├ '
divider_right='┤'
divider_top='┬'
divider_bottom='┴'
divider='┼'
arc_top_left='╭'
arc_top_right='╮'
arc_bottom_left='╰'
arc_bottom_right='╯'
console_set = "INFO"
# console_set = "DEBUG"

def get_last_run():
    """Retrieves the last run.
    
    Returns:
        `last_run` (int):
            The last run
    """
    with open (RUN_PATH, 'r') as infile:
        last_run_dict = dict((load(infile)))
    
    return int(last_run_dict["last_run"])

def increment_run():
    """Increments last_run to get the current run.

    Args:
        `run` (int): 
            last_run
            
    Returns:
        `run` (int)
            The current run.
    """
    last_run = get_last_run()
    return last_run + 1

def get_run():
    """Retrieves the current run.
    
    Returns:
        `run` (int):
            The current run.
    """
    return increment_run()

def write_run(run: Optional[int]):
    """Writes the current run to json file.

    Args:
        `run` (Optional[int]): 
            If provided, writes the inputted int as the current run. 
    """
    if not run:
        run = increment_run()
    run_dict = {"last_run": run}
    with open (RUN_PATH, 'w') as outfile:
        dump(run_dict, outfile, indent=4)

current_run = get_run()
write_run(current_run)
# >#####################################################################
# >                                                                   .#
# >       888                                                         .#
# >       888  e88 88e   e88 888  e88 888  ,e e,  888,8,              .#
# >       888 d888 888b d888 888 d888 888 d88 88b 888 "               .#
# >       888 Y888 888P Y888 888 Y888 888 888   , 888                 .#
# >       888  "88 88"   "88 888  "88 888  "YeeP" 888                 .#
# >                       ,  88P   ,  88P                888 888      .#
# >                      "8",P"   "8",P"                              .#
# >                                                                   .#
# >#####################################################################
def console_fmt(record: dict):
    """
    Generates the format to be used when logging stdout/stderr to the console via 'tqdm.write(msg, end="")'
    
    Args:
        record (dict): 
            A python dict that contains the metadata of the logged message.
            
    Returns:
        record (dict): 
            An updated python dict that contains the metadata of the logged message.
    """
    
    if record["exception"]:
        return """\n<lvl>  {time:h:m:ss.SSS A}  <v>  {level.name: >56}  </v>
┌───────────────┬──────────────┬──────────────────────┬───────────────────────┐
│  <u><i>SUPERFORGE</i></u>   │</lvl>    <w>Run {extra[run]: <5}</w> <lvl>│</lvl> <e>{file.name: ^21}</e><lvl>│ <m>      Line {line: <7} </m>   │
├───────────────┴──────────────┴──────────────────────┴───────────────────────┤
│<v>    𥉉  </v>   EXCEPTION    <v>   𥉉    EXCEPTION    𥉉   </v>   EXCEPTION    <v>    𥉉   </v> │
└─────────────────────────────────────────────────────────────────────────────┘
{exception}</lvl>
"""
    else:
        return """\n<lvl>  {time:h:m:ss.SSS A}  <v>  {level.name: >56}  </v>
┌───────────────┬──────────────┬──────────────────────┬───────────────────────┐
│  <u><i>SUPERFORGE</i></u>   │</lvl>    <w>Run {extra[run]: <5}</w> <lvl>│</lvl> <e>{file.name: ^21}</e><lvl>│ <m>      Line {line: <7} </m>   │
└───────────────┴──────────────┴──────────────────────┴───────────────────────┘
{message}</lvl>
"""

def console_error_flt(record: dict):
    """
    A filtering function that returns messages intended to be displayed on the console via stderr.
    
    Args:
        'record' (dict):
            A python dict that contains the metadata of the logged message.
            
    Returns:
        `record`(dict)
            An updated python dict that contains the a of the logged exception.
    """
    
    lvl = record["level"].no
    if lvl >= 40:
        return record 
    
def console_info_flt(record:dict):
    """
    A filtering function that returns messages intended to be displayed on the console via stdout.
    
    Args:
        'record' (dict):
            A python dict that contains the metadata of the logged message.
            
    Returns:
        `record`(dict)
            An updated python dict that contains the metadata of the logged message.
    """
    lvl = record["level"].name
    if lvl == "INFO":
        return record 
    elif lvl == "WARNING":
        return record
    
def console_debug_flt(record:dict):
    """
    A filtering function that returns messages intended to be displayed on the console via stdout.
    
    Args:
        'record' (dict):
            A python dict that contains the metadata of the logged message.
            
    Returns:
        `record`(dict)
            An updated python dict that contains the metadata of the logged message.
    """
    lvl = record["level"].name
    if lvl == "DEBUG":
        return record
    elif lvl == "INFO":
        return record 
    elif lvl == "WARNING":
        return record

#. Patch main logger
# to truncate exceedingly long filenames generated from ipython
def truncate_filenames(record):
    '''
    Truncate exceedingly long filenames to maintain formatting.

    Args:
        `record` (dict):
            The record dictionary of a logged message.

    Returns:
        `record` (dict): 
            The edited record dictionary of the given message.
    '''
    filename = record['file'].name
    if 'ipython' in filename:
        filename = 'ipython'
    if len(filename) > 20:
        filename = filename[0:17]
    record['file'].name = filename
    return record
    
    
log = logger.patch(truncate_filenames)

#. Initialize Console Sink
log.remove() # removes the default logger provided by loguru
sinks = {}
if console_set == "INFO":
    log.configure(
        handlers=[
            dict(
                sink=(lambda msg: tqdm.write(msg, end="")),
                colorize=True,
                format=console_fmt,
                level="ERROR",
                backtrace=True, 
                diagnose=True,
                catch=True,
                filter=console_error_flt
            ),
            dict(
                sink=lambda msg: tqdm.write(msg, end=""),
                colorize=True,
                format=console_fmt,
                level="DEBUG",
                backtrace=True, 
                diagnose=True,
                
                filter=console_info_flt
            ),
            dict(
                sink=f"{BASE}/logs/supergene.log",
                colorize=False,
                format="Run {extra[run]} │ {time:hh:mm:ss:SSS A} │ {file.name: ^13} │  Line {line: ^5} │ {level: <8}ﰲ  {message}",
                level = "DEBUG",
                backtrace = True,
                diagnose=True
            )
        ],
        
        extra = {
            "run": current_run
        }
    )
elif console_set== "DEBUG":
    log.configure(
        handlers=[
            dict(
                sink=(lambda msg: tqdm.write(msg, end="")),
                colorize=True,
                format=console_fmt,
                level="ERROR",
                backtrace=True, 
                diagnose=True,
                catch=True,
                filter=console_error_flt
            ),
            dict(
                sink=lambda msg: tqdm.write(msg, end=""),
                colorize=True,
                format=console_fmt,
                level="DEBUG",
                backtrace=True, 
                diagnose=True,
                filter=console_debug_flt
            ),
            dict(
                sink=f"{BASE}/logs/supergene.log",
                colorize=False,
                format="Run {extra[run]} | {time:hh:mm:ss:SSS A} | {file.name: ^13} |  Line {line: ^5} | {level: <8}ﰲ  {message}",
                level = "DEBUG",
                backtrace = True,
                diagnose=True
                
            )
        ],
        extra = {
            "run": current_run,
            "function": ""
        }
    )

# >##########################################################
# >                                                         #
# >                                888      Y8b Y88888P     #
# >     888 888 8e   ,"Y88b 888,8, 888 ee    Y8b Y888P      #
# >     888 888 88b "8" 888 888 "  888 P      Y8b Y8P       #
# >     888 888 888 ,ee 888 888    888 b       Y8b Y        #
# >     888 888 888 "88 888 888    888 8b       Y8P         #
# >                                                         #   
# >##########################################################

def md_fmt(record: dict):
    """
    A formatting function that returns the format for writing responsive logs to a markdown file.
    
    Note: For this function to work, at the end of a run of a script the function 'endrun()' must be called.
    """
    
    lvl = str(record["level"].name).lower()
    if lvl == "debug":
        return '''
\<br>
\<a class="debug" href="vscode://file/{file.path}:{line}:1">
    \<div class="card-debug">
        \<div class="header-debug">
            Run {extra[run]} | {time:h:mm:ss A} | {file.name} | Line {line}
        \</div>
        \<div class="container-debug">
            \<pre>
{message}
            \</pre>
        \</div>
    \</div>
\</a>
'''
    elif lvl == 'info':
        return '''
\<br>
\<a class="info" href="vscode://file/{file.path}:{line}:1">
    \<div class="card-info">
        \<div class="header-info">
            Run {extra[run]} | {time:h:mm:ss A} | {file.name} | Line {line}
        \</div>
        \<div class="container-info">
            \<pre>
{message}
            \</pre>
        \</div>
    \</div>
\</a>
'''
    elif lvl == 'warning':
        return '''
\<br>
\<a class="warn" href="vscode://file/{file.path}:{line}:1">
    \<div class="card-warn">
        \<div class="header-warn">
            Run {extra[run]} | {time:h:mm:ss A} | {file.name} | Line {line}
        \</div>
        \<div class="container-warn">
            \<pre>
{message}
            \</pre>
        \</div>
    \</div>
\</a>
'''
    elif lvl == 'error':
        return '''
\<br>
\<a class="error" href="vscode://file/{file.path}:{line}:1">
    \<div class="card-error">
        \<div class="header-error">
            Run {extra[run]} | {time:h:mm:ss A} | {file.name} | Line {line}
        \</div>
        \<div class="container-error">
            \<pre>
{message}
            \</pre>
        \</div>
    \</div>
\</a>
'''
def main_flt(record: dict):
    filename = record['file'].name
    if filename != "log.py'":
        return record


def pwrap(line: str):
    return f"<p>{line}</p>"

def multiline(record):
    return str(record.message).strip()

logger = log.bind(scope="main")
logger.add(
    sink=f"{BASE}/logs/log.md",
    colorize=False,
    level="DEBUG",
    format=md_fmt,
    filter=main_flt,
    rotation="100 MB"
)
logger.patch(multiline)

def fix_tags():
    LOG = f"{BASE}/logs/log.md"

    with open (LOG, 'r') as infile:
        md = infile.read()
        
    fixed_md = md.replace('\<','<')
    with open (LOG, 'w') as outfile:
        outfile.write(fixed_md)
    log.debug("\n\n\n\n")

def test_logger():
    logger.debug("Test the logger DEBUG log.")
    logger.info("Test the logger INFO log.")
    logger.warning("Test the logger WARNING log.")
    logger.error("Test the logger ERROR log.")

def test_log():
    log.debug("Test the DEBUG console log.")
    log.info("Test the INFO console log.")
    log.warning("Test the WARNING console log.")

    @log.catch
    def test_exception():
        return 34/0

    exception = test_exception()


def new_run(test_loggers: bool=False):
    run_json = f'{BASE}/json/run.json'
    md_log = f'{BASE}/logs/log.md'
    
    with open (run_json, 'r') as infile:
        last_run = dict((load(infile)))["last_run"]
        current_run = last_run + 1
        if current_run % 3 == 0:
            # If this run is a multiple of 3: 
            new_log = """# *SUPERFORGE* Log
            
<img src=f"{BASE}/books/book01/Images/gem.gif" alt="gem" width="120" height="60" />

"""
            with open (md_log, 'w') as outfile:
                outfile.write(new_log)
        
    
    with open (md_log, 'a') as outfile:
        outfile.write(f'\n <br> <br> \n \n \n ## Run {current_run}\n<br>\n<img src=f"{BASE}/books/book01/Images/gem.gif" alt="gem" id="gem" width="120" height="60" />\n\n')
    if test_loggers:
        test_logger()
    fix_tags()


def errwrap(*, entry=True, exit=True, level="DEBUG", test: bool=False):
    """Create a decorator that can be used to record the entry, *args, **kwargs,as well ass the exit and results of a decorated function.

    Args:
        entry (bool, optional): 
            Should the entry , *args, and **kwargs of given decorated function be logged? Defaults to True.
            
        exit (bool, optional): 
            Should the exit and the result of given decorated function be logged? Defaults to True.
            
        level (str, optional): 
            The level at which to log to be recorded.. Defaults to "DEBUG".
            
        test (bool, optional):
            Should the logged function be tested? Defaults to False.
    """
    
    def wrapper(func):
        name = func.__name__
        
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            xylog = log.opt(depth=1)
            if test: 
                #> Test run - record entry and exit to test.
                xylog.log (level, f"Entering '{name}'\n<code>\nargs= '{args}'\n\nkwargs={kwargs}</code>")
                result = func(*args, **kwargs)
                xylog.log(level, f"Exiting '{name}'<code>\nresult:\n<{result}</code>")
                return result
            else:
                #> Non-test
                if entry:
                    xylog.log (level, f"Entering '{name}'\n<code>\nargs:\n{args}'\n\nkwargs={kwargs}</code>")
                result = func(*args, **kwargs)
                if exit:
                    xylog.log(level, f"Exiting '{name}'<code>\nresult:\n<{result}</code>")
                return result
        return wrapped
    return wrapper


class CommandLogger(monitoring.CommandListener):
    def started(self, event):
        log.debug("Command {0.command_name} with request id "
            "{0.request_id} started on server "
            "{0.connection_id}".format(event))

    def succeeded(self, event):
        log.debug("Command {0.command_name} with request id "
            "{0.request_id} on server {0.connection_id} "
            "succeeded in {0.duration_micros} "
            "microseconds".format(event))

    def failed(self, event):
        log.debug("Command {0.command_name} with request id "
            "{0.request_id} on server {0.connection_id} "
            "failed in {0.duration_micros} "
            "microseconds".format(event))
            
monitoring.register(CommandLogger())
