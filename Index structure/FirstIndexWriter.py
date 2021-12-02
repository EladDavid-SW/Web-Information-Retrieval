import os
from struct import pack
import shutil


class FirstIndexWriter:
    words = []
    reviews = []
    dictionary = {}
    prefixes_dictionary = {}
    pointers_blocks = {}
    dictionary_str = ""
    word_counter = 0

    # Helper functions:
    def removeLabel(self, from1, from2, to1, to2):
        """
        Removing one label or a few from the words list.
        :param from1: first word to look for (first part of the opening label)
        :param from2: validate this word appear after from1
        :param to1: remove till to1 word (first part of the closing label)
        :param to2: validate that the string to2 coming after to1
        :return:
        """
        from1 = from1.lower()
        from2 = from2.lower()
        to1 = to1.lower()
        to2 = to2.lower()
        temp = [self.words[0], self.words[1]]
        i = 2
        while i < len(self.words):
            if self.words[i-2] == from1 and self.words[i-1] == from2:
                del temp[-1]
                del temp[-1]
                while not (self.words[i] == to1 and self.words[i + 1] == to2):
                    i += 1
            temp.append(self.words[i])
            i += 1
        self.words = temp

    def getReviews(self):
        reviews = []
        length = len(self.words)
        i = 2
        while i < length:
            if self.words[i - 2] == 'review' and self.words[i - 1] == 'text':
                cut_from = i
                while not (i == length or self.words[i] == 'review' and self.words[i + 1] == 'text'):
                    i += 1
                reviews.append(self.words[cut_from:i])
            i += 1
        self.reviews = reviews

    def getCountDict(self):
        temp_dict = {}
        for review in self.reviews:  # Array of all the words in one review
            for word in review:
                self.word_counter += 1
        for review in self.reviews:  # Array of all the words in one review
            review = list(dict.fromkeys(review))  # Remove the duplicated words in the review
            for word in review:
                if word not in temp_dict:
                    temp_dict[word] = 1
                else:
                    temp_dict[word] += 1
        temp_dict = sorted(temp_dict.items())
        for a, b in temp_dict:
            self.dictionary.setdefault(a, b)

    def longest_prefix(self, str1, str2):
        """
        :param str1: First string to be compared
        :param str2: Second string to be compared
        :return: Index of the end of their longest mutual prefix
        """
        i = 0
        while i < len(str1) and i < len(str2):
            if str1[i] != str2[i]:
                break
            i += 1
        return i

    def create_blocks(self):
        block_counter = 0
        blocks_dict = []   # From list to str
        comparing_dict = []
        for word in self.dictionary:
            if block_counter == 0:  # Beginning of block
                blocks_dict.append(word)
                comparing_dict.append(word)
                self.prefixes_dictionary[word] = 0
                self.pointers_blocks[word] = len(''.join(blocks_dict)) - len(word)
                block_counter += 1
            elif block_counter < 10:
                prefix = self.longest_prefix(comparing_dict[-1], word)  # Compare the last word and the current word
                blocks_dict.append(word[prefix:])
                comparing_dict.append(word)
                self.prefixes_dictionary[word] = prefix
                if block_counter == 9:  # The last word in the block
                    block_counter = 0
                else:
                    block_counter += 1
        self.dictionary_str = ''.join(blocks_dict)

    def writeToFile(self, dir):
        with open(os.path.join(dir, "text.dic"), "w+b") as file:
            file.write(pack('l', len(self.dictionary_str)))
            file.write(self.dictionary_str.encode('ascii'))
            index = 0
            for word in self.dictionary:
                if index % 10 == 0:
                    file.write(pack('l', self.pointers_blocks[word]))    # Write the block's pointer
                    file.write(pack('l', self.dictionary[word]))         # Write the frequency of the word
                    file.write(pack('B', len(word)))                     # Write the length of the word
                else:
                    file.write(pack('l', self.dictionary[word]))         # Write the frequency of the word
                    if index % 10 != 9:
                        file.write(pack('B', len(word)))                     # Write the length of the word
                    file.write(pack('B', self.prefixes_dictionary[word]))    # Write the prefix of the word
                index += 1
            # To pad the last block with zeros
            if len(self.dictionary) % 10 > 0:
                for i in range(10 - (len(self.dictionary) % 10) - 1):
                    # Any other word in the last block: 4+1+1 bytes
                    file.write(pack('l', 0))  # Write the frequency of the word
                    file.write(pack('B', 0))  # Write the length of the word
                    file.write(pack('B', 0))  # Write the prefix of the word
                # The last word in block: 4+1 bytes
                file.write(pack('l', 0))  # Write the frequency of the word
                file.write(pack('B', 0))  # Write the prefix of the word

    def __init__(self, inputFile, dir):
        """Given product review data, creates an on
        disk index
        inputFile is the path to the file containing
        the review data
        dir is the path of the directory in which all
        index files will be created
        if the directory does not exist, it should be
        created"""
        if not os.path.exists(dir):
            os.makedirs(dir)    # If the directory is not exist, create it
        assert os.path.exists(inputFile), "Error (FirstIndexWriter:__init__): Input File path is not exist."
        with open(inputFile, "r") as f:
            file = f.read()
            file = file.lower()  # Normalize the data
            word = ""
            for ch in file:     # Append all alpha-numeric words to words list
                if ch.isalnum():    # Check if alpha-numeric
                    word += ch
                else:
                    if word != "":
                        self.words.append(word)
                        word = ""

            self.removeLabel("product", "productId", "review", "text")
            self.getReviews()
            self.getCountDict()
            self.create_blocks()
            self.writeToFile(dir)
        with open(os.path.join(dir, 'helper.txt'), "w+b") as f:
            f.write(pack('l', len(self.reviews)))
            f.write(pack('l', self.word_counter))

    def removeIndex(self, dir):
        """Delete all index files by removing the given
        directory
        dir is the path of the directory to be
        deleted"""
        if os.path.exists(dir):
            shutil.rmtree(dir)
