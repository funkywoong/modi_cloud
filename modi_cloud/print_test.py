import sys, os
import time

def delete_last_line():
    "Use this function to delete the last line in the STDOUT"

    #cursor up one line
    sys.stdout.write('\x1b[1A')

    #delete last line
    sys.stdout.write('\x1b[2K')

def screen_clear():
    if os.name == 'nt':
      _ = os.system('cls')
   # for mac and linux(here, os.name is 'posix')
    else:
      _ = os.system('clear')


if __name__ == '__main__':
    
    for i in range(0, 10):
        print('hi')
        screen_clear()
        time.sleep(0.01)
        
    