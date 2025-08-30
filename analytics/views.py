# analytics/views.py
from datetime import timedelta, datetime, date
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from .forms import AnalyticsFilterForm

from .models import AnalyticsModel

FIELDS = [
    "students",
    "enrollments",
    "trial_enrollments",
    "payments",
    "payments_sum",
    "new_students",
    "new_enrollments",
    "courses",
]

def analytics_series_json(request):
    """
    Returns dense daily time series for requested fields.
    GET:
      days=30            (or use start=YYYY-MM-DD&end=YYYY-MM-DD)
      fields=payments_sum,enrollments  (defaults to all)
    """
    # range
    if request.GET.get("start") and request.GET.get("end"):
        start = date.fromisoformat(request.GET["start"])
        end   = date.fromisoformat(request.GET["end"])
    else:
        days = int(request.GET.get("days", 30))
        end = timezone.localdate()
        start = end - timedelta(days=days - 1)

    # fields
    req_fields = request.GET.get("fields")
    fields = [f.strip() for f in req_fields.split(",")] if req_fields else FIELDS
    fields = [f for f in fields if f in FIELDS] or ["payments_sum"]

    # fetch
    rows = (AnalyticsModel.objects
            .filter(date__range=(start, end))
            .order_by("date")
            .values("date", *FIELDS))

    # map by date
    by_day = {r["date"]: r for r in rows}

    # dense series (zero-fill)
    labels = []
    series = {f: [] for f in fields}
    d = start
    while d <= end:
        labels.append(d.isoformat())
        r = by_day.get(d)
        for f in fields:
            val = r[f] if r else 0
            # ensure plain float for sums so JSON is safe for Chart.js
            if f.endswith("_sum"):
                val = float(val or 0)
            series[f].append(val)
        d += timedelta(days=1)

    field_labels = {
        f: str(AnalyticsModel._meta.get_field(f).verbose_name) for f in fields
    }

    print(field_labels)

    return JsonResponse({"labels": labels, "series": series, "default_checked": ["payments_sum", "enrollments"]})


class AnalyticsPageView(TemplateView):
    template_name = 'analytics/linechart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_labels'] = {f: str(AnalyticsModel._meta.get_field(f).verbose_name) for f in FIELDS}
        context['filter_form'] =  AnalyticsFilterForm(initial=self.request.GET.copy())
        return context