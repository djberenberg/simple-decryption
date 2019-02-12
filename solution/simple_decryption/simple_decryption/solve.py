import random
import string
from math import log2
from .utils import chunks
from .core import SubstitutionCipher

"""
solve submodule intended for cipher-specific solution codes
"""
__all__ = ["SubstitutionSolver"]

CLEAR = 80 * " "

class SubstitutionSolver(object):
    """
    Genetic method for solving a substitituion cipher by way of hill climber algorithm

    This algorithm follows one lineage of elite chromosomes, iteratively mutating each
    successive child until its fitness cannot be maximized or the number of generations
    has expired
    """

    def __init__(self, ngram_distribution, total_ngrams, gram_length):
        """ 
        args:
            :ngram_distribution (dict) - mapping from ngrams -> their (log) probabilities
            :total_ngrams (int) - the total number of ngrams found in the corpus text
            :gram_length (int) - the length of the ngrams in `ngram_distribution`
            :vocab (optional) - vocabulary to verify the solution against; casted to set on construction
        """
        self.ngram_dist = ngram_distribution
        self.N = total_ngrams
        self.gram_len = gram_length

    def score(self, string):
        """
        Score a string based on its n-gram language model (log) likelihood
        
        Scoring in this case functions as a loss function for the algorithm

        args:
            :string (str) - string to 'score'
        returns:
            :(float) - the n-gram lang. model (log) likelihood
        raises:
            :TypeError if `string` is not a str
        """
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

    @staticmethod
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
    
    @staticmethod
    def generate_parent():
        """
        helper function to wrap the parent generation routine
        returns:
            :(str) - a parent cipher key
        """
        key = list(string.ascii_lowercase)
        random.shuffle(key)
        return "".join(key)

    def solve(self, ciphertext, n_iters, verbose=False, seed_parent=None):
        """
        perform the hill climber algorithm on cipher text for some number of iterations
        args:
            :ciphertext (str) - the encrypted text
            :n_iters (int) - number of iterations to run
            :verbose (bool) - print verbose outputs
            :seed_parent (str or NoneType) - seed key to use for solution, if None then one will be generated
        returns:
            :(SubstitutionCipher) - Cipher object containing the final decryption cipher found
            :(float) - the final fitness of that key

        raises:
            :AssertionError if `seed` is neither None nor str
        """
        assert isinstance(seed_parent, str) or seed_parent is None, "Bad seed. Expected `str` or `NoneType`"

        if seed_parent is None:
            top_key = SubstitutionSolver.generate_parent() 
        else:
            top_key = seed_parent
        top_fitness = self.score(ciphertext)
        parent = top_key
        
        # hill climbing algorithm
        time_stagnant = i = 0
        while i < n_iters:
            child = SubstitutionSolver.mutate(parent) # randomly modify the parent key
            decrypted =  SubstitutionCipher(child).decrypt(ciphertext) # decrypt wrt this key
            child_fitness = self.score(decrypted) # how fit is the key?
            if child_fitness > top_fitness: # keep top performing keys for future mutation
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
        return SubstitutionCipher(top_key), top_fitness
