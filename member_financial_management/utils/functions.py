import uuid
from ..models import Invoice, Sale


def generate_unique_invoice_number():
    while True:
        unique_id = f"INV-{uuid.uuid4().hex[:8].upper()}"  # e.g., INV-1A2B3C4D
        if not Invoice.objects.filter(invoice_number=unique_id).exists():
            return unique_id


def generate_unique_sale_number():
    while True:
        unique_id = f"SAL-{uuid.uuid4().hex[:8].upper()}"  # e.g., SAL-1A2B3C4D
        if not Sale.objects.filter(sale_number=unique_id).exists():
            return unique_id
