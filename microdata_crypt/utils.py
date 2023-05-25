import os
import shutil
import tarfile
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def tar_dataset(input_dir: Path, dataset_name: str) -> None:
    """
    Creates a tar file from encrypted dataset files.
    Removes the input directory after successful completion.
    :param input_dir: the input directory containing the dataset directory
    :param dataset_name: the name of the dataset
    """

    if not input_dir.exists():
        print("Please specify a directory containing the files to tar")
        raise SystemExit(1)

    if len(list((input_dir / dataset_name).iterdir())) == 0:
        print(f"No files found in {input_dir / dataset_name}")
        raise SystemExit(1)

    tar_file_name = f"{dataset_name}.tar"
    full_tar_file_name = input_dir / tar_file_name
    files_to_tar = [
        input_dir / dataset_name / f"{dataset_name}.csv.encr",
        input_dir / dataset_name / f"{dataset_name}.symkey.encr",
        input_dir / dataset_name / f"{dataset_name}.json",
    ]

    json_file = input_dir / dataset_name / f"{dataset_name}.json"
    if not json_file.exists():
        print(f"The required file {json_file} not found")
        raise SystemExit(1)

    with tarfile.open(full_tar_file_name, "w") as tar:
        for file in files_to_tar:
            if file.exists():
                print(f"Adding {file} to tar..")
                tar.add(file, arcname=file.name)

    shutil.rmtree(input_dir / dataset_name)
    print(f"Archive {full_tar_file_name} created")


def create_rsa_keys(target_dir: Path) -> None:
    """
    Creates public and private RSA keys.
    :param target_dir: directory to place the generated keys
    """

    if not target_dir.exists():
        os.makedirs(target_dir)

    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    public_key = private_key.public_key()

    microdata_private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    private_key_location = target_dir / "microdata_private_key.pem"
    with open(private_key_location, "wb") as file:
        file.write(microdata_private_key_pem)

    print(f"Stored {private_key_location}")

    microdata_public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    public_key_location = target_dir / "microdata_public_key.pem"
    with open(public_key_location, "wb") as file:
        file.write(microdata_public_key_pem)

    print(f"Stored {public_key_location}")
