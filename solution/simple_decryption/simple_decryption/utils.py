#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Daniel Berenberg

"""
Helper library for simple_decryption lib.
"""
import re
import pickle
import string
import sys, os
from math import log2
from collections import Counter

__all__ = ["cache_pickle","chunks","clean","ngram_distribution"]

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

 
def clean(filename,filt="[^A-Za-z]",return_vocab=False):
    """
    clean a text corpus by removing chars based on the regex defined in `filt`
    args:
        :filename (str) - preverified path to text file
        :filt (str, regex) - the regex to off of whic to base cleaning operation
        :return_vocab (bool) - return the text vocabulary, all unique types of the corpus 
    returns:
        :(str) - the cleaned text, all lowercase
        :(set of str) - if return_vocab enabled, the set of unique tokens of the corpus
    """
    with open(filename, "rt") as f:
        text = f.read()
        if return_vocab:
            text = re.sub(filt, " ", text).lower()
            voc = set(text.split())
            text = re.sub(" ", "", text)
            return text, voc
        else:
            text = re.sub(filt, "", text).lower()
            return text

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
