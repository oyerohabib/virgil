from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import *
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import *
from .decorators import manager_required, admin_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from core.tokens import account_activation_token
from django.views.generic import View, DetailView, ListView
from django.core.mail import send_mail
from .constants import Actions
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

# Create your views here.

@login_required
def Dashboard(request):

    page_title = "Dashboard"
    Errors = Error.objects.all().order_by("-id")[:4]
    Transactions = Transaction.objects.all().order_by("-id")[:4]

    queryset = Transaction.objects.values('created_at__month').annotate(sum= Sum('cigarettecounter')).order_by('created_at__month')

    data = {
        r['created_at__month']: r['sum'] for r in queryset
    }

    data = {
        datetime.date(1900, m, 1).strftime('%b'): data.get(m, 0)
        for m in range(1, 13)
    }

    context = {"page_title":page_title, "errors":Errors, "transactions":Transactions, "data":data}

    return render(request, "core/index.html", context)

@login_required
def Errors(request):

    page_title = "List of Errors"
    Errors = Error.objects.all().order_by("-id")

    context = {"page_title":page_title, "errors":Errors}

    return render(request, "core/errors.html", context)

@login_required
def ErrorDetail(request, pk):
    
    page_title = "Error Detail Page"
    errordetail = Error.objects.get(id=pk)
    e_form = UpdateErrorForm(instance=errordetail)
    mydict={'e_form':e_form}
    if request.method == 'POST':
        e_form = UpdateErrorForm(request.POST, request.FILES, instance=errordetail)
        if e_form.is_valid():
            e_form.save()
            return redirect(request.path)
            messages.success(request, "Error Updated Successfully")

    context = {"page_title":page_title, "errordetail":errordetail, 'e_form':e_form}

    return render(request, "core/errordetail.html", context)

@login_required
def Transactions(request):

    page_title = "List of Transactions"
    Transactions = Transaction.objects.all().order_by("-id")

    context = {"page_title":page_title, "transactions":Transactions}

    return render(request, "core/transactions.html", context)

@login_required
def TransactionDetail(request, pk):

    page_title = "Transaction Detail Page"
    transactionsdetails = Transaction.objects.get(id=pk)
    form = UpdateTransactionForm(instance=transactionsdetails)
    if request.method == 'POST':
        form = UpdateTransactionForm(request.POST, instance=transactionsdetails)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction Form updated Successfully")
            return redirect(request.path)

    context = {"page_title":page_title, "transactions":transactionsdetails, 'form':form}

    return render(request, "core/transactionsdetails.html", context)

@login_required
def Stations(request):

    page_title = "List of Stations"
    Stations = Station.objects.all().order_by("-id")

    context = {"page_title":page_title, "stations":Stations}

    return render(request, "core/stations.html", context)

@login_required
@admin_required()
def AddStation(request):

    page_title = "Add Station Page"
    form = StationForm()
    if request.method == 'POST':
        form = StationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Station Added Successfully")
            return redirect('stations')

    context = {"page_title":page_title, "form":form}

    return render(request, "core/addstation.html", context)

@login_required
@admin_required()
def EditStation(request, pk):

    page_title = "Edit Station Page"
    station = Station.objects.get(id=pk)

    form = StationForm(instance=station)
    if request.method == 'POST':
        form = StationForm(request.POST, instance=station)
        if form.is_valid():
            form.save()
            messages.success(request, "Station Edited Successfully")
            return redirect('stations')

    context = {"page_title":page_title, "form":form}

    return render(request, "core/editstation.html", context)

@login_required
@admin_required()
def DeleteStation(request, pk):

    page_title = "Delete Station"
    station = Station.objects.get(id=pk)
    station.delete()
    messages.error(request, "Station Deleted Successfully")
    return redirect('stations')

    context = {"page_title":page_title, "station":station}

    return render(request, "core/stations.html", context)

@login_required
@admin_required
def Users(request):

    page_title = "All Users"
    Users = User.objects.all().exclude(id=request.user.pk).order_by("-id")

    context = {"page_title":page_title, "users":Users}
    return render(request, "core/users.html", context)

