from django.shortcuts import render


def home(request):
    return render(request, "adtsolcre_list.html")
