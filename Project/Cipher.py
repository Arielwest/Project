# region ---------------------------- ABOUT ----------------------------
"""
##################################################################
# Created By: Ariel Westfried                                    #
# Date: 01/01/2016                                               #
# Name: Cipher                                                   #
# Version: 1.0                                                   #
# Windows Tested Versions: Win 7 32-bit                          #
# Python Tested Versions: 2.6 32-bit                             #
# Python Environment  : PyCharm                                  #
##################################################################
"""
# endregion

# region ---------------------------- IMPORTS ----------------------------
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Random import get_random_bytes
import pickle
# endregion

# region ---------------------------- CONSTANTS ----------------------------
RSA_KEY_LENGTH = 1024
AES_KEY_LENGTHS = [16, 24, 32]
RSA_BLOCK_SIZE = 128
BLOCK_SEPARATOR = '~'
# endregion

# region ---------------------------- Cipher CLASS ----------------------------


class Cipher(object):
    __signature = False
    __public = False

    # constructor
    def __init__(self, key=None):
        if not key:  # Creates random asymmetrical key
            self.__cipher_object = RSA.generate(RSA_KEY_LENGTH)
            self.asymmetrical = True
        elif key == 'signature':  # creates a random asymmetrical key that functions as a signature
            self.__cipher_object = RSA.generate(RSA_KEY_LENGTH)
            self.__signature = True
            self.asymmetrical = True
        elif isinstance(key, str) and len(key) in AES_KEY_LENGTHS:  # creates symmetrical key with given string
            self.__cipher_object = AES.new(key)
            self.asymmetrical = False
            self.__key = key
        elif isinstance(key, Cipher):  # extracts public key from an existing key
            self.__cipher_object = key.__cipher_object.publickey()
            if key.__signature:
                self.__signature = True
            self.asymmetrical = True
            self.__public = True
        else:
            raise NameError("'key' must be 16, 24 or 32 byte long (or a pubkey object).")

    # the encrypting method
    def encrypt(self, data):
        """
        Input:
                data - the plaintext
        Output:
                Encrypted message
        """
        if self.__signature:
            cipher_data = self.__cipher_object.decrypt(data)
        elif self.asymmetrical:
            cipher_data = ""
            data_parts = [data[i: i + RSA_BLOCK_SIZE] for i in xrange(0, len(data), RSA_BLOCK_SIZE)]
            for part in data_parts:
                cipher_data += self.__cipher_object.encrypt(part, 1)[0].encode('base64') + BLOCK_SEPARATOR
            return cipher_data
        else:
            to_add = 16 - (len(data) % 16)
            data += ' ' * to_add
            cipher_data = self.__cipher_object.encrypt(data)
        return cipher_data.encode('base64')

    # the decrypting method
    def decrypt(self, data):
        """
        Input:
                data - the encrypted data
        Output: plaintext
        """
        if self.__public and not self.__signature:
            raise NameError("Public key cannot decrypt!")
        if self.__signature:
            decrypted = self.__cipher_object.encrypt(data.decode('base64'), 1)[0]
        elif self.asymmetrical:
            decrypted = ""
            for part in data.split(BLOCK_SEPARATOR)[:-1]:
                to_add = self.__cipher_object.decrypt(part.decode('base64'))
                decrypted += to_add
        else:
            data = data.decode('base64')
            decrypted = self.__cipher_object.decrypt(data)
            if ' ' in decrypted:
                decrypted = decrypted.rstrip(' ')
        return decrypted

    # public key generator
    def public_key(self):
        if self.asymmetrical:
            return Cipher(key=self)

    # serialization
    def pack(self):
        if self.asymmetrical:
            return '1' + pickle.dumps(self).encode('base64')
        return '0' + self.__key.encode('base64')

    # alternative constructor for random symmetric key
    @staticmethod
    def random_key():
        return Cipher(get_random_bytes(32))

    # deserialization
    @staticmethod
    def unpack(data):
        asymmetrical = data[0] == '1'
        if not asymmetrical:
            return Cipher(key=data[1:].decode('base64'))
        return pickle.loads(data[1:].decode('base64'))

    # alternative constructor for signature object
    @staticmethod
    def crate_signature():
        return Cipher(key='signature')

    # hashing method
    @staticmethod
    def hash(data):
        md5 = MD5.new(data)
        return md5.hexdigest()

# endregion
