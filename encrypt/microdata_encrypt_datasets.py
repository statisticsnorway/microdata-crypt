import os
import shutil
import sys
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

""" microdata_encrypt_datasets.py

This script expects one or more .csv files and the microdata public key to 
reside within current directory.

It encrypts all csv files placing them in ./encrypted 
"""

current_dir = os.getcwd()
encrypted_dir = f'{current_dir}/encrypted'
microdata_public_key = f'{current_dir}/microdata_public_key.pem'


def csv_files_in_current_dir():
    all_files = os.listdir(current_dir)
    return list(filter(lambda f: f.endswith('.csv'), all_files))


csv_files = csv_files_in_current_dir()

if len(csv_files) == 0:
    print('No csv files found in current directory.')
    sys.exit()

path = Path(microdata_public_key)
if not path.is_file():
    print('No public key from microdata found in current directory.')
    sys.exit()

if os.path.exists(encrypted_dir):
    shutil.rmtree(encrypted_dir)
os.makedirs(encrypted_dir)

for csv_file in csv_files:
    variable_name = csv_file.split(".")[0]

    encrypted_file = f'{encrypted_dir}/{csv_file}.encr'
    encrypted_symkey_file = f'{encrypted_dir}/{variable_name}.symkey.encr'

    # Generate and store symmetric key for this file
    symkey = Fernet.generate_key()

    # Encrypt csv file
    with open(csv_file, 'rb') as f:
        data = f.read()  # Read the bytes of the input file

    fernet = Fernet(symkey)
    encrypted = fernet.encrypt(data)

    with open(encrypted_file, 'wb') as f:
        f.write(encrypted)

    print(f'Csv file {csv_file} encrypted into  {encrypted_file}')

    # Read public key from file
    with open(microdata_public_key, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    encrypted_sym_key = public_key.encrypt(
        symkey,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Store encrypted symkey to file
    with open(encrypted_symkey_file, 'wb') as f:
        f.write(encrypted_sym_key)

    print(f'Key file for {csv_file} encrypted into  {encrypted_symkey_file}')
    print("\n")