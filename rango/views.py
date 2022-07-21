from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from .forms import CategoryForm, PageForm, UserProfileForm
from .models import Category, Page, UserProfile

# Create your views here.


def goto_url(request):
    page_id = None
    url = "/rango/"
    if request.method == "GET":
        if "page_id" in request.GET:
            page_id = request.GET["page_id"]
    try:
        page = Page.objects.get(id=page_id)
        page.views = page.views + 1
        page.save()
        url = page.url
    except Page.DoesNotExist:
        pass
    return redirect(url)


def index(request):
    request.session.set_test_cookie()
    category_list = Category.objects.order_by("-likes")[:5]
    context_dict = {"categories": category_list}

    visitor_cookie_handler(request)
    context_dict["visits"] = request.session["visits"]

    return render(request, "rango/index.html", context=context_dict)


def about(request):
    return render(request, "rango/about.html", {})


@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()
    return render(
        request, "rango/list_profile.html", {"userprofile_list": userprofile_list}
    )


@login_required
def register_profile(request):
    form = UserProfileForm()
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect("rango:index")
    else:
        print(form.errors)
    context_dict = {"form": form}
    return render(request, "rango/profile_registration.html", context_dict)


def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by("-views")
        context_dict["pages"] = pages
        context_dict["category"] = category
    except Category.DoesNotExist:
        context_dict["category"] = None
        context_dict["pages"] = None

    context_dict["query"] = category.name
    result_list = []
    if request.method == "POST":
        query = request.POST["query"].strip()
        if query:
            category = Category.objects.get(name=query)
            context_dict["query"] = query
            context_dict["result_list"] = result_list

    return render(request, "rango/category.html", context_dict)


def add_category(request):
    form = CategoryForm()
    # A HTTP POST?
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect("/rango/")
    else:
        print(form.errors)
    return render(request, "rango/add_category.html", {"form": form})


@login_required
def like_category(request):
    likes = 0
    cat_id = None
    if request.method == "GET":
        cat_id = request.GET["category_id"]
        likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)


def get_category_list(max_results=0, starts_with=""):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    else:
        cat_list = Category.objects.all()
    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    return cat_list


def suggest_category(request):
    cat_list = []
    starts_with = ""
    if request.method == "GET":
        starts_with = request.GET["suggestion"]
    cat_list = get_category_list(8, starts_with)

    if len(cat_list) == 0:
        cat_list = Category.objects.order_by("-likes")
    return HttpResponse(cat_list)


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
        return redirect("/rango/")
    form = PageForm()
    if request.method == "POST":
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(
                    reverse(
                        "rango:show_category",
                        kwargs={"category_name_slug": category_name_slug},
                    )
                )
        else:
            print(form.errors)

    context_dict = {"form": form, "category": category}
    return render(request, "rango/add_page.html", context_dict)


def search(request):
    result_list = []
    if request.method == "POST":
        query = request.POST["query"].strip()
    return render(request, "rango/search.html", {"result_list": result_list})


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


# Updated the function definition
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, "visits", "1"))
    last_visit_cookie = get_server_side_cookie(
        request, "last_visit", str(datetime.now())
    )
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], "%Y-%m-%d %H:%M:%S")
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session["last_visit"] = str(datetime.now())
    else:
        request.session["last_visit"] = last_visit_cookie
    request.session["visits"] = visits


def visitor_cookie_handler_client(request, response):
    visits = int(request.COOKIES.get("visits", "1"))
    last_visit_cookie = request.COOKIES.get("last_visit", str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], "%Y-%m-%d %H:%M:%S")
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        response.set_cookie("last_visit", str(datetime.now()))
    else:
        response.set_cookie("last_visit", last_visit_cookie)
    response.set_cookie("visits", visits)


class AboutView(View):
    def get(self, request):
        # view logic
        visitor_cookie_handler(request)
        return render(
            request, "rango/about.html", context={"visits": request.session["visits"]}
        )


class AddCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, "rango/add_category.html", {"form": form})

    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm()
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
        return render(request, "rango/add_category.html", {"form": form})


class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect("index")
        userprofile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm(
            {"website": userprofile.website, "picture": userprofile.picture}
        )
        return (user, userprofile, form)

    @method_decorator(login_required)
    def get(self, request, username):
        (user, userprofile, form) = self.get_user_details(username)
        return render(
            request,
            "rango/profile.html",
            {"userprofile": userprofile, "selecteduser": user, "form": form},
        )

    @method_decorator(login_required)
    def post(self, request, username):
        (user, userprofile, form) = self.get_user_details(username)
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect("rango:profile", user.username)
        else:
            print(form.errors)
            return render(
                request,
                "rango/profile.html",
                {"userprofile": userprofile, "selecteduser": user, "form": form},
            )
