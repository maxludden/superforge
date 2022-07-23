# superforge/yay.py
from os import system
from time import sleep
from subprocess import run, PIPE
from typing import Optional
from json import load

try:
    from core.log import log, errwrap
except ImportError:
    from log import log, errwrap

def yay(celebrate: bool=True):
    if celebrate == True:
        system("clear")
        sleep(0.75)
        system('for i in {1..10}\ndo\n  open raycast://confetti && echo "Celebrate  🎉"\ndone')


def superyay(celebrate: bool=True):
    if celebrate == True:
        system("clear")
        sleep(0.75)
        for i in range(0,4):
            system('for i in {1..20}\ndo\n  open raycast://confetti && echo "Celebrate  🎉"\ndone')
            sleep(1)

        
def finished(
    message: Optional[str]|None,  
    filename:Optional[str]|None,
    title: str = "SUPERFORGE") -> None:
    if message is None:
        receipt = "Code Complete"
    if filename is None:
        with open ("../json/run.json", 'r') as infile:
            current_run = dict((load(infile)))["last_run"]
            filename = f"Run {current_run}"
            
    #> Command Strings
    # cd_cmd_str = f'workon supergene && cdproject;'

    notification_str = f'alerter -message \"{message}\" -actions \"Open Code\", Yay, Dismiss-title \"{title}\" -subtitle \"{filename}\"   -closeLabel Dismiss  -sender com.microsoft.VSCode -group code -sound "Crystal"'
    
    # #> Commands
    # cd_cmd = cd_cmd_str.split()
    # yay_cmd = yay_cmd_str.split()
    notification_cmd = notification_str.split()


    yay()
    # system(notification_str)
    result = run( notification_cmd, capture_output=True)
    if result.returncode == 0:
        selection = result.stdout.decode('utf-8')
        log.info(f"Selected Action: {selection}")
        if selection == "@CONTENTCLICKED" | selection == "@ACTIONCLICKED":
            system("open -a 'Visual Studio Code'")
        
                
                
finished ("Test", 'yay.py')
