from shutil import rmtree
from os import listdir, chdir


def delete_folder(path):
    return rmtree(path)


def list_directory_files(path):
    return listdir(path)


def list_directory_files_paths(path):
    files = list_directory_files(path)
    paths = []
    for filename in files:
        paths.append(f"{path}/{filename}")
    return paths


def change_directory(path):
    return chdir(path)


def read_file(path):
    return open(path)
