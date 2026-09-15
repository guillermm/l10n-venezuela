[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# Venezuela IGTF

[![License: AGPL-3](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0-standalone.html)
[![OCA/l10n-venezuela](https://img.shields.io/badge/github-OCA%2Fl10n--venezuela-lightgrey.png?logo=github)](https://github.com/OCA/l10n-venezuela)

IGTF on payments through foreign-currency or crypto journals (Odoo 17), and optionally on vendor bills. Flag per journal; rate and accounts on the company; applied on the payment and on Register Payment. Vendor bills can add an IGTF expense line that increases the residual; the payment wizard does not auto-apply IGTF if the bill already has it. No TXT / SENIAT declaration in this version.

**Table of contents**

- [Configuration](#configuration)
- [Usage](#usage)
- [Bug Tracker](#bug-tracker)
- [Credits](#credits)
  - [Authors](#authors)
  - [Contributors](#contributors)
  - [Maintainers](#maintainers)

## Configuration

1. Company: IGTF rate (default 3 %), expense account (6601001 / fallback 9114001) and perception account (2103004). Optional perception agent flag.
2. Enable *Apply IGTF* on the bank / currency / crypto journal.
3. Vendor bills: optional *Apply IGTF* on the invoice form. The payment wizard stays off if the bill already recorded IGTF.

## Usage

1. Register a payment on a journal with IGTF enabled.
2. Review *Apply IGTF*, rate and amount on the wizard or payment form.
3. Confirm; the payment entry includes the IGTF lines and stays balanced.
4. On a vendor bill you can also tick *Apply IGTF* before posting. Do not apply it again on that payment.

## Bug Tracker

Bugs are tracked on [GitHub Issues](https://github.com/OCA/l10n-venezuela/issues). In case of trouble, please check there if your issue has already been reported. If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Do not contact contributors directly about support or help with technical issues.

## Credits

### Authors

* Guillermo Montoya

### Contributors

* Guillermo Montoya <https://github.com/guillermm>

### Maintainers

This module is maintained by the OCA.

<a href="https://odoo-community.org">
    <img src="https://odoo-community.org/logo.png" alt="Odoo Community Association" width="200" />
</a>

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

This module is part of the [OCA/l10n-venezuela](https://github.com/OCA/l10n-venezuela/tree/17.0/l10n_ve_igtf) project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
