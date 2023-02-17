import argparse
import os
import tarfile
from pathlib import Path

parser = argparse.ArgumentParser(description='Create tar file')
parser.add_argument('-d', '--directory', help='The directory to tar.', required=True)
parser.add_argument('-n', '--tar_file_name', help='The name of the tar file', required=False)

args = parser.parse_args()

tar_dir = Path(args.directory)
if not os.path.exists(tar_dir):
    print('Need to specify a directory containing the files to tar.')
    raise SystemExit(1)

if len(os.listdir(tar_dir)) == 0:
    print(f'No files found in {tar_dir}.')
    raise SystemExit(1)

tar_file_name = args.tar_file_name
if not tar_file_name:
    tar_file_name = 'my_tar_file'

tar_file_name = tar_file_name if tar_file_name.endswith('.tar') else f'{tar_file_name}.tar'

with tarfile.open(tar_file_name, 'w') as tar:
    for filename in os.listdir(tar_dir):
        if filename.endswith('.encr'):
            fpath = os.path.join(tar_dir, filename)
            tar.add(fpath, arcname=filename)

print(f'Archive {tar_file_name} created.')