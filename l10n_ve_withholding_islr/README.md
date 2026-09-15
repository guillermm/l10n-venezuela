[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# Management Withholding ISLR Venezuelan Laws

[![License: AGPL-3](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0-standalone.html)
[![OCA/l10n-venezuela](https://img.shields.io/badge/github-OCA%2Fl10n--venezuela-lightgrey.png?logo=github)](https://github.com/OCA/l10n-venezuela)

Income tax withholding (Retención de ISLR) for Odoo 17. Official SENIAT catalog (Decreto 1.808 / PA 0095): one 3-digit code per person type (e.g. fees 002/003/004). PNRE sustraendo 83.3334 UT. Applied in Register Payment; QWeb voucher; SENIAT XML in VES (ISO-8859-1). No AR-I/ARC or payroll concept 001.

**Table of contents**

- [Configuration](#configuration)
- [Usage](#usage)
- [Bug Tracker](#bug-tracker)
- [Credits](#credits)
  - [Authors](#authors)
  - [Contributors](#contributors)
  - [Maintainers](#maintainers)

## Configuration

1. *Accounting -> Configuration -> Venezuelan Localization -> ISLR Concepts & Rates*.
2. Set the default ISLR journal and account on the company.
3. Assign the partner person type and, on bills, the ISLR concept per line.

## Usage

1. On the vendor bill, assign the ISLR concept (or inherit it from the sale/purchase line if `l10n_ve_sale_purchase` is installed).
2. Post the bill and open Register Payment; review the ISLR amount.
3. Confirm the payment to create the voucher and write-off.
4. *Accounting -> Vendors -> Vendor ISLR Withholdings* (or Customers for inbound).
5. *Accounting -> Reporting -> Generate XML SENIAT (ISLR)*.

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

This module is part of the [OCA/l10n-venezuela](https://github.com/OCA/l10n-venezuela/tree/17.0/l10n_ve_withholding_islr) project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
