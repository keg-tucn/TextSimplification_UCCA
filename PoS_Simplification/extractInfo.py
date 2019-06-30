import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize


class ExtractInfo:

    @staticmethod
    def extract_part_of_speech(file):
        stop_words = set(stopwords.words('english'))
        text = ""
        with open(file, encoding="utf8") as f:
            raw = f.read()
            text = text + " " + raw

        tokenized = sent_tokenize(text)
        tagged_sentences = []
        for i in tokenized:
            # Word tokenizers is used to find the words
            # and punctuation in a string
            wordsList = nltk.word_tokenize(i)

            #  Using a Tagger. Which is part-of-speech
            # tagger or POS-tagger.
            tagged = nltk.pos_tag(wordsList)
            tagged_sentences.append(tagged)
        return tagged_sentences

