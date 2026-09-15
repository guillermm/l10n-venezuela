[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# Fiscal Report For Venezuela (Libros Fiscales)

[![License: AGPL-3](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0-standalone.html)
[![OCA/l10n-venezuela](https://img.shields.io/badge/github-OCA%2Fl10n--venezuela-lightgrey.png?logo=github)](https://github.com/OCA/l10n-venezuela)

Purchase and sale fiscal books for Odoo 17. Uses document/invoice date and VES amounts (rate required). Aliquots 8/16/31 %, exempt and SDCF. Credit notes keep the affected document. VAT withholdings follow the voucher month. Imports (05) and VAT write-offs (04). Posting locks the period. Internal QWeb PDF and Excel export (RLIVA Art. 75/76/78; not the official SENIAT XLSX template; no POS).

**Table of contents**

- [Configuration](#configuration)
- [Usage](#usage)
- [Bug Tracker](#bug-tracker)
- [Credits](#credits)
  - [Authors](#authors)
  - [Contributors](#contributors)
  - [Maintainers](#maintainers)

## Configuration

Tag taxes with their Venezuelan aliquot type (General, Reduced, Additional, Exempt, SDCF). Keep the VES rate posted for the book period.

## Usage

1. *Accounting -> Reporting -> Generate Fiscal Book Wizard*, or create a book under Purchase / Sale Fiscal Books.
2. Choose type and period; generate / update to classify posted invoices.
3. Print the QWeb report or use *Export Excel*.

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

This module is part of the [OCA/l10n-venezuela](https://github.com/OCA/l10n-venezuela/tree/17.0/l10n_ve_fiscal_book) project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
