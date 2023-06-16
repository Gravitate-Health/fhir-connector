from fs_utils import change_direcotry
from os import system

def execute_sushi(path):
    change_direcotry(path)
    command = "sushi ."
    exit_code = system(command)
    
