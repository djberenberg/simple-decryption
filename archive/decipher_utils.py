#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Daniel Berenberg
"""
Helper library for converting substitution encoded text to cipher 
"""
import re
import pickle
import string
import random
import sys, os
from math import log2
from collections import Counter

CLEAR = " " * 80

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
def ngram_distribution(text,n=1, log=True):
    """
    Compute ngram probabilities across a text

    In order to compute the fitness of a cipher solution, we need to compute the probability
    that the deciphered text appears in the English language. This is computed
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

    args:
        :text (str)
        :n (int > 0) - size of the ngrams
        :likelihood (bool) - whether or not to compute log probabilities
    returns:
        :(dict) - mapping from ngrams --> their probabilties
        :(int)  - total number of ngrams
    """
    ngram_counts = Counter(chunks(text,n))

    N = sum(ngram_counts.values())
    if log:
        return {gram:log2(count/N)for gram, count in ngram_counts.items()}, N
    else:
        return {gram:count/N for gram, count in ngram_counts.items()}, N

        
def clean(filename, filt="[^A-Za-z]"):
    """
    clean a text corpus by removing based on the regex defined in `filt`
    args:
        :filename (str) - preverified path to text file
        :filt (str, regex) - the regex to off of whic to base cleaning operation
    returns:
        :(str) - the cleaned text, all lowercase
    """
    with open(filename, "rt") as f:
        text = f.read()
        text = re.sub(filt, "", text).lower()
    
    return text

def mutate(parent):
    """
    mutate a parent by swapping two separate characters in its key
    args:
        :parent (str) - cipher key
    returns:
        :(str) - the mutated parent, a child
    """
    child = list(parent)
    swp1 = swp2 = 0
    while swp1 == swp2:
        swp1, swp2 = random.randint(0, 25), random.randint(0, 25)      
    child[swp1], child[swp2] = child[swp2], child[swp1]
    
    return "".join(child)

def generate_parent():
    """
    helper function to wrap the parent generation routine
    returns:
        :(str) - a parent cipher key
    """
    key = list(string.ascii_lowercase)
    random.shuffle(key)
    return "".join(key)

class Solver(object):
    """
    algorithm for iterating on the cipher
    """

    def __init__(self, ngram_distribution, total_ngrams, gram_length):
        """ 
        args:
            :corpus_file (str) - path to the training corpus
            :n (int > 0) - n gram size 

        raises:
            :FileNotFoundError if corpus path doesn't exist
            :ValueError for n <= 0
        """
        self.ngram_dist = ngram_distribution
        self.N = total_ngrams
        self.gram_len = gram_length

    def score(self, string):
        if not isinstance(string, str):
            raise TypeError("Expected `string` to be str")
        
        total = 0
        for chunk in chunks(string, self.gram_len):
            try:
                p = self.ngram_dist[chunk]
            except KeyError:
                # this chunk did not occur in the training corpus,
                # add it for future use with a low probability
                self.ngram_dist[chunk] = log2(0.0001/self.N)
                p = self.ngram_dist[chunk]
            
            total += p
        return total

    def solve(self, ciphertext, n_iters, verbose=False, seed_parent=None):
        """
        perform the hill climber algorithm on cipher text for some number of iterations
        args:
            :ciphertext (str) - the encrypted text
            :n_iters (int) - number of iterations to run
        returns:
            :(str) - the final decryption key found
            :(float) - the final fitness of that key
        """
        if seed_parent is None:
            top_key = generate_parent() 
        else:
            top_key = seed_parent
        top_fitness = self.score(ciphertext)
        parent = top_key
        
        # hill climbing algorithm
        time_stagnant = i = 0
        while i < n_iters:
            child = mutate(parent)
            decrypted =  SubstitutionCipher(child).decrypt(ciphertext)
            child_fitness = self.score(decrypted)
            if child_fitness > top_fitness:
                if verbose:
                    print(f"\r{CLEAR}\r[{i:5d}], fitness: {child_fitness}", end="")
                parent = child
                top_key = parent
                top_fitness = child_fitness
            else:
                time_stagnant += 1

            i += 1 

        if verbose:
            print(f"\r{CLEAR}\r[>] Final cipher fitness: {top_fitness}")
        return top_key, top_fitness

def export_decrypted_text(key, text):
    final_str = ""
    cipher = SubstitutionCipher(key)
    for ch in text:
        dec = cipher.decrypt(ch.lower())
        if ch.isalpha():
            if ch.isupper():
                final_str += dec.upper() 
            else:
                final_str += dec
        else:
            final_str += ch

    return final_str

def export_cipher(key):
    final_str = ""
    cipher = SubstitutionCipher(key)
    for ch in sorted(cipher.key):
        final_str += f"{ch} -> {cipher.k2a[ch]}\n"
    return final_str

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
        
        self.k2a = dict(zip(self._k, self._alph)) # key      --> alphabet 
        self.a2k = dict(zip(self._alph, self._k)) # alphabet --> key

    @property
    def key(self):
        return "".join(self._k)

    @property
    def alphabet(self):
        return "".join(self._alph)
    
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
