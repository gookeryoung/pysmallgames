import os
import pathlib
import subprocess

games = ['snake']

if __name__ == '__main__':
    source_dirs = [pathlib.Path(game) for game in games]
    for source_dir in source_dirs:
        os.chdir(source_dir)
        source_file = source_dir / f'{source_dir.stem}.py'
        options = '--standalone --onefile --windows-disable-console'
        icon = f'--windows-icon-from-ico=assets/{source_file.stem}.ico'
        command = f'python -m nuitka {options} --follow-imports {source_file.name} {icon}'
        subprocess.call(command)
