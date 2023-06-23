import os


def symlink(path_source, path_dest):
    """create (or recreate) symlink"""
    if os.path.islink(path_dest):
        print(f'rm {path_dest}')
        os.remove(path_dest)
    os.symlink(path_source, path_dest)
