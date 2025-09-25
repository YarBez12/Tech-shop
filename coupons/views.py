from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Coupon, CouponUsage
from .forms import CouponApplyForm
from django.contrib import messages


@require_POST
def coupon_apply(request):
    now = timezone.now()
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code'].strip()
        coupon = (Coupon.objects
                .only('id', 'code', 'usage_limit', 'used_count', 'one_time_per_user')
                .filter(code__iexact=code,
                        valid_from__lte=now,
                        valid_to__gte=now,
                        active=True)
                .first())
        if not coupon:
            request.session.pop('coupon_id', None)
            messages.error(request, 'Invalid coupon!')
            return redirect('carts:cart')
        if coupon.one_time_per_user and request.user.is_authenticated:
            if CouponUsage.objects.filter(user=request.user, coupon=coupon).exists():
                messages.error(request, "You have already used this coupon")
                request.session.pop('coupon_id', None)
            else:
                request.session['coupon_id'] = coupon.id
                messages.success(request, f'Coupon "{coupon.code}" applied.')
        elif coupon.usage_limit <= coupon.used_count:
            request.session.pop('coupon_id', None)
            messages.error(request, 'Coupon has already been used the maximum number of times.')
        else:
            request.session['coupon_id'] = coupon.id
            messages.success(request, f'Coupon "{coupon.code}" applied.')
    return redirect('carts:cart')