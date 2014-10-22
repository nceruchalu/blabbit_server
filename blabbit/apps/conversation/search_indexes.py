from haystack import indexes
from blabbit.apps.conversation.models import Room

class RoomIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Haystack search index for Room model.
    
    This includes the created_at field for use in filtering out expired Rooms.
    """
    
    text = indexes.EdgeNgramField(document=True, use_template=True)
    created_at = indexes.DateTimeField(model_attr='created_at')
    
    def get_model(self):
        return Room
