from django.shortcuts import render

def dashboard(request):
    return render(request, 'dashboard.html')

def review(request):
    return render(request, 'review.html')

def own_stock(request):
    return render(request, 'own_stock.html')
