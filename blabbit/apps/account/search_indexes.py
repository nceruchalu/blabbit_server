from haystack import indexes
from blabbit.apps.account.models import User

class UserIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Haystack search index for User model
    """
    
    text = indexes.EdgeNgramField(document=True, use_template=True)
    
    def get_model(self):
        return User
