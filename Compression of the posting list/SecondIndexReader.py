from FirstIndexReader import *


class SecondIndexReader:
    def __init__(self, dir):
        """Creates a FirstIndexReader object which will
        read from the given directory
        dir is the path of the directory that contains
        the index files"""
        self.reader = FirstIndexReader(dir)

    def getTokenFrequency(self, token):
        """Return the number of reviews containing a
        given token (i.e., word)
        Returns 0 if there are no reviews containing
        this token"""
        return self.reader.getTokenFrequency(token)

    def getTokenCollectionFrequency(self, token):
        """Return the number of times that a given
        token (i.e., word) appears in all the reviews
        indexed (with repetitions)
        Returns 0 if there are no reviews containing
        this token"""
        posting_list = self.getReviewsWithToken(token)
        if not posting_list:
            return 0
        counter = 0
        for i in range(1, len(posting_list), 2):
            counter += posting_list[i]
        return counter

    def getReviewsWithToken(self, token):
        """Returns a series of integers of the form id-1, freq-1, id-2, freq-2, ... such
        that id-n is the n-th review containing the
        given token and freq-n is the
        number of times that the token appears in
        review id-n
        Note that the integers should be sorted by id
        Returns an empty Tuple if there are no reviews
        containing this token"""
        obj = self.reader.getToken(token)
        if obj == 0:
            return ()
        next_token = self.reader.getNextToken(token)
        if next_token == -1 or next_token == 0:
            return ()
        pl_index = obj['ptr_pl']
        if next_token == -2 or not ('length' in next_token) or next_token['length'] == 0:
            with open(os.path.join(self.reader.dir, 'text.pl'), "rb") as file:
                file.read(pl_index)
                posting_list = file.read()
                return self.analyzePostingList(posting_list)
        else:
            next_pl_index = next_token['ptr_pl']
        with open(os.path.join(self.reader.dir, 'text.pl'), "rb") as file:
            file.read(pl_index)
            posting_list = file.read(next_pl_index - pl_index)
            return self.analyzePostingList(posting_list)

    def getNumberOfReviews(self):
        """Return the number of product reviews
        available in the system"""
        return self.reader.getNumberOfReviews()

    def getTokenSizeOfReviews(self):
        """Return the number of tokens in the system
        (Tokens should be counted as many times as they
        appear)"""
        return self.reader.getTokenSizeOfReviews()

    # Helper Functions:

    def analyzePostingList(self, pl):
        bytes_list = []
        for i in pl:
            bits = ""
            if not len(bin(i)[2:]) == 8:
                bits = '0' * (8 - len(bin(i)[2:]))
            bits += bin(i)[2:]
            bytes_list.append(bits)
        numbers = []
        number = ""
        for i in bytes_list:
            number += i[1:]
            if i[0] == '1':
                numbers.append(int(number, 2))
                number = ""
        sum_no_gaps = 0
        for i in range(0, len(numbers), 2):
            sum_no_gaps += numbers[i]
            numbers[i] = sum_no_gaps
        return tuple(numbers)
