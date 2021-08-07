from django.urls import path
from workflow.views import WorkflowJsonView

urlpatterns = [
    path(
        'upload-json/',
        WorkflowJsonView.as_view(),
        name="upload-json"
    )
]
