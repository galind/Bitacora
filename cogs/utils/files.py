import os

folder_path = os.getcwd()


def get_initial_extensions():
    modules = []
    for folder in os.listdir(f'{folder_path}/cogs/'):
        if folder != 'utils':
            modules.append(f'cogs.{folder}')
    return modules
