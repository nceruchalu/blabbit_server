from django.contrib import admin
from blabbit.apps.feedback.models import Feedback
from blabbit.apps.feedback.forms import FeedbackForm

class FeedbackAdmin(admin.ModelAdmin):
    """
    Representation of Feedback model in admin interface with a custom form
    """
    form = FeedbackForm

admin.site.register(Feedback, FeedbackAdmin)
