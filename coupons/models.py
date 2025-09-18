from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import UniqueConstraint


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(
        validators=[MinValueValidator(0),
        MaxValueValidator(100)],
        help_text='Percentage value (0 to 100)')
    active = models.BooleanField()
    usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    one_time_per_user = models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def clean(self):
        if self.valid_from and self.valid_to and self.valid_from >= self.valid_to:
            raise ValidationError("`valid_from` must be earlier than `valid_to`.")

    @property
    def is_available(self):
        now = timezone.now()
        return (
            self.active
            and (self.valid_from <= now <= self.valid_to)
            and (self.usage_limit > self.used_count)
        )

    def __str__(self):
        return f"{self.code} (-{self.discount}%)"    

class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'coupon'], name='unique_active_coupon')
        ]