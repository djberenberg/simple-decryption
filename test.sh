#!/bin/sh
for i in `seq 0 100`; do
    python decipher.py encoded-en.txt
    result=$(cmp decrypted.txt correct.txt || echo "$i: different")
    echo $result >> results.txt
done

