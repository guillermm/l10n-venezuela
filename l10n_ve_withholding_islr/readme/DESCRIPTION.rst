Management Withholding ISLR Venezuelan Laws
============================================

Income tax withholding (Retención de ISLR) for Odoo 17:

- Official SENIAT concept catalog (Decreto 1.808 / PA 0095). Each activity
  has one code per person type (PNRE / PNNR / PJDO / PJND). Example:
  professional fees are 002 / 003 / 004, not a single concept code.
- PNRE sustraendo uses 83.3334 UT (Reglamento). The XML field
  ``CodigoConcepto`` comes from the rate of the partner type, in VES.
- Applied when registering a payment (write-off).
- Official withholding voucher (QWeb).
- SENIAT XML export in VES (ISO-8859-1).

Payroll / salary concept 001 and AR-I / ARC declarations are out of scope.
