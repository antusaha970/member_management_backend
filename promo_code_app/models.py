from django.db import models
from core.models import MembershipType
from member.models import Member
from django.utils import timezone


class PromoCodeBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class PromoCodeCategory(PromoCodeBaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class PromoCode(PromoCodeBaseModel):
    promo_code = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    limit = models.IntegerField()
    remaining_limit = models.IntegerField(blank=True, default=0)
    description = models.TextField()
    # foreignkey relations
    category = models.ManyToManyField(
        PromoCodeCategory)

    def __str__(self):
        return self.promo_code

    def save(self, *args, **kwargs):
        if self._state.adding:  # Only on creation
            self.remaining_limit = self.limit
        super().save(*args, **kwargs)

    def is_promo_code_valid(self):
        today = timezone.now().date()
        return (
            self.start_date <= today <= self.end_date and
            self.remaining_limit > 0
        )


class AppliedPromoCode(PromoCodeBaseModel):
    discounted_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    # foreignkey relations
    promo_code = models.ForeignKey(
        PromoCode, on_delete=models.RESTRICT, related_name="applied_promo_code")
    used_by = models.ForeignKey(
        Member, on_delete=models.RESTRICT, related_name="applied_promo_code_member")

    def __str__(self):
        return f"Promo {self.promo_code.promo_code} used by {self.used_by.member_ID} "
