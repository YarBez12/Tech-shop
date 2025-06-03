from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
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

    @property
    def is_available(self):
        return self.active and (self.usage_limit > self.used_count)

    def __str__(self):
        return self.code
    

class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'coupon')