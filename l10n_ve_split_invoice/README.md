[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# Split Invoices for Venezuela

[![License: AGPL-3](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0-standalone.html)
[![OCA/l10n-venezuela](https://img.shields.io/badge/github-OCA%2Fl10n--venezuela-lightgrey.png?logo=github)](https://github.com/OCA/l10n-venezuela)

When posting a customer invoice or credit note that exceeds the company line limit, extra product lines are copied to a new draft invoice and removed from the original (`split_parent_id`).

**Table of contents**

- [Configuration](#configuration)
- [Usage](#usage)
- [Bug Tracker](#bug-tracker)
- [Credits](#credits)
  - [Authors](#authors)
  - [Contributors](#contributors)
  - [Maintainers](#maintainers)

## Configuration

Set the maximum number of product lines per invoice on the company (`lines_invoice`).

## Usage

Post a customer invoice with more product lines than the company limit. A second draft invoice is created with the overflow lines.

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

This module is part of the [OCA/l10n-venezuela](https://github.com/OCA/l10n-venezuela/tree/17.0/l10n_ve_split_invoice) project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
