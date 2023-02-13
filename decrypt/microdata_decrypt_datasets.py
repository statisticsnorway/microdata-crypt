import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

""" microdata_decrypt_datasets.py

This script ...

It decrypts all csv files placed in ./encrypted 
"""

rsa_dir = '/Users/vak/projects/github/M.2.0/microdata-crypt/rsa'
encrypted_dir = '/Users/vak/projects/github/M.2.0/microdata-crypt/encrypt/encrypted'
decrypted_dir = '/Users/vak/projects/github/M.2.0/microdata-crypt/decrypt/decrypted'


def encrypted_csv_files():
    all_files = os.listdir(encrypted_dir)
    return list(filter(lambda f: f.endswith('.csv.encr'), all_files))


csv_files = encrypted_csv_files()

print(csv_files)

for csv_file in csv_files:
    variable_name = csv_file.split(".")[0]

    # Reads privet key from file
    with open(f'{rsa_dir}/microdata_private_key.pem', "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    # decrypt symkey
    encrypted_symkey = f'{encrypted_dir}/{variable_name}.symkey.encr'
    with open(encrypted_symkey, 'rb') as f:
        symkey = f.read()  # Read the bytes of the encrypted file

    decrypted_symkey = private_key.decrypt(
        symkey,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    print(f'decrypted symkey for {variable_name}: {decrypted_symkey}')

    # decrypt csv file
    with open(f'{encrypted_dir}/{csv_file}', 'rb') as f:
        data = f.read()  # Read the bytes of the encrypted file

    fernet = Fernet(decrypted_symkey)
    try:
        decrypted = fernet.decrypt(data)
        with open(f'{decrypted_dir}/{variable_name}.csv', 'wb') as f:
            f.write(decrypted)  # Write the decrypted bytes to the output file

    # Note: You can delete input_file here if you want
    except InvalidToken as e:
        print(f'ERROR : {variable_name} : Invalid Key - Unsuccessfully decrypted')
