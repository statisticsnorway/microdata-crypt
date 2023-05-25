from pathlib import Path
import shutil
import tarfile

from microdata_crypt import decrypt_dataset, package_dataset
from microdata_crypt.utils import create_rsa_keys

RSA_KEYS_DIRECTORY = Path("tests/resources/rsa_keys")
INPUT_DIRECTORY = Path("tests/resources/input")
OUTPUT_DIRECTORY = Path("tests/resources/output")


def setup_function():
    shutil.copytree("tests/resources", "tests/resources_backup")


def teardown_function():
    shutil.rmtree("tests/resources")
    shutil.move("tests/resources_backup", "tests/resources")


def test_package_dataset():
    create_rsa_keys(target_dir=RSA_KEYS_DIRECTORY)

    package_dataset(
        rsa_keys_dir=RSA_KEYS_DIRECTORY,
        dataset_dir=Path(f"{INPUT_DIRECTORY}/VARIABLE_1"),
        output_dir=OUTPUT_DIRECTORY,
    )

    result_file = OUTPUT_DIRECTORY / "VARIABLE_1.tar"
    assert result_file.exists()

    with tarfile.open(result_file, "r:") as tar:
        tarred_files = [file.name for file in tar.getmembers()]
        assert "VARIABLE_1.csv.encr" in tarred_files
        assert "VARIABLE_1.symkey.encr" in tarred_files
        assert "VARIABLE_1.json" in tarred_files


def test_decrypt_dataset():
    create_rsa_keys(target_dir=RSA_KEYS_DIRECTORY)

    package_dataset(
        rsa_keys_dir=RSA_KEYS_DIRECTORY,
        dataset_dir=Path(f"{INPUT_DIRECTORY}/VARIABLE_1"),
        output_dir=OUTPUT_DIRECTORY,
    )

    decrypted_dir = OUTPUT_DIRECTORY / "decrypted"
    decrypt_dataset(
        rsa_keys_dir=RSA_KEYS_DIRECTORY,
        input_dir=OUTPUT_DIRECTORY / "VARIABLE_1",
        output_dir=decrypted_dir,
    )
    assert decrypted_dir.exists()

    assert (
        Path(decrypted_dir / "VARIABLE_1.csv").stat().st_size
        == Path(INPUT_DIRECTORY / "VARIABLE_1/VARIABLE_1.csv").stat().st_size
    )
