import argparse
import os
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

""" create_rsa_keys.py

    Script to create public and private rsa keys.
"""

parser = argparse.ArgumentParser(description='Generate RSA keys')
parser.add_argument('-r', '--rsa_key_dir', help='The directory to place the generated keys.', required=True)

args = parser.parse_args()

rsa_key_dir = Path(args.rsa_key_dir)
if not os.path.exists(rsa_key_dir):
    os.makedirs(rsa_key_dir)

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

public_key = private_key.public_key()

microdata_private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

private_key_location = f'{rsa_key_dir}/microdata_private_key.pem'
with open(private_key_location, 'wb') as f:
    f.write(microdata_private_key_pem)

print(f'Stored {private_key_location}')

microdata_public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

public_key_location = f'{rsa_key_dir}/microdata_public_key.pem'
with open(f'{rsa_key_dir}/microdata_public_key.pem', 'wb') as f:
    f.write(microdata_public_key_pem)

print(f'Stored {public_key_location}')
