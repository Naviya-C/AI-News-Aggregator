from transformers import pipeline

class Classifier():
    def __init__(self, labels:list):
        self.labels = labels
        
    def classify_news(self, text: str):
        """
        In here, this function used to categorize scraped news using 'zero-shot-model' to 7 categories.
            - business, entertainment, general, health, science, sports, technology.
            - Using zero-shot classification named -> 'facebook/bart-large-mnli'
            - Only get first highest 2 labels only by filtering threshold. And store to 'article_categories' table
        """
        
        pipe = pipeline("zero-shot-classification", model = "facebook/bart-large-mnli")
        labels = self.labels
        
        result = pipe(text, labels) # result is a dictionary contains {labels:[], score:[]}
        return result["labels"][0]