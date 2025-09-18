from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
from .models import Cart, Receiver

@shared_task
def send_receipt_email(user_email, cart_id, receiver_id):
    cart = Cart.objects.get(id=cart_id)
    receiver = Receiver.objects.get(id=receiver_id)
    context = {
        'order': cart,
        'receiver': receiver
    }
    html_content = render_to_string('carts/email_receipt.html', context)
    pdf_content = render_to_pdf('carts/pdf_receipt.html', context)

    subject = "Payment Successful - Your Order Receipt"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    email = EmailMultiAlternatives(subject, html_content, from_email, recipient_list)
    email.attach_alternative(html_content, "text/html")
    if pdf_content:
        email.attach('receipt.pdf', pdf_content, 'application/pdf')

    email.send()


def render_to_pdf(template_src, context_dict={}):
    template_string = render_to_string(template_src, context_dict)
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(template_string.encode("UTF-8")), dest=result)
    if pdf.err:
        return None
    return result.getvalue()
