from utils.fs_utils import change_directory, create_directory_if_not_exists
from os import system
import logging

logger = logging.getLogger(__name__)

class sushiProvider:
    pass

    def __init__(self) -> None:
        pass

    def execute_sushi(self, path) -> None:
        create_directory_if_not_exists(path)
        change_directory(path)
        command = "sushi ."

        logger.info("Executing sushi in .fsh folder")
        exit_code = system(command)
        logger.info("Finished executing sushi")
        return None