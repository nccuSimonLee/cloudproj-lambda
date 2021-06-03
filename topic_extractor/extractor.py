from opencc import OpenCC
cc = OpenCC('s2t')



class Extractor:
    def __init__(self):
        pass
    
    def extract_topic(self, texts):
        texts = cc.convert(texts)
        return texts
