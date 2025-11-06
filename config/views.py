from django.shortcuts import render

def home_view(request):
    """
    Vista principal (pàgina inicial del projecte).
    Mostra un missatge de benvinguda i opcions segons si l'usuari està autenticat.
    """
    return render(request, 'home.html')
