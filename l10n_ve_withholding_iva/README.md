[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# Management Withholding VAT Venezuelan Laws

[![License: AGPL-3](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0-standalone.html)
[![OCA/l10n-venezuela](https://img.shields.io/badge/github-OCA%2Fl10n--venezuela-lightgrey.png?logo=github)](https://github.com/OCA/l10n-venezuela)

VAT withholding (Retención de IVA) for Odoo 17. Rate on the partner (75 % or 100 %); applied in Register Payment as a write-off; official QWeb voucher; TXT 99035 in VES (fortnight, latin-1).

**Table of contents**

- [Configuration](#configuration)
- [Usage](#usage)
- [Bug Tracker](#bug-tracker)
- [Credits](#credits)
  - [Authors](#authors)
  - [Contributors](#contributors)
  - [Maintainers](#maintainers)

## Configuration

On the company, set the default VAT withholding journal and account (7-digit codes). On each supplier, set the IVA withholding rate (75 % or 100 %).

## Usage

1. Post the vendor bill (no voucher is created yet).
2. *Accounting -> Vendors -> Register Payment*: review *IVA a Retener*.
3. Confirm the payment; the voucher and write-off are created together.
4. Review vouchers under *Accounting -> Vendors -> Vendor VAT Withholdings*.
5. Customer withholdings received: enter the amount and voucher number on the inbound payment wizard.
6. *Accounting -> Reporting -> Generate TXT SENIAT (IVA)*.

## Bug Tracker

Bugs are tracked on [GitHub Issues](https://github.com/OCA/l10n-venezuela/issues). In case of trouble, please check there if your issue has already been reported. If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Do not contact contributors directly about support or help with technical issues.

## Credits

### Authors

* Vauxoo
* OpenERP Venezuela

### Contributors

* Guillermo Montoya <https://github.com/guillermm>
* Nhomar Hernandez <nhomar@vauxoo.com>
* Humberto Arocha <hbto@vauxoo.com>
* Maria Gabriela Quilarque <gabriela@vauxoo.com>

### Maintainers

This module is maintained by the OCA.

<a href="https://odoo-community.org">
    <img src="https://odoo-community.org/logo.png" alt="Odoo Community Association" width="200" />
</a>

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

This module is part of the [OCA/l10n-venezuela](https://github.com/OCA/l10n-venezuela/tree/17.0/l10n_ve_withholding_iva) project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
