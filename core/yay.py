# superforge/yay.py
from os import system
from time import sleep
from subprocess import run, PIPE
from typing import Optional
from json import load
from inspect import getframeinfo, stack

from core.log import log, errwrap

caller_log = log.opt(depth=1)

@errwrap()
def debuginfo(message, level: str = "DEBUG"):
    caller = getframeinfo(stack()[1][0])
    caller_dict = dict(caller.as_dict())
    caller_log.log(level, f"{caller.filename}:{caller.function}:{caller.lineno} - {message}")
    return caller_dict
     
    
def yay(clear: bool = True):
    """
    Celebrates Anything!

    Args:
        `clear` (bool, optional): Whether to clear the console prior to celebrating. Defaults to True.
    """
    if clear == True:
        system("clear")
    sleep(0.75)
    system(
        'for i in {1..10}\ndo\n  open raycast://confetti && echo "Celebrate  🎉"\ndone'
    )


def superyay(clear: bool = True) -> None:
    """
    Excessively Celebrates Anything!

    Args:
        `clear` (bool, optional): Whether to clear the console prior to celebrating. Defaults to True.
    """
    if clear == True:
        system("clear")
    sleep(0.75)
    for i in range(0, 4):
        system(
            'for i in {1..20}\ndo\n  open raycast://confetti && echo "Celebrate  🎉"\ndone'
        )
        sleep(1)


def finished(
    message: Optional[str] | None,
    filename: Optional[str] | None,
    title: str = "SUPERFORGE",
    clear: bool = True,) -> None:

    # > Initialize optional variables
    if message is None:
        receipt = "Code Complete"
    if filename is None:
        with open("../json/run.json", "r") as infile:
            current_run = dict((load(infile)))["last_run"]
            filename = f"Run {current_run}"

    # > Alerter Command
    notification_str = f'alerter -message "{message}" -actions "Open Code", Yay, Dismiss-title "{title}" -subtitle "{filename}"   -closeLabel Dismiss  -sender com.microsoft.VSCode -group code -sound "Crystal" -timeout 15'

    notification_cmd = notification_str.split()

    if clear:
        yay()  # . Confetti!!!!
    else:
        yay(clear=False)  # . Confetti!!!!
    # system(notification_str)
    result = run(notification_cmd, capture_output=True)
    if result.returncode == 0:
        selection = result.stdout.decode("utf-8")
        if selection == "@CONTENTCLICKED":
            system("open -a 'Visual Studio Code'")
            log.info(f"Alerter Returned: {selection}. Opened Visual Studio Code.")
        elif selection == "@ACTIONCLICKED":
            system("open -a 'Visual Studio Code'")
            log.info(f"Alerter Returned: {selection}. Opened Visual Studio Code.")
        elif selection == "@DISMISSED":
            log.info(f"Alerter Returned {selection}. User Dismissed Notification.")
        elif selection == "@TIMEOUT":
            log.info(
                f"Alerter Returned {selection}. Notification Automatically Dismissed."
            )
        else:
            log.info(f"Unknown Response: {selection}")
    else:
        log.warning(f"Alerter Returned: {result.returncode}")
        log.warning(f"Alerter Returned: {result.stderr.decode('utf-8')}")
