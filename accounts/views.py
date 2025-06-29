from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def contact_us(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # You can send email or save it to the DB
            messages.success(request, "Thanks for contacting us. We'll get back to you soon.")
            return redirect('contact_us')
    else:
        form = ContactForm()
    return render(request, 'accounts/contact_us.html', {'form': form})
