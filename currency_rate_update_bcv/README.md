[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# Currency Rate Provider BCV

[![License: AGPL-3](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0-standalone.html)
[![OCA/l10n-venezuela](https://img.shields.io/badge/github-OCA%2Fl10n--venezuela-lightgrey.png?logo=github)](https://github.com/OCA/l10n-venezuela)

Currency rate provider for [Currency Rate Update](https://github.com/OCA/currency/tree/17.0/currency_rate_update). Scrapes the Banco Central de Venezuela site for USD, EUR, CNY, RUB and TRY. Migrated to 17.0 from the [OCA 16.0 module](https://github.com/OCA/l10n-venezuela/tree/16.0/res_currency_rate_provider_BCV). Scrap hardening (timeout, HTTP 200, ISO date keys) is a backport to 17.0 from [OCA 18.0 `currency_rate_update_bcv`](https://github.com/OCA/l10n-venezuela/tree/18.0/currency_rate_update_bcv).

**Table of contents**

- [Configuration](#configuration)
- [Usage](#usage)
- [Bug Tracker](#bug-tracker)
- [Credits](#credits)
  - [Authors](#authors)
  - [Contributors](#contributors)
  - [Maintainers](#maintainers)

## Configuration

1. Install `currency_rate_update` from OCA/currency (17.0).
2. Install this module.
3. *Accounting -> Configuration -> Currency Rates Providers*: create a *BCV scrapping* provider and select USD (plus EUR/CNY/TRY/RUB if needed).
4. Enable *Automatic Currency Rates (OCA)* in Settings, or update manually.

The company currency should be VES: BCV publishes bolívares per foreign unit.

## Usage

*Accounting -> Configuration -> Currency Rates Providers -> Update Rates*.
BCV only publishes today's rate (this provider has no history).

## Bug Tracker

Bugs are tracked on [GitHub Issues](https://github.com/OCA/l10n-venezuela/issues). In case of trouble, please check there if your issue has already been reported. If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Do not contact contributors directly about support or help with technical issues.

## Credits

### Authors

* Luis Pinzón
* Anderson Armeya
* andyengit

### Contributors

* Luis Pinzón <elpinzon@gmail.com>
* Anderson Armeya
* andyengit
* Guillermo Montoya <https://github.com/guillermm> — 16.0 → 17.0 migration and 18.0 → 17.0 backport

### Maintainers

This module is maintained by the OCA.

<a href="https://odoo-community.org">
    <img src="https://odoo-community.org/logo.png" alt="Odoo Community Association" width="200" />
</a>

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

Current maintainers:

<a href='https://github.com/lapinzon'><img src='https://github.com/lapinzon.png' width='32' height='32' style='border-radius:50%;' alt='lapinzon'/></a>
<a href='https://github.com/andyengit'><img src='https://github.com/andyengit.png' width='32' height='32' style='border-radius:50%;' alt='andyengit'/></a>
<a href='https://github.com/guillermm'><img src='https://github.com/guillermm.png' width='32' height='32' style='border-radius:50%;' alt='guillermm'/></a>

This module is part of the [OCA/l10n-venezuela](https://github.com/OCA/l10n-venezuela/tree/17.0/currency_rate_update_bcv) project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
