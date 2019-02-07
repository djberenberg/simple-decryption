#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Daniel Berenberg
"""
Helper library for converting substitution encoded text to cipher 
"""
import re
import pickle
import string
import sys, os
from math import log
from collections import Counter

__all__ = ["exists","direxists","intgt0","prepare_training_corpus","SubstitutionCipher"]

#### command line "types" ####
def exists(pth):
    """
    asserts a path to a filename exists
    args:
        :pth (str) - the path to verify
    returns:
        :the filename
    raises:
        :FileNotFoundError if the path does not exist
    """
    pth = str(pth)
    if not os.path.exists(pth):
        raise FileNotFoundError(f"{pth} does not found")
    return pth

def direxists(pth):
    """
    verifies the existence of or creates a directory at `pth`
    args:
        :pth - path in question
    returns:
        :the path to the created/verified directory
    """
    pth = str(pth)
    os.makedirs(pth, exist_ok=True)
    return pth

def intgt0(x):
    """
    asserts the input is an integer > 0
    args:
        :x - the data to verify
    returns:
        :the verified data
    raises:
        :TypeError if the provided input cannot be cast to integer
    """

    x = int(x)
    if x <= 0:
        raise TypeError(f"Expected int > 0; got {x}")
    return x


#### helper functions ####
def cache_pickle(handler):
    """
    decorator for caching the output of a computation-intensive
    action to a serialized pickle object for later usage.

    args:
        :handler (function) - returns the data
        handler args:
            :*args - the arguments that handler expects
            :**kwargs - the keyword arguments passable to handler
        returns:
            :the cached data

    usage:

    Suppose we have to perform some computationally intensive action.
    To save that action's output to a text file just define the function
    as follows:

    >>> @cache_pickle
    >>> def comp_intensive_func(arg1, arg2, ..., kwarg1=foo, kwarg2=bar, ...):
    >>>    # ...    
    
    and call it in the following way, assuming we'd like to cache outputs to 'mypickle.bin':

    >>> comp_intensive_func('mypickle.bin', arg1, arg2, ...)
    """
    def wrapper(filename, *args, **kwargs):
        try:
            with open(filename, "rb") as pkf:
                #print("{} is cached!".format(filename), file=sys.stderr)
                return pickle.load(pkf)
        except FileNotFoundError: # the pickle was not found
            out = handler(*args, **kwargs)
            with open(filename, "wb") as pkf:
                pickle.dump(out, pkf)
                #print("cached content to {}".format(filename), file=sys.stderr)
        return out
    
    return wrapper

def chunks(item,chunksize):
    """
    Step through `item`, generating `chunksize` chunks of it. Throw out the last bit
    if there is `chunksize` does not evenly divide `len(item)`
    args:
        :item (indexable; list, tuple, str) - the item to chunkify
        :chunksize (int > 0) - the size of the chunks
    yields:
        :chunks of item of size `chunksize`
    raises:
        :TypeError for item not instance of list, tuple, or str
        :ValueError for chunksize <= 0

    usage:
    
    >>> mystr = "CHUNKME"
    >>> chunkifier = chunks(mystr, 3)
    >>> type(chunkifier)
        generator
    >>> [chunk for chunk in chunkifier]
       ["CHU","HUN","UNK","NKM","KME"] 
    """
    chunksize = int(chunksize)
    if chunksize <= 0:
        raise ValueError("Expected `chunksize` to be > 0")
    if not isinstance(item, (str, list, tuple)):
        raise TypeError(f"Expected item to be of type str, list, or tuple; got {type(item)}")
    
    end = False
    for i in range(0,len(item)):
        chunk = item[i:i+chunksize]
        if len(chunk) != chunksize: # throw away the final bit that isn't size chunksize
            return
        else:
            yield chunk

@cache_pickle
def prepare_training_corpus(corpus_file, ngram=4, filt="[^A-Za-z]"):
    """
    In order to compute the fitness of a cipher solution, we need to compute the likelihood
    that the deciphered text appears in the English language. This likelihood is computed
    with respect to the log probability of n-gram counts.
    
    Suppose we choose n = 4, meaning we will consider 4-gram counts from an English corpus.

    If we are concerned with the fitness of the word "DECIPHER", then its probability
    is the product of 4-gram probs inside of it, i.e

    p(DECIPHER) = p(DECI)*p(ECIP)*p(CIPH)*p(IPHE)*(PHER) = q

    where p(DECI) =  # of times DECI appears in corpus
                     ---------------------------------
                       total # of 4-grams in corpus

    and the log probability of DECIPHER is

    log p(DECIPHER) = log(q) = log(p(DECI)) + log(p(ECIP)) + ...
    --------------------------------------------------------------
    This function cleans a text corpus and extracts the log probabilities of the specified ngrams
    in the corpus. The text is cleaned by removing all non alphabetical characters.

    args:
        :corpus_file (str) - the filename of the training corpus
        :ngram (int > 0) - the size of word chunks to extract
        :filt (str regex) - the characters to keep; allows the potentiality of incorporating non english lettering
    returns:
        :(dict) - mapping from ngrams (str) --> log probabilties (float)
    raises:
        :ValueError for ngram <= 0
        :FileNotFoundError for not found corpus_file
    """
    # validate inputs
    ngram = int(ngram)
    if ngram <= 0:
        raise ValueError("Expected `ngram` > 0")
    if not os.path.exists(corpus_file):
        raise FileNotFoundError(f"Corpus file not found: {corpus_file}")

    with open(corpus_file, "rt") as cf:
        text = cf.read()
        # make remove non alphabetical chars and make them lower case
        text = re.sub(filt,"",text).lower()
    # obtain ngram counts
    ngram_counts = Counter(chunks(text, ngram)) 
    N = sum(ngram_counts.values())

    return {gram:log(count/N) for gram,count in ngram_counts.items()}

#### cipher object ####
class SubstitutionCipher(object):
    """
    SubstitutionCipher object

    Every SubstitutionCipher has `encrypt` and `decrypt` methods for encryption/decryption
    to/from ciphertext
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

        self.k2a = dict(zip(self.k, self.alph)) # key      --> alphabet 
        self.a2k = dict(zip(self.alph, self.k)) # alphabet --> key

    @property
    def key(self):
        return "".join(self.k)

    @property
    def alphabet(self):
        return "".join(self.alph)
    
    def _encode(self,ch,mapping):
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
        return "".join(self._encode(ch, self.k2a) for ch in msg)

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
        return "".join(self._encode(ch, self.a2k) for ch in msg)

    def __str__(self):
        return f"{self.__class__.__name__}(from={self.key}, to={self.alphabet})"

if __name__ == "__main__":
    print("To use this library, use `import decipher_utils as du`")
