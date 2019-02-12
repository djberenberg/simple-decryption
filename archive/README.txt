Decipher
========

Goal
----

The goal of this task is to assess a candidate's craftsmanship skills
as a software engineering.

The goal of this problem is to write a program that decrypts a set of
short quotations from an English quote book.  They are roughly the
length of Tweets but not in tweet-speak.  They are proper English
prose.  

The text file has been encrypted with a simple substitution cipher.
The cipher is so simple that you can reverse it by hand.  It only
substitutes letters, so the white space and capitalization remain
unchanged.  You can find "H" and guess it is the word "I" and find "c"
and guess it is the word "a", and keep going by hand.

The task is to write a program that automatically derives the cipher
and recovers the original text.  It must get the complete cipher and
do so automatically.

But, here's the thing: this task is just hard enough that whatever
approach you try first, it probably won't get all the letters.  The
text is small enough that simple things like frequency counts are
inadequate, so you will have to enhance your algorithm.  In the
process of improving your algorithm, you will necessarily iterate on
your code, and that process of working the .py file(s) that you create
will stress your engineering craftsmanship.  That's the test.  That's
what we are looking for.

While we do care about algorithmic sophistication and math and speed
and cleverness, we care much more about *maintainability*, ease of
reading, ease of understanding someone else's code, and *joy of use*.

The problem forces you to evolve your thinking, and thus your code
must also evolve.  One measure of engineering craftsmanship is how
quickly a person can evolve their thinking while still maintaining
high-quality, readable, *maintainable* code.


How long will this take?
------------------------

Typically, this takes people between three and eight hours to
complete.  Some people get really into it and spend many days
exploring the problem space.  

Interestingly, we have detected no correlation between how long
someone says the spent on it, and the quality of the solution.  By
"quality", we mean *maintainability*.

We ask ourselves: can I understand the code on first skimming it, and
do I want to maintain it?  We also ask several detailed questions
about that code that require full reading, however those are
secondary.

So, in addition to solving the algorithm, please write your own
README.txt to replace this one, and do whatever else you would do for
a maintainable piece of software.


Input Data
----------
Along with this documentation file, you have been given two data files. 

"encoded-en.txt" is a set of short messages in English, where each has
been encrypted using a simple substitution cipher. Such a cipher works
by replacing all occurrences of a character with a different (randomly
selected, but consistent) character. The substitution is not case
sensitive.

For example:

Original message: "Hello world."
Encrypted message: "Lkccz mzfca."

Cipher:
d -> a
e -> k
h -> l
l -> c
o -> z
r -> f
w -> m

For this problem white space and punctuation are not substituted.

"corpus-en.txt" is a corpus of English texts from gutenberg.org
consisting of the contents of a number of books.  Please do not use
external data sources.  If you want character frequencies etc, then
please use corpus-en.txt.


Your Program
------------
We prefer that you code this in python.  If you would like to submit
solutions in other programming languages, we will certainly read them.
Language nimbleness is an important skill.  If non-standard libraries
are required to run the solution you need to provide them (ideally
none).

Your program should be runnable from the command line and output at
least two other separate files:

(1) The decryption cipher (i.e. the inverse mapping of encoded
character back to original), in a single text file with the format:

<encrypted> -> <decrypted>
...

for each character. No header row, thus there should be 26 rows (one
for each English letter).

e.g.
a -> z
b -> y
c -> x
...
z -> a

(2) The original texts decrypted based on this decryption cipher.
This should be in a single text file, following the same formatting as
the encrypted messages provided.


You should submit at the conclusion of the exercise:

- All code written

- Example output files as specified above

- Any supplementary files (e.g. tests, data)

- A brief write-up explaining your approach, how well it worked, what
  further avenues you might explore given time, along with any
  necessary instructions on how to run the code. Specify the language
  version if important to running the solution.



Important Notes
---------------

In addition to evaluating the simplicity and cleverness of your
technical approach, we also give marks for ease of use, engineering
hygiene, craftmanship & style.

Correct solutions get the reverse cipher without fail.  That is,
programs should *not* require repeated manual operation to eventually
get a valid reverse cipher.

Your program should be sufficiently generalized that it can be run on
*other* input files, or even incorporated into a larger system.  We
want to see how you organize the interface to your algorithm.

Pythonic style counts.  Use the python standard library and tools.

