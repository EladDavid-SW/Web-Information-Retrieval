from FirstIndexWriter import *
from FirstIndexReader import *


class Main:
    files_path = r''
    dir_path = r''
    word = 'zucchini'
    writer = FirstIndexWriter(files_path, dir_path)
    # writer.removeIndex(dir_path)
    reader = FirstIndexReader(dir_path)
    print(reader.getTokenSizeOfReviews())
    print(reader.getTokenFrequency(word))
    print(reader.getNumberOfReviews())
