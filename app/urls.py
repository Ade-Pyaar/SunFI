from django.urls import path

from .views import home, signup, login, character_fav, character_quotes_fav, characters, characters_quotes, favourites



urlpatterns = [
    path('', home, name='home'),

    path('signup', signup, name='signup'),

    path('login', login, name='login'),

    path("characters", characters),

    path("characters/<slug:xter_id>/quotes", characters_quotes),

    path("characters/<slug:xter_id>/favorites", character_fav),

    path("characters/<slug:xter_id>/quotes/<slug:quote_id>/favorites", character_quotes_fav),

    path("favorites", favourites),

]