#!/usr/bin/env python
import os
import stat
import urllib.request
import zipfile
import platform
from setuptools import setup

VERSION = '1.0.1'
TERRAFORM_VERSION = '1.2.5'
PLATFORM_SYSTEM = platform.system().lower()
PLATFORM_CPU = platform.machine().lower()

def download_terraform():
    base_url = f'https://releases.hashicorp.com/terraform/{TERRAFORM_VERSION}'
    file_name = f'terraform_{TERRAFORM_VERSION}_{PLATFORM_SYSTEM}_{PLATFORM_CPU}.zip'
    download_url = f'{base_url}/{file_name}'

    download_directory = 'downloads'
    extract_directory = 'lib'
    target_file = f'{download_directory}/{file_name}'

    os.makedirs(download_directory, exist_ok=True)
    os.makedirs(extract_directory, exist_ok=True)

    if not os.path.exists(target_file):
        urllib.request.urlretrieve(download_url, target_file)

    with zipfile.ZipFile(target_file) as terraform_zip_archive:
        terraform_zip_archive.extractall(extract_directory)

    if PLATFORM_SYSTEM == 'windows': 
        new_executable_path = f'{extract_directory}/terraform_{PLATFORM_SYSTEM}.exe'
        old_executable_path = f'{extract_directory}/terraform.exe'
    else:
        new_executable_path = f'{extract_directory}/terraform_{PLATFORM_SYSTEM}'
        old_executable_path = f'{extract_directory}/terraform'

    if os.path.exists(new_executable_path):
        os.remove(new_executable_path)
    os.rename(old_executable_path, new_executable_path )

    executable_stat = os.stat(new_executable_path)
    os.chmod(new_executable_path, executable_stat.st_mode | stat.S_IEXEC)
    return new_executable_path

executable_path=download_terraform()

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False
except ImportError:
    bdist_wheel = None

setup(
    name='terraform-bin',
    py_modules=['terraform'],
    data_files=[
        (executable_path),
    ],
    entry_points={
        'console_scripts': [
            'terraform = terraform:main',
        ]
    },
)