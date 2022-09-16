from django.db import models


# Create your models here.

class Profile(models.Model):
    CHOICES = (
        ('Lock', 'Lock'),
        ('Unlock', 'Unlock'),
    )
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
    last_lime = models.TextField(
        verbose_name="Last time of Request",
        null=True,
    )
    request_count = models.TextField(
        verbose_name="Count of Request",
        null=True,
    )
    status = models.TextField(
        verbose_name="Status",
        choices=CHOICES,
        null=True,
    )
    currency = models.TextField(
        verbose_name="Currency",
        null=True,
    )
    access = models.TextField(
        verbose_name='Access',
        null=True,
    )

    def __str__(self):
        return f"#{self.external_id}"

    class Meta:
        verbose_name = "Profile"


class Admin(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name="User ID",
        unique=True,
    )
    name = models.TextField(
        verbose_name="name",
        null=True
    )

    def __str__(self):
        return f"#{self.external_id}"

    class Meta:
        verbose_name = "Admin"


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
    present = models.TextField(
        verbose_name="Present",
        null=True,
    )
    payment_type = models.TextField(
        verbose_name="Payment type",
        null=True,
    )
    number_of_payment = models.TextField(
        verbose_name="Number",
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
    percent = models.TextField(
        verbose_name="Percent",
        null=True,
        editable=True,
    )
    min_amount = models.TextField(null=True)
    max_amount = models.TextField(null=True)

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

    currentPrice = models.TextField(
        verbose_name="Current Price",
        null=True,
        default='0',
    )

    limit = models.TextField(
        verbose_name="Limit",
        null=True,
    )

    def __str__(self):
        return f"#{self.type.typeOfRequisites} {self.number}"

    class Meta:
        verbose_name = "Requisites data"


class Config(models.Model):
    min_amount = models.TextField(null=True)
    max_amount = models.TextField(null=True)

    class Meta:
        verbose_name = "Config"


class Request(models.Model):
    profile = models.ForeignKey(
        to='ugc.Profile',
        verbose_name="Profile",
        on_delete=models.PROTECT,
    )
    type = models.TextField(
        verbose_name="Requisites Type",
        null=True,
    )
    amount = models.TextField(
        verbose_name="Amount",
    )
    time = models.TextField(
        verbose_name="time",
        null=True,
    )

    class Meta:
        verbose_name = "Request"


class CleanBTC(models.Model):
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
    account = models.TextField(
        verbose_name="Account",
        null=True,
    )
    status = models.TextField(
        verbose_name="Status",
        null=True,
    )
    present = models.TextField(
        verbose_name="Present",
        null=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Receiving time",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Clean BTC"


class CleanAccount(models.Model):
    account = models.TextField(
        verbose_name="Account",
        null=True,
    )

    class Meta:
        verbose_name = "BTC Account"


class QueueToReq(models.Model):
    profile = models.TextField(
        verbose_name="Account",
        null=True,
    )
    paymentUserType = models.TextField(
        verbose_name="User Payment Type",
        null=True,
    )
    fiatPrice = models.TextField(
        verbose_name="Fiat Price",
        null=True
    )

    class Meta:
        verbose_name = "Queue To Requisites"
