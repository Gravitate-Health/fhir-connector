from shutil import rmtree
from os import listdir, chdir, mkdir, path


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
    create_directory_if_not_exists(path)
    return chdir(path)


def read_file(path):
    return open(path)


def write_file(path, content):
    f = open(path, "w")
    f.write(content)
    f.close()
    return


def create_directory_if_not_exists(directory_path):
    if not path.exists(directory_path):
        mkdir(directory_path)
    return
