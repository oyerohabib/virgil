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

    today = datetime.datetime.now()

    page_title = "Dashboard"
    Errors = Error.objects.all().order_by("-id")[:4]
    Transactions = Transaction.objects.all().order_by("-id")[:4]

    queryset = Transaction.objects.values('created_at__month').annotate(sum= Sum('cigarettecounter')).filter(created_at__year=today.year, status="completed").order_by('created_at__month')

    queryset2 = Transaction.objects.values('created_at__day').filter(created_at__year=today.year, created_at__month=today.month,status="completed").annotate(sum= Sum('cigarettecounter')).order_by('created_at__month')

    queryset3 = Transaction.objects.values('created_at__year').filter(status="completed").annotate(sum= Sum('cigarettecounter')).order_by('created_at__year')

    month_range = ['04', '06', '11', '09']

    data = {
        r['created_at__month']: r['sum'] for r in queryset
    }

    data = {
        datetime.date(1900, m, 1).strftime('%b'): data.get(m, 0)
        for m in range(1, 13)
    }

    days = {
        r['created_at__day']: r['sum'] for r in queryset2
    }

    # print(queryset3)
    if today.month in month_range:
        data2 = {
            datetime.date(today.year, today.month, m).strftime('%d'): days.get(m, 0)
            for m in range(1, 31)
        }
    else:
        data2 = {
            datetime.date(today.year, today.month, m).strftime('%d'): days.get(m, 0)
            for m in range(1, 32)
        }

    data3 = {
        r['created_at__year']: r['sum'] for r in queryset3
    }
    
    data4 = {
        datetime.date(m, today.month, 1).strftime('%Y'): data3.get(m, 0)
        for m in range(today.year-11, today.year+1)
    }

    context = {"page_title":page_title, "errors":Errors, "transactions":Transactions, "data":data2, "monthly": data, "yearly": data4, "present_month": datetime.date(today.year, today.month, today.day).strftime('%m-%Y')}

    # print(data4)
    try:
        if request.GET['chart_type'] == 'monthly':
            print(data)
            context["data"] = data
            
        if request.GET['chart_type'] == 'yearly':
            print(data4)
            context["data"] = data4
    except Exception as e:
        # print(e)
        pass

    try:
        if '-' in request.GET['date']:
            # print(request.GET['chart_type'])
            yrmn = request.GET['date'].split('-')

            queryset2 = Transaction.objects.values('created_at__day').filter(created_at__year=yrmn[0], created_at__month=yrmn[1],status="completed").annotate(sum= Sum('cigarettecounter')).order_by('created_at__year')

            days = {
                r['created_at__day']: r['sum'] for r in queryset2
            }

            if yrmn[1] in month_range:
                data5 = {
                    datetime.date(int(yrmn[0]), int(yrmn[1]), m).strftime('%d'): days.get(m, 0)
                    for m in range(1, 31)
                }
            else:
                data5 = {
                    datetime.date(int(yrmn[0]), int(yrmn[1]), m).strftime('%d'): days.get(m, 0)
                    for m in range(1, 32)
                }
            # print(data5)
            context["data"] = data5
    except Exception:
        pass
    

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
@admin_required()
def terminal_page(request):
    page_title = "Terminal Page"
    if request.method == 'POST':
        try:
            unit_price = request.POST['unit_price']
            terminal = TerminalSettings.objects.create(user=request.user, unit_price=unit_price)
            terminal.save()
            messages.success(request, "Terminal Activated Successfully")
            return redirect('terminal_page')
        except Exception as e:
            messages.error(request, "Error in Activating Terminal")
            return redirect('terminal_page')

    terminals = TerminalSettings.objects.all().order_by("-date_created")

    context = {"page_title":page_title, "terminals":terminals}
    return render(request, "core/terminal.html", context)

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

            messages.success(request, ('Please User with email - {email} should confirm your email to complete registration.'.format(email=user.email)))
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
    feedbacks = FeedBack.objects.all().order_by("-id")
    context = {"page_title":page_title, "feedbacks": feedbacks}
    return render(request, 'core/reply_message.html', context)

def feeds(request, id):
    page_title = "Messages"

    feed = FeedBack.objects.get(id=id)

    msgs = Message.objects.filter(message_in=feed).order_by("created_at")

    allow_access_for = User.objects.filter(user_type__is_manager=True)

    try:
        permit = MessagePermission.objects.get(feedback=feed)
    except Exception or FieldDoesNotExist:
        permit = None

    if request.POST:
        # print()
        msg = Message.objects.create(user_id=request.user, message_in=feed, feedback_reply=request.POST['feedback_reply'])
        msg.save()
        return redirect(f'/feeds/{id}')

    context = {"page_title":page_title, "msgs": msgs, "feed": feed, "allow_access_for": allow_access_for, "permitted": permit}

    return render(request, 'core/feed_message.html', context)

def InviteUser(request, id, user_id):
    page_title = "Messages"

    feed = FeedBack.objects.get(id=id)

    user_ = User.objects.get(id=user_id)

    try:
        msg_ = MessagePermission.objects.get(user=user_)
        messages.error(request, "User Already Added.")
        return redirect(f'/feeds/{id}')
    except Exception or TypeError:

        msg = MessagePermission.objects.create(user=user_, feedback=feed)
        msg.save()
        messages.success(request, "User Added Successfully")
        return redirect(f'/feeds/{id}')


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
    feedback_data = FeedBack.objects.filter(user=user_obj).order_by("-id")
    invites = MessagePermission.objects.filter(user=user_obj).order_by("-id")

    if request.POST:
        # print()
        feed = FeedBack.objects.create(user=request.user, name=request.POST['feedback_message'])
        feed.save()
        return redirect(f'/feeds/{feed.id}')

    context = {"page_title":page_title, "feedback_data": feedback_data, "invites": invites}
    return render(request, 'core/manager_message.html', context)

@login_required
@admin_required()
def close_feed(request, id):
    page_title = "Close Feedback"
    feedback_data = FeedBack.objects.get(id=id)

    feedback_data.is_closed = True
    feedback_data.save()

    messages.success(request, "Feedback Closed")
    return redirect(f'/feeds/{id}')

@login_required
@admin_required()
def open_feed(request, id):
    page_title = "Open Feedback"
    feedback_data = FeedBack.objects.get(id=id)

    feedback_data.is_closed = False
    feedback_data.save()

    messages.success(request, "Feedback Re Opened")
    return redirect(f'/feeds/{id}')


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