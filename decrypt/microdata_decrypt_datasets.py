import argparse
import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

""" microdata_decrypt_datasets.py

    Script to decrypt datasets, for each dataset
        1. Decrypts the symmetric key using the private key.
        2. Decrypts the dataset file using the symmetric key.
"""

parser = argparse.ArgumentParser(description="Decrypt datasets")
parser.add_argument(
    "-r",
    "--rsa_key_dir",
    help="The directory containing private key file microdata_private_key.pem",
    required=True,
)
parser.add_argument(
    "-e",
    "--encrypted_dir",
    help="The directory containing the encrypted files (input).",
    required=True,
)
parser.add_argument(
    "-d",
    "--decrypted_dir",
    help="The directory containing the decrypted files (output).",
    required=True,
)

args = parser.parse_args()

rsa_key_dir = Path(args.rsa_key_dir)
if not rsa_key_dir.exists():
    print("Need to specify a directory containing the rsa keys.")
    raise SystemExit(1)

encrypted_dir = Path(args.encrypted_dir)
if not encrypted_dir.exists():
    print("Need to specify a directory containing the encrypted files.")
    raise SystemExit(1)

decrypted_dir = Path(args.decrypted_dir)
if not os.path.exists(decrypted_dir):
    os.makedirs(decrypted_dir)

private_key_location = f"{rsa_key_dir}/microdata_private_key.pem"

if not Path(private_key_location).is_file():
    print("microdata_private_key.pem not found.")
    raise SystemExit(1)

# Reads private key from file
with open(private_key_location, "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(), password=None, backend=default_backend()
    )

csv_files = [
    file for file in os.listdir(encrypted_dir) if file.endswith(".csv.encr")
]

if len(csv_files) == 0:
    print(f"No csv.encr files found in {encrypted_dir}.")
    raise SystemExit(1)

for csv_file in csv_files:
    variable_name = csv_file.split(".")[0]

    # decrypt symkey
    encrypted_symkey = f"{encrypted_dir}/{variable_name}.symkey.encr"
    with open(encrypted_symkey, "rb") as f:
        symkey = f.read()  # Read the bytes of the encrypted file

    decrypted_symkey = private_key.decrypt(
        symkey,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # decrypt csv file
    with open(f"{encrypted_dir}/{csv_file}", "rb") as f:
        data = f.read()

    fernet = Fernet(decrypted_symkey)
    try:
        decrypted = fernet.decrypt(data)
        with open(f"{decrypted_dir}/{variable_name}.csv", "wb") as f:
            f.write(decrypted)
    except InvalidToken as e:
        print(
            f"ERROR : {variable_name} : Invalid Key - Unsuccessfully decrypted"
        )

    print(f"Decrypted {csv_file}")

print("Decryption done!")
