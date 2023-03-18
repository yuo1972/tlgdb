from django_filters import rest_framework as dj_filters
from .models import Tlg


class TlgFilterSet(dj_filters.FilterSet):

    inp_chan = dj_filters.CharFilter(lookup_expr="istartswith")
    out_chan = dj_filters.CharFilter(lookup_expr="istartswith")
    kn = dj_filters.CharFilter(lookup_expr="iregex")
    pp = dj_filters.CharFilter(lookup_expr="iregex")
    address = dj_filters.CharFilter(lookup_expr="iregex")
    subscribe = dj_filters.CharFilter(lookup_expr="iregex")
    datei = dj_filters.DateFromToRangeFilter(field_name="inp_gate_date")

    order_by_field = "ordering"

    class Meta:
        model = Tlg
        fields = [
            "un_name",
            "inp_num",
            "out_num",
        ]
