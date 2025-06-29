from django.shortcuts import render,redirect


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # (Optional) logic to validate email or send reset link
        return redirect('reset_link_sent')
    return render(request, 'accounts/forgot_password.html')