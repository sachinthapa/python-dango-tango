from django.urls import path

from . import views

app_name = "rango"
urlpatterns = [
    path("", views.index, name="index"),
    path("register_profile/", views.register_profile, name="register_profile"),
    # path("about/", views.about, name="about"),
    path(
        "category/<slug:category_name_slug>", views.show_category, name="show_category"
    ),
    # path("add_category/", views.add_category, name="add_category"),
    path("category/<category_name_slug>/add_page/", views.add_page, name="add_page"),
    path("search/", views.search, name="search"),
    path("goto/", views.goto_url, name="goto"),
    # Class based views ------
    path("about/", views.AboutView.as_view(), name="about"),
    path("profile/<username>/", views.ProfileView.as_view(), name="profile"),
    path("list_profile", views.list_profiles, name="list_profile"),
    path("add_category/", views.AddCategoryView.as_view(), name="add_category"),
    path("like_category/", views.like_category, name="like_category"),
    path("suggest/", views.suggest_category, name="suggest_category"),
]
