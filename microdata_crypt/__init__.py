import logging
import os
import shutil
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from microdata_crypt.encrypt import encrypt_dataset
from microdata_crypt.utils import tar_dataset

logger = logging.getLogger()


def package_dataset(
    rsa_keys_dir: Path,
    dataset_dir: Path,
    output_dir: Path,
) -> None:
    """
    Encrypt a dataset and tar the resulting files.
    Only the CSV file will be encrypted.

    :param rsa_key_dir: directory containing public key file microdata_public_key.pem
    :param dataset_dir: directory containing the dataset files (CSV and JSON)
    :param output_dir: directory to encrypt to
    :return: None
    """

    dataset_output_dir = encrypt_dataset(
        rsa_keys_dir=rsa_keys_dir,
        dataset_dir=dataset_dir,
        output_dir=output_dir,
    )
    dataset_name = dataset_dir.stem
    shutil.copyfile(
        dataset_dir / f"{dataset_name}.json",
        dataset_output_dir / f"{dataset_name}.json",
    )
    tar_dataset(input_dir=output_dir, dataset_name=dataset_name)


def package_datasets(
    rsa_keys_dir: Path,
    datasets_dir: Path,
    output_dir: Path,
) -> None:
    """
    Encrypt multiple datasets and tar the resulting files.
    Only the CSV file will be encrypted.

    :param rsa_key_dir: directory containing public key file microdata_public_key.pem
    :param datasets_dir: directory containing the datasets
    :param output_dir: directory to encrypt to
    :return: None
    """
    if not datasets_dir.exists():
        print("The directory containing the datasets has to exist")
        raise SystemExit(1)
    for dataset in datasets_dir.iterdir():
        if not datasets_dir.is_dir():
            print(f"{datasets_dir} is not a directory")
            raise SystemExit(1)
        package_dataset(
            rsa_keys_dir=rsa_keys_dir,
            dataset_dir=dataset,
            output_dir=output_dir,
        )


def decrypt_dataset(
    rsa_keys_dir: Path, input_dir: Path, output_dir: Path
) -> None:
    """
    Decrypts a dataset as follows:
        1. Decrypts the symmetric key using the private key.
        2. Decrypts the dataset file using the symmetric key.

    :param rsa_keys_dir: directory containing private key file microdata_private_key.pem
    :param input_dir: directory containing the encrypted dataset file (.encr) and encrypted symmetric key
    :param output_dir: directory to decrypt to
    :return: None
    """

    if not rsa_keys_dir.exists():
        print("The RSA keys directory has to exist")
        raise SystemExit(1)

    if not input_dir.exists():
        print("The directory containing the encrypted files has to exist")
        raise SystemExit(1)

    if not output_dir.exists():
        os.makedirs(output_dir)

    private_key_location = rsa_keys_dir / "microdata_private_key.pem"

    if not private_key_location.is_file():
        print(f"{private_key_location} not found")
        raise SystemExit(1)

    # Reads private key from file
    with open(private_key_location, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(), password=None, backend=default_backend()
        )

    csv_file = next(
        file for file in input_dir.iterdir() if str(file).endswith(".csv.encr")
    )

    if csv_file is None:
        print(f"No file with .csv.encr extenstion found in {input_dir}")
        raise SystemExit(1)

    dataset_name = input_dir.stem

    # decrypt symkey
    encrypted_symkey = input_dir / f"{dataset_name}.symkey.encr"
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
    with open(csv_file, "rb") as f:
        data = f.read()

    fernet = Fernet(decrypted_symkey)
    try:
        decrypted = fernet.decrypt(data)
        with open(output_dir / f"{dataset_name}.csv", "wb") as f:
            f.write(decrypted)
    except InvalidToken as exc:
        print(f"ERROR : {dataset_name} : Invalid key")
        raise SystemExit(1) from exc

    print(f"Decrypted {csv_file}")
    print("Decryption done!")


__all__ = ["package_dataset", "decrypt_dataset"]
