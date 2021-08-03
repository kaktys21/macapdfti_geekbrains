from pymongo import MongoClient

class JobSearcherPipeline:
    
    def __init__(self):
        
        client = MongoClient('localhost', 27017)
        self.mongpbase = client.vacansy
        
    def process_item(self, item, spider):
        collection = self.mongpbase[spider.name]
        collection.insert_one(item)
        print(item['salary'])
        return item
