import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


#Director class
class Scrambling():
    # Set AES mode 
    MODE = AES.MODE_CBC
    # Set keys sizes
    KEY_SIZE = 32
    IV_SIZE = AES.block_size
    HASH_SIZE = 256
    #---------------------------------------------------------------------------------------------------------------------------------
    @classmethod
    def encryptFile(cls, infile: str) -> None:
        """
        Encrypt files with AES-256 and RSA
        Args:
            infile(str): file to be encrypted
        Returns:
            None
        """
        #Generate random bytes keys
        key = get_random_bytes(cls.KEY_SIZE)
        iv = get_random_bytes(cls.IV_SIZE)
        #Import public key
        public = RSA.import_key(open('pub.pem').read())
        #Encrypt the key and iv with RSA
        cipher = PKCS1_OAEP.new(public)
        encrypted_key = cipher.encrypt(key)
        encrypted_iv = cipher.encrypt(iv)
        outfile = infile + '.enc'
        #open binary files 
        with open(infile, 'rb') as infile, \
            open(outfile, 'wb') as outfile:
            #Encryptation by chunks
            cipher = AES.new(key, cls.MODE, iv)
            #write encrypted key and iv
            outfile.write(encrypted_key)
            outfile.write(encrypted_iv)
            finished = False
            while not finished:
                chunk = infile.read(1024 * cls.IV_SIZE)
                #stop condition
                if len(chunk) == 0 or len(chunk) % cls.IV_SIZE != 0:
                    padding_length = (cls.IV_SIZE - len(chunk) % cls.IV_SIZE) or cls.IV_SIZE
                    chunk += (padding_length * chr(padding_length)).encode()
                    finished = True
                #write chunk encrypted    
                outfile.write(cipher.encrypt(chunk))
        #bye
        return None

    #---------------------------------------------------------------------------------------------------------------------------------

    @classmethod
    def decryptFile(cls, infile: str) -> None:
        """
        Decrypt files with AES-256 and RSA
        Args:
            infile(str): file to be decrypted
        Returns:
            None
        """      
        # Decrypt key and iv with RSA
        private = RSA.import_key(open('priv.pem').read())
        cipher = PKCS1_OAEP.new(private)
        outfile = '.'.join(infile.split('.')[:-1])
        #open binary files 
        with open(infile, 'rb') as infile, \
            open(outfile, 'wb') as outfile:
            key = cipher.decrypt( infile.read(cls.HASH_SIZE))  
            iv = cipher.decrypt( infile.read(cls.HASH_SIZE))
            cipher = AES.new(key, cls.MODE, iv)
            next_chunk = b''
            finished = False
            while not finished:
                chunk, next_chunk = next_chunk, cipher.decrypt(infile.read(1024 * cls.IV_SIZE))
                if not next_chunk:
                    padlen = chunk[-1]
                    if isinstance(padlen, str):
                        padlen = ord(padlen)
                        padding = padlen * chr(padlen)
                    else:
                        padding = (padlen * chr(chunk[-1])).encode()

                    if padlen < 1 or padlen > cls.IV_SIZE:
                        raise ValueError("bad decrypt pad (%d)" % padlen)

                    # all the pad-bytes must be the same
                    if chunk[-padlen:] != padding:
                        # this is similar to the bad decrypt:evp_enc.c
                        # from openssl program
                        raise ValueError("bad decrypt")

                    chunk = chunk[:-padlen]
                    finished = True

                outfile.write(chunk)
        #bye
        return None
