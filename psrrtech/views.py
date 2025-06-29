from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # (Optional) logic to validate email or send reset link
        return redirect('reset_link_sent')
    return render(request, 'accounts/forgot_password.html')

@login_required
def dashboard_router(request):
    role = getattr(request.user.profile, "role", None)

    if role == 'admin':
        return render(request, 'psrrtech/dashboard/admin_dashboard.html')
    elif role == 'hr':
        return render(request, 'psrrtech/dashboard/hr_dashboard.html')
    elif role == 'employee':
        return render(request, 'psrrtech/dashboard/employee_dashboard.html')
    else:
        return render(request, '403.html', status=403) 