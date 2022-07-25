import os
import sys
import platform


PLATFORM = platform.system().lower()
BASE_DIR = os.path.dirname(__file__)
TERRAFORM_PATH = f'lib/terraform_{PLATFORM}'
if PLATFORM == 'windows': 
    TERRAFORM_PATH = f'{TERRAFORM_PATH}.exe'
TERRAFORM_EXECUTABLE_SYSTEM = os.path.join(sys.prefix, TERRAFORM_PATH)
TERRAFORM_EXECUTABLE_LOCAL = os.path.join(BASE_DIR, TERRAFORM_PATH)
TERRAFORM_EXECUTABLE = (
    TERRAFORM_EXECUTABLE_SYSTEM
    if os.path.exists(TERRAFORM_EXECUTABLE_SYSTEM)
    else TERRAFORM_EXECUTABLE_LOCAL
)

def main():
    args = [] if len(sys.argv) < 2 else sys.argv[1:]
    os.execv(TERRAFORM_EXECUTABLE, ['terraform'] + args)