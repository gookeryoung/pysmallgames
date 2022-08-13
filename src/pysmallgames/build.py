import os
import pathlib
import subprocess

if __name__ == '__main__':
    source_dirs = [f for f in pathlib.Path('.').iterdir() if f.is_dir()]
    for source_dir in source_dirs:
        os.chdir(source_dir)
        source_file = source_dir / f'{source_dir.stem}.py'
        options = '--standalone --onefile --windows-disable-console'
        icon = f'--windows-icon-from-ico=assets/{source_file.stem}.ico'
        command = f'python -m nuitka {options} --follow-imports {source_file.name} {icon}'
        subprocess.call(command)
