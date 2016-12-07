import sys
import re
import ast
from operator import itemgetter

from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer


def filter_words(summary, words_file):
    ignoredWordsFile = open(words_file, 'r')
    ignored = []
    lemmatizer = WordNetLemmatizer()
    tokenizer = RegexpTokenizer(r'\w+')

    summary = summary.lower()

    # read all ignored words into list
    word = ignoredWordsFile.readline()
    while word != "":
        word = word.strip()
        ignored.append(word)
        word = ignoredWordsFile.readline()
    ignoredWordsFile.close()

    summary_tokens = tokenizer.tokenize(summary)
    for i, token in enumerate(summary_tokens):
        try:
            summary_tokens[i] = lemmatizer.lemmatize(
                token.decode('utf-8')).encode('ascii', 'ignore')
        except UnicodeDecodeError:
            summary_tokens.remove(token)
    for item in ignored:
        summary_tokens = filter(lambda a: a != item, summary_tokens)
    return ' '.join(summary_tokens)


def parse(file_name, dest_file, words_file):
    inFile = open(file_name, 'r')
    outFile = open(dest_file, 'w')

    line = inFile.readline()
    genreDict = {}
    while line != "":
        line = re.split(r'\t+', line)
        if len(line) > 5:
            title = line[2]
            if line[3].startswith('{'):
                genres = ast.literal_eval(line[3]).values()
                summary = line[4]
            elif line[4].startswith('{'):
                genres = ast.literal_eval(line[4]).values()
                summary = line[5]
            elif line[5].startswith('{'):
                genres = ast.literal_eval(line[5]).values()
                summary = line[6]
            outFile.write(title + '|')
            curString = ""
            for g in genres:
                if '\\' not in g:
                    if g in genreDict:
                        genreDict[g] += 1
                    else:
                        genreDict[g] = 1
                    curString += g + ','
            outFile.write(curString[:-1])

            # filter words from summary
            summary = filter_words(summary, words_file)
            outFile.write('|' + summary + '\n')
        line = inFile.readline()
    inFile.close()
    outFile.close()
    return genreDict


def main():
    args = sys.argv
    if len(args) != 5:
        print("Error: wrong number of arguments")
        return 1
    input_file = args[1]
    output_file = args[2]
    words_file = args[3]
    genre_file = args[4]
    genreSet = parse(input_file, output_file, words_file)
    with open(genre_file,"w") as writer:
        for key, value in sorted(genreSet.iteritems(), key=lambda (k, v): (v, k), reverse=True):
            writer.write(str(key)+":"+str(value)+"\n")
    writer.close()
if __name__ == "__main__":
    main()
