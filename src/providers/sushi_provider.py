from utils.fs_utils import change_directory
from os import system
import logging

logger = logging.getLogger(__name__)

class sushiProvider:
    pass

    def __init__(self) -> None:
        pass

    def execute_sushi(self, path) -> None:
        
        change_directory(path)
        command = "sushi ."

        logger.info("Executing sushi in .fsh folder")
        exit_code = system(command)
        logger.info("Finished executing sushi")
        return None