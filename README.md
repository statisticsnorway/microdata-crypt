# microdata-crypt
A repository to package datasets based on Python cryptography package.
The datasets will be encrypted and packaged as tar archives. The process is as follows:

1. Generate the symmetric key for a dataset.
2. Encrypt the dataset data (CSV) using the symmetric key and store the encrypted file as `<DATASET_NAME>.csv.encr`
3. Encrypt the symmetric key using the asymmetric rsa public key and store the encrypted file as `<DATASET_NAME>.symkey.encr`
4. Gather the encrypted CSV, encrypted symmetric key and metadata (JSON) file in one tar file.

## Usage

Once you have your metadata and data files ready to go, they should be named and stored like this:
```
my-input-directory/
    MY_DATASET_NAME/
        MY_DATASET_NAME.csv
        MY_DATASET_NAME.json
```

Then use pip to install cryptography package:
```
python3 -m pip install cryptography
```

In your Python script you can then write:
```py
from pathlib import Path
from microdata_crypt import package_dataset
from microdata_crypt.utils import create_rsa_keys

RSA_KEYS_DIRECTORY = Path("tests/resources/rsa_keys")
DATASET_DIRECTORY = Path("tests/resources/input/DATASET_1")
OUTPUT_DIRECTORY = Path("tests/resources/output")

# Create RSA private and public keys for testing purposes
create_rsa_keys(target_dir=RSA_KEYS_DIRECTORY)

package_dataset(
    rsa_keys_dir=RSA_KEYS_DIRECTORY,
    dataset_dir=DATASET_DIRECTORY,
    output_dir=OUTPUT_DIRECTORY,
)
```
and run the script (assuming the script is located in the root directory of this project):
```
python my-script.py
```

You can also use the `package_datasets` function that will package many datasets at once:
```py
package_datasets(
    rsa_keys_dir=RSA_KEYS_DIRECTORY,
    datasets_dir=DATASETS_DIRECTORY,
    output_dir=OUTPUT_DIRECTORY,
)
```

As an additional function, you can also decrypt the encrypted dataset:
```py
decrypt_dataset(
    rsa_keys_dir=RSA_KEYS_DIRECTORY,
    input_dir=OUTPUT_DIRECTORY / "DATASET_1",
    output_dir=decrypted_dir,
)
```

Please check the function documentation of `create_rsa_keys`, `package_dataset(s)` and `decrypt_dataset` for more details.
