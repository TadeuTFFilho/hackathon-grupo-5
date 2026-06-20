from django.db import models
from .rules import check_prescribed, DEBT_TYPE_LABELS


class UserProfile(models.Model):
    cpf            = models.CharField(max_length=14, unique=True)
    name           = models.CharField(max_length=200)
    email          = models.CharField(max_length=200, blank=True)
    phone          = models.CharField(max_length=20, blank=True)
    birthdate      = models.CharField(max_length=10, blank=True)
    # endereço
    street         = models.CharField(max_length=300, blank=True)
    neighborhood   = models.CharField(max_length=200, blank=True)
    city           = models.CharField(max_length=200, blank=True)
    state          = models.CharField(max_length=2, blank=True)
    zip_code       = models.CharField(max_length=9, blank=True)
    # financeiro
    monthly_income = models.FloatField(default=0)
    password_hash  = models.CharField(max_length=300)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "userprofile"

    def __str__(self):
        return f"{self.name} ({self.cpf})"

    def to_session_dict(self):
        return {
            "cpf":       self.cpf,
            "name":      self.name,
            "email":     self.email,
            "phone":     self.phone,
            "birthdate": self.birthdate,
            "address": {
                "street":       self.street,
                "neighborhood": self.neighborhood,
                "city":         self.city,
                "state":        self.state,
                "zip":          self.zip_code,
            },
            "is_db_user": True,
            "db_pk":      self.pk,
        }


class Debt(models.Model):
    DEBT_TYPE_CHOICES = [(k, v) for k, v in DEBT_TYPE_LABELS.items()]
    STATUS_CHOICES = [
        ("",               "Ativa"),
        ("em_negociacao",  "Em Negociação"),
        ("paga",           "Paga"),
    ]

    user            = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="debts")
    creditor        = models.CharField(max_length=200)
    type            = models.CharField(max_length=50, choices=DEBT_TYPE_CHOICES, default="outros")
    total_amount    = models.FloatField()
    monthly_payment = models.FloatField(default=0)
    due_date        = models.CharField(max_length=10, blank=True, null=True)
    debt_status     = models.CharField(max_length=20, blank=True, default="")
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = "debt"
        ordering  = ["created_at"]

    def __str__(self):
        return f"{self.creditor} — {self.user.name}"

    def to_dict(self, index=None):
        return {
            "id":              index if index is not None else self.pk,
            "db_pk":           self.pk,
            "creditor":        self.creditor,
            "type":            self.type,
            "type_label":      DEBT_TYPE_LABELS.get(self.type, "Outros"),
            "total_amount":    self.total_amount,
            "monthly_payment": self.monthly_payment,
            "due_date":        self.due_date or None,
            "debt_status":     self.debt_status,
            "is_prescribed":   check_prescribed(self.due_date),
        }
