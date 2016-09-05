from django.shortcuts import render


def school(request):
    return render(request, 'school/school.html')