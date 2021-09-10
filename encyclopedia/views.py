import random

from django import forms
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from markdown2 import Markdown

from . import util


class CreateForm(forms.Form):
    title = forms.CharField(label="New Title")
    content = forms.CharField(label="New Content")


class EditForm(forms.Form):
    content = forms.CharField(label="New Content")


def index(request):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


def entry(request, title):
    entry_md = util.get_entry(title)
    if entry_md != None:
        return render(
            request,
            "encyclopedia/entry.html",
            {
                "title": title,
                "entry": entry_md,
            },
        )
    else:
        return render(
            request,
            "encyclopedia/error.html",
            {"title": title},
        )


def create(request):
    if request.method == "GET":
        return render(request, "encyclopedia/create.html", {"form": CreateForm()})

    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if util.get_entry(title):
                messages.error(
                    request,
                    "This page title already exists!",
                )
                return render(request, "encyclopedia/create.html", {"form": form})
            else:
                util.save_entry(title, content)
                messages.success(request, f'New page "{title}" created successfully!')
                return redirect(reverse("entry", args=[title]))
        else:
            messages.error(request, "Entry form not valid, please try again!")
            return render(request, "encyclopedia/create.html", {"form": form})


def edit(request, title):
    if request.method == "GET":
        content = util.get_entry(title)
        if content == None:
            messages.error(request, f"{title} page does not exist!")
        else:
            return render(
                request,
                "encyclopedia/edit.html",
                {
                    "title": title,
                    "edit_form": EditForm(initial={"content": content}),
                },
            )

    elif request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            messages.success(request, f'Entry "{title}" updated successfully!')
            return redirect(reverse("entry", args=[title]))
        else:
            messages.error(request, f"Editing form not valid, please try again!")
            return render(
                request,
                "encyclopedia/edit.html",
                {"title": title, "edit_form": form},
            )


def search(request):
    title = request.GET["q"]
    if title in util.list_entries():
        return redirect(reverse("entry", args=[title]))
    else:
        return render(request, "encyclopedia/error.html", {"title": title})


def random_title(request):
    titles = util.list_entries()
    random_title = random.choice(titles)
    return redirect(reverse("entry", args=[random_title]))
