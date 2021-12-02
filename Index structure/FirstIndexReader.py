import os
from struct import unpack


class FirstIndexReader:

    dictionary_str = ""
    blocks = []
    dir = ""

    def __init__(self, dir):
        """Creates a FirstIndexReader object which will
        read from the given directory
        dir is the path of the directory that contains
        the index files"""
        self.dir = dir
        full_path = os.path.join(dir, "text.dic")
        assert os.path.exists(full_path), "Error (FirstIndexReader:__init__): Dictionary File path is not exist."
        with open(full_path, "rb") as file:
            self.file_len = len(file.read())

        with open(full_path, "rb") as file:
            dic_len = file.read(4)
            self.dic_len = unpack('l', dic_len)[0]
            self.dictionary_str = file.read(self.dic_len)

            self.num_of_blocks = (self.file_len - self.dic_len - 4) // 62
            self.setDataStructure()

            for block in range(self.num_of_blocks):
                # self.blocks[block][0] = {}
                self.blocks[block][0]["str_ptr"] = unpack('l', file.read(4))[0]
                self.blocks[block][0]["freq"] = unpack('l', file.read(4))[0]
                self.blocks[block][0]["length"] = unpack('B', file.read(1))[0]
                for inner_block in range(1, 9):
                    self.blocks[block][inner_block]["freq"] = unpack('l', file.read(4))[0]
                    self.blocks[block][inner_block]["length"] = unpack('B', file.read(1))[0]
                    self.blocks[block][inner_block]["prefix"] = unpack('B', file.read(1))[0]
                self.blocks[block][9]["freq"] = unpack('l', file.read(4))[0]
                self.blocks[block][9]["prefix"] = unpack('B', file.read(1))[0]

    # Helper functions:
    def setDataStructure(self):
        self.blocks = []
        for block in range(self.num_of_blocks):
            self.blocks.append([])
            for i in range(10):
                self.blocks[block].append({})

    def getTokenBlock(self, token):
        start = 0
        END = self.num_of_blocks - 1
        end = END
        if token < self.dictionary_str[:self.blocks[0][0]["length"]].decode('ascii'):
            return -1
        while start <= end:
            mid = (start + end) // 2
            if start == end:
                return start
            current_word_dic = self.blocks[mid][0]
            word_ptr = current_word_dic["str_ptr"]
            word_len = current_word_dic["length"]
            current_word = self.dictionary_str[word_ptr:(word_ptr + word_len)].decode('ascii')
            if mid != END:
                next_block = self.blocks[mid + 1][0]
                next_ptr = next_block["str_ptr"]
                next_len = next_block["length"]
                next_word = self.dictionary_str[next_ptr:(next_ptr + next_len)].decode('ascii')
            if current_word < token:
                if mid != END and next_word > token:
                    return mid
                else:
                    start = mid + 1
            elif current_word > token:
                end = mid
            else:   # The word is the mid (index) block, first position
                return mid

    def getToken(self, token):
        """
        Binary-Search for the token.
        :param token: The word we want to get info about.
        :return: The dictionary of the token (param) in the blocks (2-D list).
        Return 0 if not found.
        """
        index_block = self.getTokenBlock(token)
        if index_block == -1:   # The wanted token comes before the first word in the dictionary
            return 0
        block = self.blocks[index_block]
        # Run on all words in the block and locking for the token
        word_dic = block[0]
        word_ptr = word_dic["str_ptr"]
        word_len = word_dic["length"]
        word = self.dictionary_str[word_ptr:(word_ptr + word_len)].decode('ascii')
        if word == token:
            return word_dic
        index = word_ptr + word_len
        for i in range(1, 9):
            word_dic = block[i]
            word_len = word_dic["length"]
            word_prefix_len = word_dic["prefix"]
            word = word[:word_prefix_len]
            word += self.dictionary_str[index:(index + word_len - word_prefix_len)].decode('ascii')
            index += word_len - word_prefix_len
            if word == token:
                return word_dic
        # Check the last word
        if index_block == self.num_of_blocks - 1:
            next_block_ptr = self.dic_len
        else:
            next_block_ptr = self.blocks[index_block + 1][0]["str_ptr"]

        word_dic = block[9]
        word_prefix_len = word_dic["prefix"]
        word = word[:word_prefix_len]
        word += self.dictionary_str[index:next_block_ptr].decode('ascii')

        if word == token:
            return word_dic

        return 0

    def getTokenFrequency(self, token):
        """Return the number of reviews containing a
        given token (i.e., word)
        Returns 0 if there are no reviews containing
        this token"""
        search_result = self.getToken(token)
        if search_result == 0:
            return 0
        return int(search_result["freq"])  # Originally print it into a special file

    def getNumberOfReviews(self):
        """Return the number of product reviews
        available in the system"""
        with open(os.path.join(self.dir, 'helper.txt'), "rb") as f:
            return int(unpack('l', f.read(4))[0])

    def getTokenSizeOfReviews(self):
        """Return the number of tokens in the system
        (Tokens should be counted as many times as they
        appear)"""
        with open(os.path.join(self.dir, 'helper.txt'), "rb") as f:
            f.read(4)
            return int(unpack('l', f.read(4))[0])
