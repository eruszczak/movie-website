from django.shortcuts import render


def index(request):
    context = {

    }
    return render(request, 'book/index.html', context)