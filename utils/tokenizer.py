from utils.stop_words import StopWords
import re


def is_a_sinhala_letter(s):
    if len(s) != 1:
        return True
    sinhala_lower_bound = 3456
    sinhala_upper_bound = 3583
    cp = ord(s[0])
    if sinhala_lower_bound <= cp <= sinhala_upper_bound:
        return True
    return False


def contains_sinhala(s):
    for c in s:
        if is_a_sinhala_letter(c):
            return True
    return False


class Tokenizer:
    punctuation_marks = ['.', ',', '\n', '‚', '"', '/', '-', '|', '\\', '—', '¦',
                         '”', '‘', '\'', '“', '’', '´', '´', '!', '@', '#', '$', '%',
                         '^', '&', '*', '+', '-', '?', '˜',
                         '(', ')', '[', ']', '{', '}', ':', ';'
                         ]

    @staticmethod
    def tokenize(sentence):
        phrase_find_regex = re.compile('(\\\"([^\\\"]*)\\\"|\\\'([^\\\']+)\\\')')
        found_phrases = phrase_find_regex.findall(sentence)

        Phrases = []
        for phrase in found_phrases:
            phrase = phrase[0][1:-1]
            sentence = sentence.replace(phrase, '')
            Phrases.append(phrase)

        for punctuation in Tokenizer.punctuation_marks:
            if punctuation in sentence:
                sentence = sentence.replace(punctuation, '')

        tokens = sentence.split()
        Keywords = []
        for token in tokens:
            if contains_sinhala(token):
                if token not in StopWords.sinhala.value:
                    Keywords.append(token)
            else:
                token = token.lower()
                if token not in StopWords.english.value:
                    Keywords.append(token)

        return Keywords, Phrases


if __name__ == "__main__":

    test_sentences = [
        "A prolific, \"elegant and utterly classy\" batsman 'with a huge appetite' for $runs",
        "With over 10,000 runs in $% both Tests and ODIs - and a \' captaincy stint that included ",
        "ලකුණු සඳහා \"විශාල ආශාවක් ඇති දක්ෂ\", අලංකාර සහ 'සම්පූර්ණයෙන්ම උසස් පිතිකරුවෙකු' සහ සන්සුන්",
        "නමුත් අධිකාරී නායකයෙකු - මහේල ජයවර්ධන වඩාත් @#හොඳින් විස්තර කරන ගුණාංග ඒවා වේ. "
    ]

    for test_sentence in test_sentences:
        keywords, phrases = Tokenizer.tokenize(test_sentence)
        print(f'Test Sentence : {test_sentence}')
        print(f'Keywords : {keywords}')
        print(f'Pharases : {phrases}\n')
