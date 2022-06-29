from django.db import models


# Create your models here.

class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name="User ID",
        unique=True,
    )
    current_account = models.TextField(
        verbose_name="Current account",
        null=True
    )
    language = models.TextField(
        verbose_name="language",
        null=True
    )
    payment_type = models.TextField(
        verbose_name="Payment type",
        null=True,
    )

    def __str__(self):
        return f"#{self.external_id}"

    class Meta:
        verbose_name = "Profile"


class Message(models.Model):
    message_id = models.PositiveIntegerField(
        verbose_name="Message ID",
        unique=True,
        null=True,
    )
    profile = models.ForeignKey(
        to='ugc.Profile',
        verbose_name="Profile",
        on_delete=models.PROTECT,
        null=True,
    )
    btcPrice = models.TextField(
        verbose_name="BTC Price",
        null=True,
    )
    fiatPrice = models.TextField(
        verbose_name="Fiat Price",
        null=True,
    )
    account = models.TextField(
        verbose_name="Account",
        null=True,
    )
    status = models.TextField(
        verbose_name="Status",
        null=True,
    )

    created_at = models.DateTimeField(
        verbose_name="Receiving time",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Message"


class TypeOfRequisites(models.Model):
    CHOICES = (
        ('On', 'On'),
        ('Off', 'Off'),
    )
    typeOfRequisites = models.TextField(
        verbose_name="Requisites Type",
        null=True,
        unique=True,
    )
    active = models.CharField(
        max_length=3,
        verbose_name="Requisites Type",
        null=True,
        choices=CHOICES,

    )

    def __str__(self):
        return f"#{self.typeOfRequisites}"

    class Meta:
        verbose_name = "Type of Requisites"


class Type(models.Model):
    type = models.ForeignKey(
        to='ugc.TypeOfRequisites',
        verbose_name="Requisites Type",
        on_delete=models.PROTECT,
        null=True,
    )
    number = models.TextField(
        verbose_name="Number",
    )
    percent = models.TextField(
        verbose_name="Percent",
        null=True,
        editable=True,
    )

    def __str__(self):
        return f"#{self.type.typeOfRequisites} {self.number}"

    class Meta:
        verbose_name = "Requisites data"


class Requisites(models.Model):
    type = models.ForeignKey(
        to='ugc.Type',
        verbose_name="Requisites Type",
        on_delete=models.PROTECT,
        null=True
    )
    profile = models.ForeignKey(
        to='ugc.Profile',
        verbose_name="Profile",
        on_delete=models.PROTECT,
    )
    paymentUserType = models.TextField(
        verbose_name="User Payment Type",
        null=True,
    )
    btcPrice = models.TextField(
        verbose_name="BTC Price",
    )
    fiatPrice = models.TextField(
        verbose_name="Fiat Price",
    )
    created_at = models.DateTimeField(
        verbose_name="Receiving time",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Requisites"
