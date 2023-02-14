# microdata-crypt
A repository to encrypt and decrypt dataset files based on Python cryptography package.

This project consists of 3 python scripts:

---
### create_rsa_keys.py

Script to create asymmetric public and private RSA keys.

---
### microdata_encrypt_datasets.py

Script to encrypt datasets, for each dataset:

1. Generates the symmetric key for this dataet.
2. Encrypts dataset using the symmetric key
3. Encrypts symmetric key using the asymmetric public rsa key.

---
### microdata_decrypt_datasets.py

Script to decrypt datasets, for each dataset:

1. Decrypts symmetric key using the asymmetric private rsa key.
2. Decrypts dataset file using the symmetric key.

---
## Try it yourself

Test dataset files are provided in `/microdata-crypt/test/dataset`

##### Create the rsa keys:
```
cd /microdata-crypt
python3 rsa/create_rsa_keys.py -r test/rsa
```
The keys are now located in `/microdata-crypt/test/rsa`

##### Encrypt:
```
python3 encrypt/microdata_encrypt_datasets.py -r test/rsa -d test/dataset -e test/encrypted 
```

The encrypted files are now located in `/microdata-crypt/test/encrypted`

##### Decrypt:
```
python3 decrypt/microdata_decrypt_datasets.py -r test/rsa -e test/encrypted -d test/decrypted
```
The decrypted files are now located in `/microdata-crypt/test/decrypted`

---

You may observe that the decrypted files are identical to the original files in `test/dataset`.