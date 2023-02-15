# microdata-crypt
A repository to encrypt and decrypt dataset files based on Python cryptography package.

This project consists of 3 python scripts:

---
### create_rsa_keys.py

Script to create asymmetric public and private RSA key files:

- microdata_public_key.pem
- microdata_private_key.pem

---
### microdata_encrypt_datasets.py

Script to encrypt datasets, for each dataset:

1. Generates the symmetric key for this dataset.
2. Encrypts dataset using the symmetric key and stores the encrypted file as `<VARIABLE_NAME>.encr`
3. Encrypts symmetric key using the asymmetric rsa public key and stores the encrypted file as `<VARIABLE_NAME>.symkey.encr`

---
### microdata_decrypt_datasets.py

Script to decrypt datasets, for each dataset:

1. Decrypts symmetric key file (`<VARIABLE_NAME>.symkey.encr`) using the asymmetric rsa private key.
2. Decrypts dataset file using the symmetric key and stores the decrypted dataset in `<VARIABLE_NAME>.csv`

---
## Try it yourself

You need to install the python cryptography package first:
```
python3 -m pip install cryptography
```

Test dataset files are provided in `/microdata-crypt/test/dataset`

##### Create the rsa keys:
```
cd /microdata-crypt
python3 rsa/create_rsa_keys.py -r test/rsa
```
The keys are now located in `/microdata-crypt/test/rsa`.
This directory is created if does not exist.

##### Encrypt:
```
python3 encrypt/microdata_encrypt_datasets.py -r test/rsa -d test/dataset -e test/encrypted 
```

The encrypted files are now located in `/microdata-crypt/test/encrypted`.
This directory is created if does not exist.

##### Decrypt:
```
python3 decrypt/microdata_decrypt_datasets.py -r test/rsa -e test/encrypted -d test/decrypted
```
The decrypted files are now located in `/microdata-crypt/test/decrypted`.
This directory is created if does not exist.

---

You may observe that the decrypted files are identical to the original files in `test/dataset`.