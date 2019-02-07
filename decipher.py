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
import sys, os
import argparse
import decipher_utils as du

CLEAR = " " * 80

def define_args():
    """
    Lays out the passable arguments to the application

    returns:
        :(argparse.ArgumentParser) ready to parse the command line
    """
    parser = argparse.ArgumentParser(description="Decrypt substitution-ciphered text")

    parser.add_argument("encrypted",
                        type=du.exists,
                        help="path to the file containing the ciphertext")

    parser.add_argument("--ngram-size","-g",
                        dest="ngram",
                        type=du.intgt0,
                        help="size of ngrams to derive the fitness function of the genetic algorithm",
                        default=4)

    parser.add_argument("--training-corpus","-t",
                        dest="corpus",
                        type=du.exists,
                        help="path to the training corpus of English texts",
                        default="corpus-en.txt")

    parser.add_argument("--iters","-n",
                        dest="n_iters",
                        type=du.intgt0,
                        help="number of iterations to run for the cipher to decrypt",
                        default=1000)

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
                        type=du.direxists,
                        help="directory path to look for/store precomputed ngram log probabilities",
                        default="ngrams")

    return parser

def logprobs(cmdline_args):
    """
    Get the log probabilities of the specified ngram lengths
    args:
        :cmdline_args (argparse.Namespace) - the commandline arguments

    returns:
        :(dict) - mapping from ngrams found in the corpus file to their log probabilities
    """
    # build the path to the ngram file that will be used
    ngram_file = os.path.join(cmdline_args.ngram_dir, f"{cmdline_args.ngram}-grams.bin")
    
    # get the log probabilties of ngrams in the training corpus
    print(f"\r{CLEAR}\r[+] Preparing training corpus", end="", file=sys.stderr)
    ngram_probs = du.prepare_training_corpus(ngram_file, cmdline_args.corpus, ngram=cmdline_args.ngram) 
    print(f"\r{CLEAR}\r[+] Training corpus prepared", file=sys.stderr)
    return ngram_probs
    # build the path to the ngram file that will be used
    ngram_file = os.path.join(cmdline_args.ngram_dir, f"{cmdline_args.ngram}-grams.bin")
    
    # get the log probabilties of ngrams in the training corpus
    print(f"\r{CLEAR}\r[+] Preparing training corpus", end="")
    ngram_probs = du.prepare_training_corpus(ngram_file, cmdline_args.corpus, ngram=cmdline_args.ngram) 
    print(f"\r{CLEAR}\r[+] Training corpus prepared")

def main():
    args = define_args().parse_args()
    ngram_probs = logprobs(args)
    # we will assume each line of the ciphertext file is its own message
    # unless it is a newline character

    # next step is to prepare the testing corpus  
    # this is done the same way as the training corpus: 
    #   - remove all punctuation and spacing
    #   - concatenate together the message
    with open(args.encrypted, "rt") as enc:
        # this implementation assumes the encrypted text file is fairly small
        # and can be loaded totally into memory; 
        lines = list(filter(lambda L: L != "\n", enc.readlines()))
        # obtain the test corpus by removing punctuation all non alphabetical chars
        test_corpus = re.sub("[^a-zA-Z]","","".join(lines)).lower()

if __name__ == "__main__":
    main()
