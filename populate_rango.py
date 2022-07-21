import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tango_with_django_project.settings")

import django

django.setup()

from rango.models import Category, Page


def populate():

    # First, we will create lists of dictionaries containing the pages
    # we want to add into each category.
    # Then we will create a dictionary of dictionaries for our categories.
    # This might seem a little bit confusing, but it allows us to iterate
    # through each data structure, and add the data to our models.

    python_pages = [
        {
            "title": "Official Python Tutorial",
            "url": "http://docs.python.org/2/tutorial/",
        },
        {
            "title": "How to Think like a Computer Scientist",
            "url": "http://www.greenteapress.com/thinkpython/",
        },
        {
            "title": "Learn Python in 10 Minutes",
            "url": "http://www.korokithakis.net/tutorials/python/",
        },
    ]

    django_pages = [
        {
            "title": "Official Django Tutorial",
            "url": "https://docs.djangoproject.com/en/1.9/intro/tutorial01/",
        },
        {"title": "Django Rocks", "url": "http://www.djangorocks.com/"},
        {"title": "How to Tango with Django", "url": "http://www.tangowithdjango.com/"},
    ]

    other_pages = [
        {"title": "Bottle", "url": "http://bottlepy.org/docs/dev/"},
        {"title": "Flask", "url": "http://flask.pocoo.org"},
    ]

    cats = [
        {
            "likes": "128",
            "views": "64",
            "name": "Python",
            "pages": python_pages,
        },
        {
            "likes": "64",
            "views": "32",
            "name": "Django",
            "pages": django_pages,
        },
        {
            "likes": "32",
            "views": "16",
            "name": "Other Frameworks",
            "pages": other_pages,
        },
    ]

    for item in cats:
        cat = add_cat(item["name"], item["views"], item["likes"])
        for p in item["pages"]:
            add_page(cat, p["title"], p["url"])

    # Print out the categories we have added.
    # for c in Category.objects.all():
    #     for p in Page.objects.filter(category=c):
    #         print("- {0} - {1}".format(str(c), str(p)))
    #


def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title, url=url, views=views)[0]
    p.save()
    return p


def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name, views=views, likes=likes)[0]
    c.save()
    return c


# Start execution here!
if __name__ == "__main__":
    print("Starting Rango population script...")
    populate()
