from datasets import load_dataset
import re

class DatasetLoader:
    def __init__(self,load_gallery):
        self.load = load_gallery

    def get_name(filename):
        return re.sub(r'_\d+\.jpg$', '', filename)


    def run(self):
        if(self.load):
            dataset = load_dataset("bitmind/lfw")
            data = dataset["train"]




