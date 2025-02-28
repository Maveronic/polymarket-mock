from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, EventViewSet, OptionViewSet, BetViewSet

# Setting up the router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'events', EventViewSet, basename='event')
router.register(r'options', OptionViewSet, basename='option')
router.register(r'bets', BetViewSet, basename='bet')

# URL Patterns
urlpatterns = [
    path('', include(router.urls)),
]