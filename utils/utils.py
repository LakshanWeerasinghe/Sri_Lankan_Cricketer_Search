from math import sqrt
from collections import Counter


def get_cosine_sim(word1, word2):
    vec1 = word2vec(word1)
    vec2 = word2vec(word2)
    return cos_dis(vec1, vec2)


def word2vec(word):

    # count the characters in word
    cw = Counter(word)
    # precomputes a set of the different characters
    sw = set(cw)
    # precomputes the "length" of the word vector
    lw = sqrt(sum(c*c for c in cw.values()))

    # return a tuple
    return cw, sw, lw


def cos_dis(v1, v2):
    # which characters are common to the two words?
    common = v1[1].intersection(v2[1])
    # by definition of cosine distance we have
    return sum(v1[0][ch]*v2[0][ch] for ch in common)/v1[2]/v2[2]


if __name__ == '__main__':
    word1 = "worst"
    word2 = "worest"

    word3 = "පට්ට"
    word4 = "පට්ටම"

    print(cos_dis(word2vec(word1), word2vec(word2)))
    print(cos_dis(word2vec(word3), word2vec(word4)))