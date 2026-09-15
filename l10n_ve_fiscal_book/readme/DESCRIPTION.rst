Fiscal Report For Venezuela
===========================

Purchase and sale fiscal books for Odoo 17:

- Uses document date / invoice date and amounts in VES (rate required).
- Aliquots 8 %, 16 % and 31 %, plus exempt and SDCF when tagged.
- Credit/debit notes keep the affected document number (negative amounts).
- VAT withholdings are shown in the voucher period, even if the invoice
  belongs to another month.
- Posting the book locks the period: no new invoices of that type can be
  posted until an accounting manager reopens it.
- One open book per type, company and overlapping dates.
- Imports (Form 86) as document type 05 with expediente.
- VAT write-offs of the period as type-04 adjustment lines.
- Internal QWeb PDF (RLIVA Art. 75/76/78) and Excel export of the same
  columns. Not the official SENIAT XLSX template; no POS.
