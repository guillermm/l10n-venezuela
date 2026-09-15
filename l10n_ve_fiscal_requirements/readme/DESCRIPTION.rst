Venezuelan Fiscal Requirements
==============================

Core fiscal module for Odoo 17. Depends on the official ``l10n_ve`` chart
(7-digit account codes), official ``l10n_latam_base`` (identification
type + number on the partner) and ``territorial_pd`` (states,
municipalities and parishes taken from Mastercore 16.0). Adds:

- SENIAT control number (``nro_ctrl``): unique; auto-assigned on customer
  invoices at post; required on vendor bills.
- Document date (``date_document``) and fiscal lock on posted control numbers.
- Partner identification types (RIF, Venezuelan ID, foreign ID, passport).
  RIF is ``V/E/J/P/G/C`` plus 9 digits; cédula is ``V``/``E`` plus 6–8 digits.
  Venezuelan commercial partners require the number, and it must match
  ``person_type`` (V/cédula V → PNRE, E/cédula E → PNNR, J/C/G → PJDO,
  P → PJND, passport → PNNR/PJND).
- Tax Unit (UT) history (43.00 from 2025-06-02, G.O. 43.140).
- Current bolívar **VES** (symbol **Bs**). Official Odoo still ships VEF
  (Bs.F) as the country currency; this module switches to VES.
- VES conversion helpers that fail if no exchange rate is set (never 1:1).
- Partner SENIAT consultation (official site; captcha-dependent, no API).
- Tax aliquot classification (Exempt, General, Reduced, Additional, SDCF).
  In Accounting the taxes are named Exento, IVA 8%, IVA 16% and IVA 31%
  (sale/purchase default is IVA 16%). Official ``l10n_ve`` still ships
  12% / 22% until odoo#285425; this module rewrites those records in
  place to 16% / 31% (it does not delete them).
- Optional fiscal printer fields (no hardware driver).
- SENIAT taxpayer type (Ordinary / Formal / Special), distinct from
  ``person_type``.
- Venezuelan bank catalog (SUDEBAN 4-digit BIC) and account type
  (checking / savings / trust) on partner bank accounts. Catalog taken
  from Mastercore ``l10n_ve_base`` 16.0.
- Invoice PDF shows control number, partner/company RIF, municipality
  and parish.
