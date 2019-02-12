
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Daniel Berenberg

"""
User facing command line application for deciphering the English simple substitution cipher

This application uses the hill climber algorithm to determine the most likely cipher key
for the provided messages. 

One addition to the genetic approach is to verify the decrypted texts against the provided
English texts. This is done by extracting unique tokens from the English texts and verifying
that at least 95% of the decrypted vocabulary is found in the English vocabulary. 

The main source information for developing this application is found in:

    "Solving Substitution Ciphers" by Sam Hasinoff
    [https://people.csail.mit.edu/hasinoff/pubs/hasinoff-quipster-2003.pdf]

This script will output two files:
    (1) The decryption cipher (./cipher.txt by default) in the form of
        <encrypted> -> <decrypted> for each letter in the input alphabet

    (2) The original texts decrypted based on (1), defaulted to ./decrypted.txt 
"""
import re
import string
import random
import sys, os
import argparse
import datetime
import simple_decryption as sd

CLEAR = " " * 80
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
        raise FileNotFoundError(f"{pth} was not found")
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

def define_args():
    """
    Lays out the passable arguments to the application

    returns:
        :(argparse.ArgumentParser) ready to parse the command line
    """
    parser = argparse.ArgumentParser(description="Decrypt substitution-ciphered text")

    parser.add_argument("encrypted",
                        type=exists,
                        help="path to the file containing the ciphertext")

    parser.add_argument("training_corpus",
                        type=exists,
                        help="path to the training corpus of English texts")

    parser.add_argument("--cipher-file","-c",
                        dest="cipher_file",
                        type=str,
                        help="the path to which the app will write the decryption cipher",
                        default="cipher.txt")
    
    parser.add_argument("--decrypted","-d",
                        dest="decryption_file",
                        type=str,
                        help="the path to which the app will write the decrytpted text",
                        default="decrypted.txt")

    parser.add_argument("--ngram-width","-g",
                        dest="ngram",
                        type=intgt0,
                        help="The n-gram window size, defaulted to 4",
                        default=4)

    parser.add_argument("--ngram-location","-l",
                        dest="ngram_dir",
                        type=direxists,
                        help="directory path to look for/store precomputed ngram log probabilities",
                        default="ngrams")

    parser.add_argument("--verbose","-v",
                        dest="verbose",
                        help="Display verbose outputs",
                        action="store_true",
                        default=False)

    return parser

def prepare_solver(cmdline_args):
    """
    Get the log probabilities of the specified ngram lengths

    args:
        :cmdline_args (argparse.Namespace) - the commandline arguments
    returns:
        :(sd.solve.SubstitutionSolver) - Solver object storing the data computed
        :(set of str) - the vocabulary of the training corpus 
    """
    # build the path to the ngram file that will be used
    ngram_file = os.path.join(cmdline_args.ngram_dir, f"{cmdline_args.ngram}-grams.bin")
    
    # get the log probabilties of ngrams in the training corpus
    if cmdline_args.verbose:
        print(f"\r{CLEAR}\r[+] Building {cmdline_args.ngram}-gram language model", end="")
    cleaned, vocab = sd.utils.clean(cmdline_args.training_corpus,return_vocab=True)
        
    prbs, total_ngrams = sd.utils.ngram_distribution(ngram_file, cleaned, n=cmdline_args.ngram, log=True)
    if cmdline_args.verbose:
        print(f"\r{CLEAR}\r[+] Extracted {cmdline_args.ngram}-grams from {cmdline_args.training_corpus}")

    return sd.solve.SubstitutionSolver(prbs, total_ngrams, cmdline_args.ngram), vocab
    
def export_data(cmdline_args, cipher):
    """
    helper function to write final results to disk
    args:
        :cmdline_args (argparse.Namespace) - the original cmdline args
        :cipher (str) - the final cipher
    """
    with open(cmdline_args.encrypted, "rt") as infile, open(cmdline_args.decryption_file, "wt") as outfile:
        for line in filter(lambda l: l != "\n", infile.readlines()):
            sd.core.export_decrypted_text(cipher, line, file=outfile)

    with open(cmdline_args.cipher_file, "wt") as cf:
        sd.core.export_cipher(cipher, file=cf)

def mean(L):
    """
    return the mean of a list
    """
    return sum(L)/len(L)

def proportion_english_text(english_vocab, test_vocab, cipher):
    """
    return the proportion of the `test_vocab` that is found in
    `english_vocab`

    args:
        :english_vocab, test_vocab (set of str) - the texts to verify
        :cipher (sd.core.SubstitutionCipher) - the cipher to decrypt the test text
    returns:
        :(float) - a value in [0, 1] that signifies the proportion of english text found in the test text
    """

    decrypted_texts = set(cipher.decrypt(w) for w in test_vocab)
    return mean([1 if w in english_vocab else 0 for w in decrypted_texts])

def main():

    # parse command line arguments
    args = define_args().parse_args()
    args.n_iters = 5000
    # clean the test corpus for the algorithm to decode
    test_corpus, encrypted_vocab = sd.utils.clean(args.encrypted, return_vocab=True)
    # obtain a du.Solver object for decryption

    # iteratively solve the same problem for 1, 2, 3, and 4-gram language models
    # each solver builds its solution with the key seeded by its predecessor
    then = datetime.datetime.now()

    key = sd.solve.SubstitutionSolver.generate_parent() # initial key
    solver, english_vocab = prepare_solver(args)        # generate the handler that will find solution
    cipher = sd.core.SubstitutionCipher(key)            # the initial cipher
    
    iter_ct = 0
    # the encrypted texts are known to be correct, English prose. We can use
    # the corpus text to verify that the decrypted vocabulary is reasonable
    # by making it function as a dictionary
    while proportion_english_text(english_vocab, encrypted_vocab, cipher) < 0.95:
        cipher, fitness = solver.solve(test_corpus, args.n_iters, verbose=args.verbose) #seed_parent=cipher.key)
        iter_ct +=1

    elapsed = (datetime.datetime.now() - then).seconds

    grammar = {True: "attempts", False: "attempt"}  # print with correct gram
    print(f"\r{CLEAR}\r[>] Decrypted texts in {elapsed} seconds ({iter_ct} {grammar[iter_ct > 1]}).")
    export_data(args, cipher)
    print(f"[>] Wrote cipher to {args.cipher_file}, decrypted texts to {args.decryption_file}")

if __name__ == "__main__":
    main()
