#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Daniel Berenberg
"""
simple_decryption core library. Contains cipher helper functions and 
Cipher class hierarchy
"""

import string
import random
from collections import Counter
from .utils import cache_pickle, chunks

__all__ = ["SubstitutionCipher","AbstractCipher", 
           "export_cipher","export_decrypted_text"]


#### cipher object hierarchy ####
class AbstractCipher(object):
    """
    AbstractCipher is the base class for all Ciphers
    
    Every Cipher has `encrypt` and `decrypt` methods for encryption/decryption
    to/from ciphertext.

    Additionally, Ciphers have a .key and .alphabet attribute to signify 
    their the key they use to encrypt/decrypt texts
    """

    def encrypt(self, msg):
        raise NotImplementedError

    def decrypt(self, msg):
        raise NotImplementedError

    @property
    def key(self):
        return NotImplemented

    @property
    def alphabet(self):
        return NotImplemented
    
    @classmethod
    def encode(cls,ch,mapping):
        """
        internal method to encrypt/decrypt a character with respect to some mappping
        - if the character ought not to be mapped, return the identity

        args:
            :ch (str) - single character  
        returns:
            :(str) the mapped character
        """
        if ch in mapping:
            return mapping[ch]
        return ch

    def __str__(self):
        return f"{self.__class__.__name__}(from={self.key}, to={self.alphabet})"

class SubstitutionCipher(AbstractCipher):
    """
    SubstitutionCipher object

    """
    
    def __init__(self,key,alphabet=string.ascii_lowercase):
        """
        SubstitutionCipher constructor; initializes a cipher with a key
        that maps the target alphabet onto some encoding. 

        args:
            :key (str) - some permutation of the target alphabet
            :alphabet (str, optional) - the target alphabet onto which the key will map 

        raises:
            :AssertionError if there is not a 1-1 mapping from `key` -> `alphabet`
            :AssertionError if either `key` or `alphabet` is not a str
        """
        assert len(set(key)) == len(set(alphabet)), "Bad key; not a 1-1 mapping"
        assert all(lambda s:isinstance(s, str) for s in [key, alphabet]), "Either key or alphabet is not a string"

        self._k, self._alph = map(list, [key, alphabet])
        
        self.k2a = dict(zip(self._k, self._alph)) # key      --> alphabet 
        self.a2k = dict(zip(self._alph, self._k)) # alphabet --> key

    @property
    def key(self):
        return "".join(self._k)

    @property
    def alphabet(self):
        return "".join(self._alph)
    

    def encrypt(self, msg):
        """
        Encrypt a message using the supplied key. For each character in the message, 
        if that character is mappable onto the cipher alphabet, that will be done.
        If the character is not mappable, just ignore it and continue

        args:
            :msg (str) - the message to encrypt; message will be casted to string on input
        returns:
            :(str) - the encrypted message
        """
        msg = str(msg)
        return "".join(self.encode(ch, self.k2a) for ch in msg)

    def decrypt(self, msg):
        """
        Decrypt a message with respect to the supplied key. Step through the `msg` string
        and map characters to their decrypted analog if possible

        args:
            :msg (str) - the message to decrypt, casted to string on input
        returns:
            (str) - the decrypted message
        """
        msg = str(msg)
        return "".join(self.encode(ch, self.a2k) for ch in msg)



# cleanly export of texts/ciphers
def export_decrypted_text(cipher, text, **kwargs):
    """
    export decrypted text to a string for later output
    
    Supply keyword arguments for print() functionality
    args:
        :cipher (inherits .core.AbstractCipher) - the decryption cipher to use
        :text (str) - text to decipher

    returns:
        :None

    raises:
        :TypeError if cipher is not a child of .core.AbstractCipher
    """
    if not isinstance(cipher, AbstractCipher):
        raise TypeError("Expected cipher object")

    final_str = ""
    for ch in text:
        dec = cipher.decrypt(ch.lower())
        if ch.isalpha():
            if ch.isupper():
                final_str += dec.upper() 
            else:
                final_str += dec
        else:
            final_str += ch
    
    print(final_str, **kwargs)

def export_cipher(cipher, **kwargs):
    """
    export cipher to newline delimited <encrypted> -> <decrypted> format

    Supply keyword arguments for print() functionality

    args:
        :cipher (inherits .core.AbstractCipher) - the decryption cipher to use
    returns:
        :None
    raises:
        :TypeError if cipher is not a child of .core.AbstractCipher
    """
    if not isinstance(cipher, AbstractCipher):
        raise TypeError("Expected cipher object")
    final_str = ""
    for ch in sorted(cipher.key):
        final_str += f"{ch} -> {cipher.k2a[ch]}\n"

    print(final_str, **kwargs)
