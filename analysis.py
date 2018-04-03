# encoding:utf-8
import re
import nltk
import pymorphy2
import csv
import collections
from snowballstemmer import stemmer as Stemmer 

morph = pymorphy2.MorphAnalyzer()

def filter_noise(text):
    text = re.sub('<pre>.*?</pre>',u' ', text, flags=re.DOTALL)
    text = re.sub('<code>.*?</code>',u' ', text, flags=re.DOTALL)
    text = re.sub('<[^<]+?>', u' ', text, flags=re.DOTALL) 
    text = re.sub('(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)', u' ', text, flags=re.DOTALL)             
    text = re.sub('(https|http)?:\/\/.*', u'', text)
    return text

def process_text(text, short_filter=False, word_len_threshold=2):
    global morph

    def process(filter, token, word_len_threshold):
        global morph

        p = morph.parse(token)[0]
        if len(p.normal_form) < word_len_threshold:
            return None
        
        # http://pymorphy2.readthedocs.io/en/latest/user/grammemes.html
        if any(tag in str(p.tag) for tag in ['PNCT', 'NUMB']): # ['LATN', 'PNCT', 'NUMB', 'UNKN']
            return None
        # http://pymorphy2.readthedocs.io/en/latest/user/grammemes.html
        if str(p.tag.POS) not in filter:
            return str(p.normal_form)  

    otput_data = u""
    if short_filter:
        filter = ['PREP']
    else:    
        filter = ['NPRO', 'PREP', 'PRED', 'PRCL'] # 'CONJ' — минус

    text = filter_noise(text)
    text = text.lower()

    sent_text = nltk.sent_tokenize(text)
    stemmer = Stemmer("russian")
    for sentence in sent_text:
        tokenized_text = nltk.word_tokenize(sentence)
        for token in tokenized_text:
            
            token = token.replace('.', u' ')
            token = token.replace('/', u' ')
            token = token.replace('=', u' ')
            token = token.replace('`', u' ')
            token = token.replace('-', u' ')
            token = token.replace('–', u' ')

            for sub_token in token.split():
                processed = process(filter, sub_token, word_len_threshold)
                if processed is not None:
                    stemmed = stemmer.stemWord(processed)
                    otput_data += u" " + stemmed
        
    return otput_data

def parse_file(filename="comments.csv"):
    full_text = ""
    comments = list()
    with open(filename, 'rt', encoding="utf8") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        for row in csv_reader:
            _, body = row
            processed_text = process_text(body)
            if len(processed_text.replace(" ", "")) == 0:
                continue
            full_text += " " + processed_text
            comments.append((body, processed_text))
    return full_text, comments

if __name__ == "__main__":
    n_words = int(input("Please enter number of words: "))
    text, comments = parse_file()
    words_to_check = [word for word in text.split(" ") if len(word.replace(" ", "")) > 0]
    most_common_words = collections.Counter(words_to_check).most_common(n_words)

    common_dict = dict()
    for word, _ in most_common_words:
        common_dict[word] = list()

    for word, _ in most_common_words:
        for body, process_text in comments:
            if word in process_text:
                common_dict[word].append(body)
    while True:
        for word, count in most_common_words:
            print ("%s: %s" % ( str(word), str(count) ))
        print("\r\n\r\n")
        word = str(input("Please enter the word or type quit: "))
        if word == 'quit':
            print("Bye-Bye!")
            break
        if common_dict.get(word, None) is None:
            print("Wrong spelling of the word")
            continue
        print("-----------------------------------------")
        print("\r\n\r\n")
        print("### %s" % (word))
        for comment in common_dict[word]:
            print("      %s" % (comment))
        print("\r\n\r\n")
