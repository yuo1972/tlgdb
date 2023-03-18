from django.db import models


class Tlg(models.Model):
    un_name = models.CharField(max_length=12, unique=True)
    inp_gate_date = models.DateTimeField()
    inp_chan = models.CharField(max_length=12)
    inp_num = models.CharField(max_length=4)
    inp_prz = models.CharField(max_length=30)
    ref = models.CharField(max_length=40)
    kn = models.CharField(max_length=30)
    categ = models.CharField(max_length=3)
    fl_uved_bool = models.BooleanField(default=False)
    fl_urgent_bool = models.BooleanField(default=False)
    pp = models.TextField()
    address = models.TextField()
    subscribe = models.TextField()
    out_gate_date = models.DateTimeField()
    out_chan = models.CharField(max_length=12)
    out_num = models.CharField(max_length=4)
    out_prz = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Телеграммы"
