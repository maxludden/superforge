# superforge/yay.py
from os import system
from time import sleep


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
