from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
try:
    from xhtml2pdf import pisa
except ImportError:
    pisa = None
from payments.models import Invoice, Expense
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.utils import timezone

class FinancialReportPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        template_path = 'reports/financial_report_pdf.html'
        total_revenue = Invoice.objects.filter(status=Invoice.InvoiceStatus.PAID).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        
        context = {
            'revenue': total_revenue,
            'expenses': total_expenses,
            'profit': total_revenue - total_expenses,
            'recent_invoices': Invoice.objects.order_by('-created_at')[:20],
            'report_date': timezone.now(),
        }
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="financial_report.pdf"'
        
        template = get_template(template_path)
        html = template.render(context)
        
        if not pisa:
            return HttpResponse('PDF generation library (xhtml2pdf) not installed. Please run "pip install xhtml2pdf".')
        
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
           return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
