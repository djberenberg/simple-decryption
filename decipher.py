#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Daniel Berenberg

"""
User facing command line application for deciphering the English simple substitution cipher

This application uses a genetic algorithm to determine the most likely cipher key
for the provided messages. 

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
import decipher_utils as du


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

    parser.add_argument("--ngram-size","-g",
                        dest="ngram",
                        type=intgt0,
                        help="size of ngrams to derive the fitness function of the genetic algorithm",
                        default=4)

    parser.add_argument("--training-corpus","-t",
                        dest="training_corpus",
                        type=exists,
                        help="path to the training corpus of English texts",
                        default="corpus-en.txt")

    parser.add_argument("--iters","-n",
                        dest="n_iters",
                        type=intgt0,
                        help="number of iterations to run for the cipher to decrypt",
                        default=5000)

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
        :(du.Solver) - Solver object containing the storing the data computed
    """
    # build the path to the ngram file that will be used
    ngram_file = os.path.join(cmdline_args.ngram_dir, f"{cmdline_args.ngram}-grams.bin")
    
    # get the log probabilties of ngrams in the training corpus
    if cmdline_args.verbose:
        print(f"\r{du.CLEAR}\r[+] Preparing training corpus", end="", file=sys.stderr)
    cleaned = du.clean(cmdline_args.training_corpus)
        
    prbs, total_ngrams = du.ngram_distribution(ngram_file, cleaned, n=cmdline_args.ngram, log=True)
    if cmdline_args.verbose:
        print(f"\r{du.CLEAR}\r[+] Extracted {cmdline_args.ngram}-grams from {ngram_file}", file=sys.stderr)

    return du.Solver(prbs, total_ngrams, cmdline_args.ngram)
    

def main():
    args = define_args().parse_args()
    test_corpus = du.clean(args.encrypted)
    solver = prepare_solver(args)

    top_key, top_fitness = solver.solve(test_corpus, args.n_iters, verbose=args.verbose)
    if args.verbose:
        print(f"\r{du.CLEAR}\r")
    with open(args.encrypted, "rt") as infile, open(args.decryption_file, "wt") as outfile:
        for line in filter(lambda l: l != "\n", infile.readlines()):
            decoded = du.export_decrypted_text(top_key, line)
            print(decoded, file=outfile)
            #decoded = du.SubstitutionCipher(top_key).decrypt(line.lower())

if __name__ == "__main__":
    main()
