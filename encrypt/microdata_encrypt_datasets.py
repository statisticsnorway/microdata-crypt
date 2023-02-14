import argparse
import os
import sys
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

""" microdata_encrypt_datasets.py

    Script to encrypt datasets, for each dataset
        1. Generates the symmetric key for this dataet.
        2. Encrypts the dataset using the symmetric key
        3. Encrypts the symmetric key using the public rsa key.
"""

parser = argparse.ArgumentParser(description='Encrypt datasets')
parser.add_argument('-r', '--rsa_key_dir', help='The directory containing public key file microdata_public_key.pem')
parser.add_argument('-d', '--dataset_dir', help='The directory containing the dataset files (csv) to encrypt (input).')
parser.add_argument('-e', '--encrypted_dir', help='The directory containing the encrypted files (output).')

args = parser.parse_args()

if not (args.rsa_key_dir and args.dataset_dir and args.encrypted_dir):
    print('All three arguments are expected. Please use -h')
    raise SystemExit(1)

rsa_key_dir = Path(args.rsa_key_dir)
if not rsa_key_dir.exists():
    print('Need to specify a directory containing the rsa keys.')
    raise SystemExit(1)

dataset_dir = Path(args.dataset_dir)
if not dataset_dir.exists():
    print('Need to specify a directory containing the dataset files to encrypt.')
    raise SystemExit(1)

encrypted_dir = Path(args.encrypted_dir)
if not os.path.exists(encrypted_dir):
    os.makedirs(encrypted_dir)

public_key_location = f'{rsa_key_dir}/microdata_public_key.pem'

if not Path(public_key_location).is_file():
    print('microdata_public_key.pem not found.')
    raise SystemExit(1)

# Read public key from file
with open(public_key_location, "rb") as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )

all_files = os.listdir(dataset_dir)
csv_files = list(filter(lambda f: f.endswith('.csv'), all_files))

if len(csv_files) == 0:
    print(f'No csv files found in {dataset_dir}.')
    sys.exit()

for csv_file in csv_files:
    variable_name = csv_file.split(".")[0]

    encrypted_file = f'{encrypted_dir}/{csv_file}.encr'
    encrypted_symkey_file = f'{encrypted_dir}/{variable_name}.symkey.encr'

    # Generate and store symmetric key for this file
    symkey = Fernet.generate_key()

    # Encrypt csv file
    with open(f'{dataset_dir}/{csv_file}', 'rb') as f:
        data = f.read()  # Read the bytes of the input file

    fernet = Fernet(symkey)
    encrypted = fernet.encrypt(data)

    with open(encrypted_file, 'wb') as f:
        f.write(encrypted)

    print(f'Csv file {csv_file} encrypted into  {encrypted_file}')

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

print('Encryption done!')