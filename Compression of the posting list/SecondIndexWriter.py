import math
from FirstIndexWriter import *
import os
import shutil


class SecondIndexWriter:
    def __init__(self, inputFile, dir):
        """Given product review data, creates an on
        disk index
        inputFile is the path to the file containing
        the review data
        dir is the path of the directory in which all
        index files will be created
        if the directory does not exist, it should be
        created"""
        self.writer = FirstIndexWriter(inputFile, dir)
        self.reviews = self.writer.reviews

        self.index_dict = {}
        for review_i in range(len(self.reviews)):
            for word in self.reviews[review_i]:
                if word not in self.index_dict:
                    self.index_dict[word] = [review_i + 1]
                else:
                    self.index_dict[word].append(review_i + 1)
        self.index_dict = sorted(self.index_dict.items())
        # convert into dict:
        temp_dic = {}
        for word, docs_arr in self.index_dict:
            temp_dic[word] = docs_arr
        self.index_dict = temp_dic

        for word in self.index_dict:
            len_docs = len(self.index_dict[word])
            temp_index = []
            doc_i = 0
            while doc_i < len_docs:
                doc = self.index_dict[word][doc_i]
                docs_counter = 1
                doc_i += 1
                while doc_i < len_docs:
                    if not doc == self.index_dict[word][doc_i]:
                        break
                    docs_counter += 1
                    doc_i += 1
                temp_index.append(doc)
                temp_index.append(docs_counter)
            self.index_dict[word] = temp_index

        for word in self.index_dict:
            current_id = self.index_dict[word][0]       # First doc_id of the word
            for doc_id in range(2, len(self.index_dict[word]), 2):
                temp = self.index_dict[word][doc_id]
                self.index_dict[word][doc_id] = temp - current_id
                current_id = temp

        self.pointers_text_dic = {}
        counter = 0
        for word in self.index_dict:
            self.pointers_text_dic[word] = counter
            for i in range(len(self.index_dict[word])):
                counter += math.ceil(len((bin(self.index_dict[word][i]))[2:]) / 7)

        self.writeToFile(dir)

        pl_list = []
        for word in self.index_dict:
            for i in range(len(self.index_dict[word])):
                pl_list.append(self.index_dict[word][i])

        for i in range(len(pl_list)):
            pl_list[i] = bin(pl_list[i])[2:]
            if len(pl_list[i]) % 7 != 0:
                pl_list[i] = ('0' * (7 - (len(pl_list[i]) % 7))) + pl_list[i]

        bytes_array = []
        for i in range(len(pl_list)):
            binary = pl_list[i]
            j = 0
            while j < len(binary):
                if (j + 7) == len(binary):
                    bytes_array.append('1' + binary[j:j+7])
                else:
                    bytes_array.append('0' + binary[j:j+7])
                j += 7

        with open(os.path.join(dir, "text.pl"), "w+b") as file:
            for i in range(len(bytes_array)):
                file.write(pack('B', int(bytes_array[i], 2)))  # Write the one byte from posting list

        if not os.path.exists(dir):
            os.makedirs(dir)    # If the directory is not exist, create it

    def writeToFile(self, dir):
        os.remove(os.path.join(dir, "text.dic"))
        with open(os.path.join(dir, "text.dic"), "w+b") as file:
            file.write(pack('l', len(self.writer.dictionary_str)))
            file.write(self.writer.dictionary_str.encode('ascii'))
            index = 0
            for word in self.writer.dictionary:
                if index % 10 == 0:
                    file.write(pack('l', self.writer.pointers_blocks[word]))    # Write the block's pointer
                    file.write(pack('l', self.writer.dictionary[word]))         # Write the frequency of the word
                    file.write(pack('l', self.pointers_text_dic[word]))         # Write the posting list
                    file.write(pack('B', len(word)))                            # Write the length of the word
                else:
                    file.write(pack('l', self.writer.dictionary[word]))         # Write the frequency of the word
                    file.write(pack('l', self.pointers_text_dic[word]))         # Write the posting list
                    if index % 10 != 9:
                        file.write(pack('B', len(word)))                            # Write the length of the word
                    file.write(pack('B', self.writer.prefixes_dictionary[word]))    # Write the prefix of the word
                index += 1
            # To pad the last block with zeros
            if len(self.writer.dictionary) % 10 > 0:
                for i in range(10 - (len(self.writer.dictionary) % 10) - 1):
                    # Any other word in the last block: 4+1+1 bytes
                    file.write(pack('l', 0))  # Write the frequency of the word
                    file.write(pack('l', 0))  # Write the posting list
                    file.write(pack('B', 0))  # Write the length of the word
                    file.write(pack('B', 0))  # Write the prefix of the word
                # The last word in block: 4+1 bytes
                file.write(pack('l', 0))  # Write the frequency of the word
                file.write(pack('l', 0))  # Write the posting list
                file.write(pack('B', 0))  # Write the prefix of the word

    def removeIndex(self, dir):
        """Delete all index files by removing the given
        directory
        dir is the path of the directory to be
        deleted"""
        if os.path.exists(dir):
            shutil.rmtree(dir)
