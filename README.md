Decipher Task Solution
======================

Table of Contents
-----------------
- [Overview](#overview)
- [How does it work?](#howitworks)
- [Usage on the command line](#usage-cmd)
- [Usage as a library](#usage-lib)
- [Installation](#install)

Overview <a name="overview"/>
--------
This solution includes two main parts:

1. A command line application for solving a substitution cipher.
2. An accompanying library for later scalability and maintenance.

All code was written using Python 3.6 and utilizes the variety of built-in
modules from the Python standard library.

Prior to utilizing the command line application please visit the "Installation"
section of the README for a quick install of the associated code with the command line
script. In short, assuming the directory `simple_decryption/` is just under `./`,
please run `pip install --upgrade ./simple_decryption`.  

How does it work? <a name="howitworks"/>
--------------------
The command-line-intended script `decipher.py` assembles the interface provided
by `simple_decryption` in accomplish the provided task: solve an arbitrary substitution cipher.

The method chosen to solve such a cipher is a slightly modified version of the 
hill-climber algorithm,a genetic approach in which the most elite lineage of successively 
mutated children is followed until the specified number of generations to do so is complete. 

We start with a randomly generated "parent" cipher key and iteratively swap spaces in said
key until the encrypted texts seem "fit". If the space swap makes a more fit text, keep 
the new key and do the  process over again. This process is run for 5000 generations. 

In this case, "fitness" is defined by the 4-gram language model log likelihood of the 
entire, punctuation/spacing removed encrypted text. For each 4-gram from the current 
cipher-decrypted text, compute its log-likelihood (log base 2 of its 4-gram probability) 
based on the input corpus, and sum these likelihoods to estimate the likelihood of the 
decrypted text occurring in English.

The previously mentioned modification comes in after the algorithm has run its course. 
Assuming the input corpus contains reliable prose, we take the vocabulary 
(all unique tokens i.e types) of the final decrypted text and compare it against the 
vocabulary of the input corpus. If less than 95% of the decrypted vocabulary is found
in the input corpus, restart the algorithm over again using the final cipher as the 
"seed key". 

Granted, this modification is susceptible to the notion of a large proportion of OOV texts.
For example, a high volume of medical or scientific terms may not be found in the 
Alice & Wonderland input corpus. In this case, a different corpus may be more advantageous
such as a medical encyclopedia.  

Usage: At the command line <a name="usage-cmd"/>
-------------------
`python decipher.py <encrypted-text> <training-corpus>` 

As stated earlier, this solution utilizes Python 3.6, implying `python` in this
case is linked to a 3.6 executable in the user's PATH variable.

The command line application `decipher.py` takes two positional arguments:
1. The encrypted "test corpus" as a newline-delimited text file.
2. The "training corpus", a volume of prose that is used to train the 
n-gram language model and subsequently verify the decrypted message.

Additionally, `decipher.py` supports five other optional arguments one may provide at will.
Those arguments are:
1. `--cipher-file, -c FILENAME`: the output path to the decryption cipher after
        the encryption has been cracked. Defaults to "./cipher.txt"
2. `--decrypted, -d FILENAME`: the output path to the decrypted texts, defaulted to "./decrypted.txt"
3. `--ngram-location, -l LOCATION`: the output path to cache ngram files for later usage,
     defaulted to "./ngrams/". Each ngram is a dictionary mapping ngrams to log-likelihoods 
    pickled at `$NGRAM_LOCATION/$N-grams.bin` 
4. `--ngram-width, -g WIDTH`: the "n" in "n-gram language model". The window size off of which
     to base ngram log likelihoods. Defaulted to 4. 
5. `--verbose, -v`: display verbose output, defaulted to False

Usage: As a library <a name="usage-lib"/>
------------
The `simple_decryption` library is (hopefully) a scaleable and maintainable piece of software.
To use it, its customary to follow the suggested idiomatic import statement:
    `import simple_decryption as sd`

The library is distributed among 3 separate submodules for the purpose of readability and 
methodical additions in the future:
1. `sd.core`: this submodule is central to decryption; it contains a class hierarchy
    for future decryption ciphers extended from a parent interface called AbstractCipher
    as well as one cipher implementation called SubstitutionCipher. As described in the
    docstring, every cipher object expects `encrypt` and `decrypt` methods to be implemented
    as well as a way to access their "key" (how they translate plaintext to ciphertext),
    the domain of their mapping and an "alphabet", the range of their encrypted -> decrypted
    text mapping. This submodule also contains helper functions for pretty printing the 
    cipher mappings and decrypted cipher text.
2. `sd.utils`: this is a submodule containing miscellaneous helper functions for preparing
    and processing text.
3. `sd.solve`: is a submodule that contains Solver objects for cracking ciphers. The only
    entry into this module is a class called SubstitutionSolver that uses the hill climber
    algorithm mentioned in the "How does it work?" section to solve a substitution cipher.

Installation <a name="install"/>
------------
To install all necessary imports for the command line application to work, please 
change directories so that `simple_decryption/` is just under your working directory
and run:
    `pip install --upgrade ./simple_decryption`

This will install the library into your system's `site_packages` directory so that Python
recognizes it as a package it is able to import. 

