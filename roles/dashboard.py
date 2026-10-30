"""Indicadores de facturación; las lecturas acumuladas no son consumo mensual."""
from datetime import date
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from boletas.models import Boleta
from medidores.models import Medidor
from tarifas.models import Tarifa
from usuarios.models import Usuario


def dashboard_context(today=None):
    today = today or timezone.localdate()
    current = today.replace(day=1)
    months = []
    for offset in range(5, -1, -1):
        index = current.year * 12 + current.month - 1 - offset
        months.append(date(index // 12, index % 12 + 1, 1))
    index = current.year * 12 + current.month
    end = date(index // 12, index % 12 + 1, 1)
    monthly = Boleta.objects.filter(fecha_emision__gte=current, fecha_emision__lt=end)
    totals = monthly.aggregate(amount=Sum('total_a_pagar'), volume=Sum('consumo_total'))
    paid = monthly.filter(pagado=True).aggregate(total=Sum('total_a_pagar'))['total'] or Decimal('0')
    billed = totals['amount'] or Decimal('0')
    rows = Boleta.objects.filter(fecha_emision__gte=months[0], fecha_emision__lt=end).annotate(
        month=TruncMonth('fecha_emision')).values('month').annotate(total=Sum('consumo_total'))
    values = {row['month']: row['total'] or Decimal('0') for row in rows}
    maximum = max([values.get(month, 0) for month in months] + [1])
    labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    trend = [{'label': f'{labels[m.month-1]} {m.year}', 'total': values.get(m, 0),
              'height': float(values.get(m, 0) / maximum * 100)} for m in months]
    return {
        'today': today, 'total_usuarios': Usuario.objects.count(),
        'medidores_activos': Medidor.objects.filter(estado='activo').count(),
        'medidores_atencion': Medidor.objects.filter(estado__in=['mantenimiento', 'danado']).count(),
        'tarifa_actual': Tarifa.objects.filter(activo=True).order_by('-fecha_vigencia').first(),
        'facturado_mes': billed, 'pagado_mes': paid,
        'pendiente_mes': billed - paid, 'volumen_facturado_mes': totals['volume'] or Decimal('0'),
        'porcentaje_pagado': round(paid / billed * 100) if billed else 0,
        'boletas_mes': monthly.count(), 'trend': trend,
        'recent_bills': Boleta.objects.select_related('usuario').order_by('-fecha_emision', '-pk')[:6],
    }
