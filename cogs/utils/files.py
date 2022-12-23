import os

folder_path = os.getcwd()

ignored_extensions = ['utils']


def get_initial_extensions():
    extensions_list = []
    for extension in os.listdir(f'{folder_path}/cogs/'):
        if extension not in ignored_extensions:
            extensions_list.append(f'cogs.{extension}')
    return extensions_list
