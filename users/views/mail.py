from django.urls import reverse_lazy
from users.forms import MailForm
from users.models import User
from users.tasks import send_email_task
from django.views.generic.edit import FormView



class SendMailView(FormView):
    template_name = 'users/send_mail.html'
    form_class = MailForm
    success_url = reverse_lazy('main:index')  
    extra_context = {'title' : 'Sending email'}

    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        html_message = form.cleaned_data.get('html_message', '')
        recipients = list(User.objects.all().values_list('email', flat=True))
        
        for recipient in recipients:
            send_email_task.delay(subject, message, html_message, recipient)
        return super().form_valid(form)
    