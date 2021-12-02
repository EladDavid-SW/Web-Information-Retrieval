from SecondIndexReader import *
from SecondIndexWriter import *


class Main:
    files_path = r'./100.txt'
    dir_path = r'./dir'
    word = 'zucchini'

    writer = SecondIndexWriter(files_path, dir_path)
    # # writer.removeIndex(dir_path)
    reader = SecondIndexReader(dir_path)
    print(reader.getReviewsWithToken('that'))
    print(reader.getReviewsWithToken('several'))
    print(reader.getReviewsWithToken('a'))
    print(reader.getReviewsWithToken('centuries'))
    print(reader.getReviewsWithToken('was'))
    print(reader.getReviewsWithToken('mostly'))
    print(reader.getReviewsWithToken('happily'))

    print(reader.getTokenCollectionFrequency('that'))
    print(reader.getTokenCollectionFrequency('several'))
    print(reader.getTokenCollectionFrequency('a'))
    print(reader.getTokenCollectionFrequency('centuries'))
    print(reader.getTokenCollectionFrequency('was'))
    print(reader.getTokenCollectionFrequency('mostly'))
    print(reader.getTokenCollectionFrequency('happily'))
