[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# Venezuelan Municipalities and Parishes

[![License: LGPL-3](https://img.shields.io/badge/licence-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0-standalone.html)
[![OCA/l10n-venezuela](https://img.shields.io/badge/github-OCA%2Fl10n--venezuela-lightgrey.png?logo=github)](https://github.com/OCA/l10n-venezuela)

Political division of Venezuela: 24 states, municipalities and parishes, plus country nationality (gentilicio).

**Taken from** [`territorial_pd` 16.0](https://github.com/odoo-mastercore/odoo-venezuela/tree/16.0/territorial_pd) by **SINAPSYS GLOBAL SA** and **MASTERCORE SAS**. Partner address fields follow `l10n_ve_base` of the same repository. Adapted to Odoo 17 by Guillermo Montoya.

**Table of contents**

- [Configuration](#configuration)
- [Usage](#usage)
- [Bug Tracker](#bug-tracker)
- [Credits](#credits)
  - [Authors](#authors)
  - [Contributors](#contributors)
  - [Maintainers](#maintainers)

## Configuration

1. Install this module before `l10n_ve_fiscal_requirements` (that module depends on it).
2. *Contacts -> Configuration -> Localization -> Municipalities / Parishes*.
3. On a Venezuelan contact: State, then Municipality, then Parish.

Municipal withholding (`l10n_ve_withholding_muni`) uses this same municipality catalog for ordinance rates.

## Usage

Municipality and Parish appear on the partner form when the country is Venezuela.

## Bug Tracker

Bugs are tracked on [GitHub Issues](https://github.com/OCA/l10n-venezuela/issues). In case of trouble, please check there if your issue has already been reported. If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Do not contact contributors directly about support or help with technical issues.

## Credits

### Authors

* SINAPSYS GLOBAL SA
* MASTERCORE SAS
* Guillermo Montoya

### Contributors

* Reydi Hernández <rhe@sinapsys.global>
* Freddy Arraez <far@sinapsys.global>
* Elvis Paez <epa@sinapsys.global>
* Guillermo Montoya <https://github.com/guillermm>

### Maintainers

This module is maintained by the OCA.

<a href="https://odoo-community.org">
    <img src="https://odoo-community.org/logo.png" alt="Odoo Community Association" width="200" />
</a>

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

This module is part of the [OCA/l10n-venezuela](https://github.com/OCA/l10n-venezuela/tree/17.0/territorial_pd) project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
