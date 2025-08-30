# analytics/views.py
from datetime import timedelta, datetime, date
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from users.filters import SuperUserRequired
from .forms import AnalyticsFilterForm
import json

from .models import AnalyticsModel

FIELDS = [
    "payments_sum",
    "payments",
    "students",
    "enrollments",
    "trial_enrollments",
    "new_students",
    "new_enrollments",
    "courses",
]

def analytics_series_json(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    start_str = (data.get("date_from") or "").strip()  # 'YYYY-MM-DD' or ''
    end_str = (data.get("date_to") or "").strip()  # 'YYYY-MM-DD' or ''

    today = timezone.localdate()
    start = date.fromisoformat(start_str) if start_str else today.replace(day=1)
    end = date.fromisoformat(end_str) if end_str else today


    # fields
    field = data.get("show")
    fields = [field] if field else FIELDS[1:]
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
        labels.append(d)
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

    return JsonResponse({"labels": labels, "series": series, "default_checked": ["payments_sum"], 'verbose': field_labels,})


class AnalyticsPageView(SuperUserRequired,TemplateView):
    template_name = 'analytics/linechart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_labels'] = {f: str(AnalyticsModel._meta.get_field(f).verbose_name) for f in FIELDS}
        context['filter_form'] =  AnalyticsFilterForm(initial=self.request.GET.copy())
        return context