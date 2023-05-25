import os
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding


def encrypt_dataset(
    rsa_keys_dir: Path, dataset_dir: Path, output_dir: Path
) -> str:
    """
    Encrypts a dataset as follows:
        1. Generates the symmetric key for this dataset.
        2. Encrypts the dataset using the symmetric key.
        3. Encrypts the symmetric key using the public rsa key.
    """

    if not rsa_keys_dir.exists():
        print("The RSA keys directory has to exist.")
        raise SystemExit(1)

    if not dataset_dir.exists():
        print(
            "The directory containing the dataset files to encrypt has to exist."
        )
        raise SystemExit(1)

    if not output_dir.exists():
        os.makedirs(output_dir)

    public_key_location = rsa_keys_dir / "microdata_public_key.pem"

    if not public_key_location.is_file():
        print(f"Public key {public_key_location} not found.")
        raise SystemExit(1)

    # Read public key from file
    with open(public_key_location, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(), backend=default_backend()
        )

    csv_files = [
        file for file in dataset_dir.iterdir() if file.suffix == ".csv"
    ]

    if len(csv_files) == 0:
        print(f"No csv files found in {dataset_dir}.")
        raise SystemExit(1)

    if len(csv_files) > 1:
        print(f"There should only be one csv file in {dataset_dir}.")
        raise SystemExit(1)

    csv_file = csv_files[0]
    dataset_name = csv_file.stem

    if dataset_name != dataset_dir.stem:
        print(
            f"The csv file name {dataset_name} should match the dataset directory name {dataset_dir.stem}."
        )
        raise SystemExit(1)

    dataset_output_dir = output_dir / dataset_name
    os.makedirs(dataset_output_dir)

    encrypted_file = dataset_output_dir / f"{dataset_name}.csv.encr"
    encrypted_symkey_file = dataset_output_dir / f"{dataset_name}.symkey.encr"

    # Generate and store symmetric key for this file
    symkey = Fernet.generate_key()

    # Encrypt csv file
    with open(csv_file, "rb") as f:
        data = f.read()  # Read the bytes of the input file

    fernet = Fernet(symkey)
    encrypted = fernet.encrypt(data)

    with open(encrypted_file, "wb") as f:
        f.write(encrypted)

    print(f"Csv file {csv_file} encrypted into {encrypted_file}")

    encrypted_sym_key = public_key.encrypt(
        symkey,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Store encrypted symkey to file
    with open(encrypted_symkey_file, "wb") as f:
        f.write(encrypted_sym_key)

    print(f"Key file for {csv_file} encrypted into {encrypted_symkey_file}")
    print("Encryption done!")

    return dataset_output_dir