@login_required
@admin_required
def AddUser(request):

    page_title = "Add New User"
    if request.method == "POST":
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        address = request.POST.get('address')
        zipcode = request.POST.get('zipcode')
        city = request.POST.get('city')
        region = request.POST.get('region')
        country = request.POST.get('country')
        password = User.objects.make_random_password()

        usertype = request.POST.get("usertype")

        try:
            user = User.objects.create_user(email=email, telephone=telephone, firstname=firstname, password=password,
                lastname=lastname, address=address, zipcode=zipcode, city=city, country=country)

            is_admin = False
            is_manager = False

            if usertype == "M":
                is_manager = True
            elif usertype == "A":
                is_admin = True

            usertype = user_type.objects.create(
                user=user, is_admin=is_admin, is_manager=is_manager
            )

            user.is_active = False # Deactivate account till it is confirmed
            user.save()
            recipients=[email]
            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            message = render_to_string('auth/password/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            send_mail(subject, message, None, recipients, fail_silently=False)

            messages.success(request, ('Please Confirm your email to complete registration.'))
            return redirect('users')
        except Exception as e:
            messages.error(request, "Failed to Create User!" + str(e))
            return redirect('users')

    return render(request, "core/adduser.html", {"page_title": page_title})

class ActivateAccount(View):

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.profile.email_confirmed = True
            user.save()
            login(request, user)
            messages.success(request, ('Your account has been confirmed. Please reset your password by clicking the top-right icon.'))
            return redirect('index')
        else:
            messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
            return redirect('index')

@login_required
@admin_required
def ViewUserProfile(request, pk):
    page_title = "User Profile"
    user = User.objects.get(id=pk)
    context = {"page_title":page_title, "user":user}
    return render(request, "core/viewuserprofile.html", context)

@login_required
@admin_required
def DeleteUser(request, pk):
    user = User.objects.get(id=pk)
    user.delete()
    messages.error(request, "User Deleted Successfully")
    return redirect('users')

def manager_feedback_message(request):
    page_title = "Manage Feedback Message"
    feedbacks = Message.objects.all().order_by("-id")
    context = {"page_title":page_title, "feedbacks": feedbacks}
    return render(request, 'core/reply_message.html', context)


@csrf_exempt
def manager_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = Message.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def manager_feedback(request):
    page_title = "Manager Feedback"
    user_obj = User.objects.get(id=request.user.id)
    feedback_data = Message.objects.filter(user_id=user_obj).order_by("-id")
    context = {"page_title":page_title, "feedback_data": feedback_data}
    return render(request, 'core/manager_message.html', context)


def manager_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('manager_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        user_obj = User.objects.get(id=request.user.id)

        try:
            add_feedback = Message(user_id=user_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('manager_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('manager_feedback')
    
@login_required()
def Profile(request):

    page_title = "Profile Page"
    user_id = request.user.id
    user = User.objects.get(id=user_id)

    form = ProfileForm(instance=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')

    context = {"page_title":page_title, "user":user, "form":form}

    return render(request, "auth/profile.html", context)


@method_decorator(login_required, name='dispatch')
class NotificationListView(ListView):
    model = Notification
    context_object_name = 'notifications'
    paginate_by = 100
    ordering = '-date'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.request.user.notifications.filter(is_seen=False).update(is_seen=True)
        return response


@method_decorator(login_required, name='dispatch')
class NotificationDetailView(DetailView):
    model = Notification
    context_object_name = 'notification'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not self.object.is_read:
            self.object.is_read = True
            self.object.save(update_fields=['is_read'])
        return response


@login_required
def unread(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-date')
    notifications.update(is_seen=True)
    context = {"page_title":page_title, 'notifications': notifications[:5], 'Actions': Actions}
    html = render_to_string('notifications/_unread.html', context, request)
    return JsonResponse({'html': html})


@login_required
@require_POST
@csrf_exempt
def mark_all_as_read(request):
    request.user.notifications.update(is_read=True, is_seen=True)

    # If the request is ajax, it means it came from the small notifications widget on the top menu
    if request.is_ajax():
        return unread(request)

    return redirect('notifications')


@login_required
@require_POST
@csrf_exempt
def clear_all(request):
    request.user.notifications.all().delete()

    # If the request is ajax, it means it came from the small notifications widget on the top menu
    if request.is_ajax():
        return unread(request)

    return redirect('notifications')

    
def Login(request):
    page_title = "Login Page"
    if request.user.is_authenticated:
        return redirect('/')

    else:
        if (request.method == 'POST'):
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                type_obj = user_type.objects.get(user=user)
                if user.is_authenticated and type_obj.is_admin:
                    return redirect('index') #Go to Admin home
                elif user.is_authenticated and type_obj.is_manager:
                    return redirect('index') #Go to Manager home
            else:
                messages.info(request, 'Email or Password is incorrect')

        return render(request, "auth/login.html", {"page_title":page_title})

def Logout(request):
	logout(request)
	return redirect('login')

def Error404(request, exception):
    page_title = "Page Not Found"
    return render(request, "error/404.html", {"page_title":page_title})

def Error500(request):
    page_title = "Server Error"
    return render(request, "error/500.html", {"page_title":page_title})