from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Random import get_random_bytes
import pickle

RSA_KEY_LENGTH = 1024
AES_KEY_LENGTHS = [16, 24, 32]
RSA_BLOCK_SIZE = 128
BLOCK_SEPARATOR = '~'


class Cipher(object):
    __signature = False
    __public = False

    def __init__(self, key=None):
        if not key:
            self.__cipher_object = RSA.generate(RSA_KEY_LENGTH)
            self.asymmetrical = True
        elif key == 'signature':
            self.__cipher_object = RSA.generate(RSA_KEY_LENGTH)
            self.__signature = True
            self.asymmetrical = True
        elif isinstance(key, str) and len(key) in AES_KEY_LENGTHS:
            self.__cipher_object = AES.new(key)
            self.asymmetrical = False
            self.__key = key
        elif isinstance(key, Cipher):
            self.__cipher_object = key.__cipher_object.publickey()
            if key.__signature:
                self.__signature = True
            self.asymmetrical = True
            self.__public = True
        else:
            raise NameError("'key' must be 16, 24 or 32 byte long (or a pubkey object).")

    def encrypt(self, data):
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

    def decrypt(self, data):
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

    def public_key(self):
        if self.asymmetrical:
            return Cipher(key=self)

    def pack(self):
        if self.asymmetrical:
            return '1' + pickle.dumps(self).encode('base64')
        return '0' + self.__key.encode('base64')

    @staticmethod
    def random_key():
        return Cipher(get_random_bytes(32))

    @staticmethod
    def unpack(data):
        asymmetrical = data[0] == '1'
        if not asymmetrical:
            return Cipher(key=data[1:].decode('base64'))
        return pickle.loads(data[1:].decode('base64'))

    @staticmethod
    def crate_signature():
        return Cipher(key='signature')

    @staticmethod
    def hash(data):
        md5 = MD5.new(data)
        return md5.hexdigest()
