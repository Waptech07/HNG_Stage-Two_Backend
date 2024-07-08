from django.urls import path
from .views import UserDetailView, OrganisationDetailView, OrganisationListCreateView, AddUserToOrganisationView

urlpatterns = [
    path('users/<int:id>', UserDetailView.as_view(), name='user-detail'),
    path('organisations', OrganisationListCreateView.as_view(), name='organisation-list-create'),
    path('organisations/<str:orgId>', OrganisationDetailView.as_view(), name='organisation-detail'),
    path('organisations/<str:orgId>/users', AddUserToOrganisationView.as_view(), name='add-user-to-organisation'),
]
