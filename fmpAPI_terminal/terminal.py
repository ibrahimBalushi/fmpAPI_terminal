import fmpAPI_terminal
path_prefix = fmpAPI_terminal.__path__

from .main import prompt

def main():
    run_ = True
    while run_ == True:
        try:
            # input commandline arguments  
            var = input('fmpAPI terminal$ ').split()
            run_ = prompt(var, run_)

        except Exception as e: raise(e)