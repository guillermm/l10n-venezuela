Venezuelan Withholding Base
===========================

Shared architecture for Venezuelan withholdings (IVA, ISLR, Municipal, SRC)
on Odoo 17:

- Withholding status on invoices (not withheld / partial / withheld).
- Payment register helpers (``_l10n_ve_append_wh_writeoff``) so each engine
  applies the retention as a write-off when registering a payment.
- Residual of the invoice decreases; no orphan journal entry if a payment exists.
