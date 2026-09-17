[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/l10n-venezuela&target_branch=17.0)
[![Pre-commit Status](https://github.com/OCA/l10n-venezuela/actions/workflows/pre-commit.yml/badge.svg?branch=17.0)](https://github.com/OCA/l10n-venezuela/actions/workflows/pre-commit.yml?query=branch%3A17.0)
[![Build Status](https://github.com/OCA/l10n-venezuela/actions/workflows/test.yml/badge.svg?branch=17.0)](https://github.com/OCA/l10n-venezuela/actions/workflows/test.yml?query=branch%3A17.0)
[![codecov](https://codecov.io/gh/OCA/l10n-venezuela/branch/17.0/graph/badge.svg)](https://codecov.io/gh/OCA/l10n-venezuela)

# l10n-venezuela

<!-- /!\ do not modify above this line -->

## Español

Localización contable y fiscal de Venezuela para **Odoo 17**.

Continúa la estructura y la autoría de los módulos históricos de
[odoo-venezuela](https://github.com/odoo-venezuela/odoo-venezuela)
(Vauxoo y contribuidores de las ramas 7.0/8.0). La adaptación a 17.0
la mantiene **Guillermo Montoya**. El módulo nuevo `l10n_ve_igtf` no
forma parte de esa base histórica. La tasa BCV
(`currency_rate_update_bcv`) viene de la rama
[16.0 de OCA](https://github.com/OCA/l10n-venezuela/tree/16.0/res_currency_rate_provider_BCV)
(`res_currency_rate_provider_BCV`),
autoría de **Luis Pinzón** (`lapinzon`); aquí se migró a 17.0, se
renombró como en 18.0 y se hizo backport del scrap de
[18.0 `currency_rate_update_bcv`](https://github.com/OCA/l10n-venezuela/tree/18.0/currency_rate_update_bcv).
Estados, municipios y parroquias (`territorial_pd`) se tomaron de
[Mastercore 16.0](https://github.com/odoo-mastercore/odoo-venezuela/tree/16.0/territorial_pd),
autoría de **SINAPSYS GLOBAL SA** y **MASTERCORE SAS**.

El plan de cuentas no se duplica aquí: se usa el `l10n_ve` oficial, con
**códigos de 7 dígitos** (grupos funcionales de 4 dígitos, alineados con
el criterio acordado para 17.0).

Cada addon tiene su propio README con configuración y uso de esta rama.

### Qué cubre

- Número de control SENIAT, RIF (`V/E/J/P/G/C`), Unidad Tributaria y
validaciones al publicar facturas.
- Retenciones de **IVA**, **ISLR**, **municipal** y **SRC** en el
*Registrar pago* (write-off; la factura baja el residual).
- TXT de IVA (quincena, latin-1) y XML de ISLR (ISO-8859-1) en bolívares
(se exige tasa BCV; no se asume 1:1).
- Libros de compras y ventas (alícuotas 8 %, 16 % y 31 %, importación 05 y ajustes).
- Tasa BCV para libros, TXT y XML en bolívares (nunca 1:1):
  `currency_rate_update_bcv` (incluido) y su dependencia OCA
  `currency_rate_update`.
- IGTF en diarios de banco/divisas, en el registro de pagos y, si se
marca, en la factura de compra (línea de gasto; no duplicar en el pago).
- Catálogo de bancos VE (código SUDEBAN en BIC) y tipo de cuenta.
- Tipo de contribuyente SENIAT (ordinario / formal / especial).
- PDF de factura con RIF, número de control, municipio y parroquia.
- Libro fiscal en PDF y Excel (columnas internas, no la plantilla SENIAT).
- Split de facturas, declaraciones DUA/DVI y ajuste de crédito fiscal.

No incluye facturación digital (esperando normativa del SENIAT).

La **retención municipal** es lo que se descuenta al **pagar a un
proveedor** (según la ordenanza y la actividad económica) y se entera
al municipio. No es el **IMI** (impuesto municipal inmobiliario /
predial) ni la **patente** de industria y comercio (lo que la empresa
declara por *su propia* actividad ante la alcaldía).

**Dualidad monetaria / bimonetario (Bs / USD / EUR).**
Precios en divisa y declaración al SENIAT en bolívares a tasa BCV
(Ley de IVA art. 25; Providencia SNAT/2011/00071). Libros, TXT y XML
van en bolívares (nunca 1:1). **Este repo no implementa** cotizaciones
ni informes contables en dos columnas. La tasa oficial sí: compañía en
VES; `currency_rate_update_bcv` (incluido) y
[`currency_rate_update`](https://github.com/OCA/currency/tree/17.0/currency_rate_update)
(OCA/currency 17.0). **Cotizar o vender en USD/EUR** se hace con las
**tarifas de precios** de Odoo (lista en divisa); el asiento y el SENIAT
quedan en Bs. No hace falta un módulo extra para eso.

### Instalación

Instalar **en este orden** (cada módulo depende del anterior). Idioma del
usuario: **Spanish (`es_ES`)**, no `es_VE`. El usuario necesita las
características de contabilidad completas.

1. Contabilidad oficial + `l10n_ve`. Compañía en Venezuela, moneda VES, RIF
  y al menos una tasa VES. Ventas y Compras solo si se van a usar pedidos.
2. `territorial_pd` — estados, municipios y parroquias (Mastercore).
3. `l10n_ve_fiscal_requirements` — núcleo SENIAT (RIF, control, UT). Al
  instalarlo Odoo instala solo **`l10n_latam_base`** (oficial de Odoo 17;
  tipos RIF / cédula / pasaporte). No hay que descargarla ni marcarla a
  mano: ya viene en los addons de Odoo. En Impuestos se ven **Exento,
  IVA 8%, IVA 16% e IVA 31%** (el predeterminado de venta/compra es 16 %).
  El `l10n_ve` oficial aún trae 12 % y 22 % (no está aprobado el cambio
  en Odoo); al instalar/actualizar se **reemplazan en la misma ficha**
  12 % → 16 % y 22 % → 31 % y se marca `appl_type`. El SDCF (0 % sin
  crédito) se marca a mano.
4. `l10n_ve_withholding` — base de retenciones (sin menú propio).
5. `l10n_ve_withholding_iva`
6. `l10n_ve_withholding_islr`
7. `l10n_ve_withholding_muni` (opcional)
8. `l10n_ve_withholding_src` (opcional)
9. `l10n_ve_igtf` (opcional)
10. `l10n_ve_fiscal_book` — después del IVA
11. `l10n_ve_imex` — después del libro (opcional)
12. `l10n_ve_vat_write_off` (opcional)
13. `l10n_ve_sale_purchase` — después de ISLR + Ventas/Compras (opcional)
14. `l10n_ve_split_invoice` — puede ir tras el paso 2 (opcional)
15. Tasa BCV: instalar `currency_rate_update`
  (OCA/currency 17.0) y luego `currency_rate_update_bcv`. Si no, cargar
  la tasa a mano (compañía en VES, USD/EUR activos).

Tras cada retención: crear el **diario** en la compañía y revisar las
cuentas (el hook intenta rellenarlas). En el contacto: tipo de persona,
agente IVA / concepto ISLR / municipio territorial / SRC según el módulo.

El detalle de vistas, campos y data de cada addon está en su README.

### Dependencias

Este repo **no trae** la contabilidad de Odoo ni el plan `l10n_ve`: hay
que tenerlos instalados. Odoo resuelve el resto en cadena al instalar
cada addon.

**Odoo 17 (oficial / Enterprise), fuera de este repo:**

- `account` — Contabilidad (casi todos los addons)
- `contacts` — Contactos (`territorial_pd`)
- `base_vat` — validación de NIF/VAT
- `l10n_latam_base` — tipos de identificación LATAM (**oficial Odoo 17**,
  no hay que bajarla). La instala solo `l10n_ve_fiscal_requirements`;
  `l10n_ve` oficial **no** la trae.
- `l10n_ve` — plan de cuentas y fiscalidad VE oficial
- `product` — productos (`l10n_ve_withholding_islr`)
- `sale_management` y `purchase` — solo si se usa `l10n_ve_sale_purchase`

**OCA (tasa oficial), fuera de este repo:**

- `currency_rate_update`
  ([OCA/currency 17.0](https://github.com/OCA/currency/tree/17.0/currency_rate_update))
  — base de proveedores de tipo de cambio. La necesita
  `currency_rate_update_bcv` (ese sí está en este repo).

**Por módulo (este repo + externos):**

| Módulo | Depende de |
| ------ | ---------- |
| `territorial_pd` | `base`, `contacts` |
| `l10n_ve_fiscal_requirements` | `account`, `base_vat`, `l10n_latam_base`, `l10n_ve`, `territorial_pd` |
| `l10n_ve_withholding` | `account`, `l10n_ve_fiscal_requirements` |
| `l10n_ve_withholding_iva` | `account`, `l10n_ve_fiscal_requirements`, `l10n_ve_withholding` |
| `l10n_ve_withholding_islr` | `account`, `product`, `l10n_ve_fiscal_requirements`, `l10n_ve_withholding` |
| `l10n_ve_withholding_muni` | `account`, `l10n_ve_fiscal_requirements`, `l10n_ve_withholding`, `territorial_pd` |
| `l10n_ve_withholding_src` | `account`, `l10n_ve_fiscal_requirements`, `l10n_ve_withholding` |
| `l10n_ve_igtf` | `account`, `l10n_ve_fiscal_requirements`, `l10n_ve_withholding` |
| `l10n_ve_fiscal_book` | `account`, `l10n_ve_fiscal_requirements`, `l10n_ve_withholding_iva` |
| `l10n_ve_imex` | `account`, `l10n_ve_fiscal_requirements`, `l10n_ve_fiscal_book`, `l10n_ve_withholding_iva` |
| `l10n_ve_vat_write_off` | `account`, `l10n_ve_fiscal_book` |
| `l10n_ve_sale_purchase` | `sale_management`, `purchase`, `l10n_ve_withholding_islr` |
| `l10n_ve_split_invoice` | `account`, `l10n_ve_fiscal_requirements` |
| `currency_rate_update_bcv` | `currency_rate_update` (OCA/currency) |

## English

Accounting and fiscal localization of Venezuela for **Odoo 17**.

It keeps the structure and authorship of the historical modules from
[odoo-venezuela](https://github.com/odoo-venezuela/odoo-venezuela)
(Vauxoo and contributors of the 7.0/8.0 branches). The 17.0 port is
maintained by **Guillermo Montoya**. The new `l10n_ve_igtf` module is
not part of that historical tree. BCV rates
(`currency_rate_update_bcv`) come from the
[OCA 16.0 branch](https://github.com/OCA/l10n-venezuela/tree/16.0/res_currency_rate_provider_BCV)
(`res_currency_rate_provider_BCV`),
authored by **Luis Pinzón** (`lapinzon`); this repo migrated them to
17.0, renamed the addon as in 18.0, and backported the scrap hardening from
[OCA 18.0 `currency_rate_update_bcv`](https://github.com/OCA/l10n-venezuela/tree/18.0/currency_rate_update_bcv).
States, municipalities and parishes (`territorial_pd`) were
taken from
[Mastercore 16.0](https://github.com/odoo-mastercore/odoo-venezuela/tree/16.0/territorial_pd),
authored by **SINAPSYS GLOBAL SA** and **MASTERCORE SAS**.

This repo does not ship a custom chart of accounts: it uses official
`l10n_ve` with **7-digit codes** (4-digit functional groups, as agreed
for 17.0).

Each addon has its own README with configuration and usage for this
branch.

### What it covers

- SENIAT control number, RIF (`V/E/J/P/G/C`), Tax Unit and invoice
posting checks.
- **VAT**, **ISLR**, **municipal** and **SRC** withholdings on
*Register Payment* (write-off; the invoice residual decreases).
- VAT TXT (fortnight, latin-1) and ISLR XML (ISO-8859-1) in bolivars
(a BCV rate is required; never assume 1:1).
- Purchase and sale books (8 %, 16 % and 31 % rates, import type 05
and adjustments).
- BCV rate so books, TXT and XML stay in bolivars (never 1:1):
  `currency_rate_update_bcv` (included) and its OCA dependency
  `currency_rate_update`.
- IGTF on foreign-currency / crypto journals, on payment register and,
if marked, on vendor bills (expense line; do not apply it twice).
- Venezuelan bank catalog (SUDEBAN code in BIC) and account type.
- SENIAT taxpayer type (ordinary / formal / special).
- Invoice PDF with RIF, control number, municipality and parish.
- Fiscal book PDF and Excel (internal columns, not the official SENIAT
template).
- Invoice split, DUA/DVI declarations and VAT credit write-off.

It does not include digital invoicing (awaiting SENIAT regulations).

**Municipal withholding** is the amount withheld when **paying a
vendor** (rate from the municipal ordinance and economic activity) and
remitted to the municipality. It is not **IMI** (municipal real-estate /
property tax) nor the **patente** (industry-and-commerce tax the company
self-assesses on *its own* activity).

**Dual currency / bimonetary (VES / USD / EUR).**
Prices in foreign currency and SENIAT filing in bolivars at the BCV
rate (VAT Law art. 25; Providencia SNAT/2011/00071). Books, TXT and XML
stay in bolivars (never 1:1). **This repo does not implement** dual
quotations or two-column accounting reports. The official rate is
covered: company in VES; `currency_rate_update_bcv` (included) and
[`currency_rate_update`](https://github.com/OCA/currency/tree/17.0/currency_rate_update)
(OCA/currency 17.0). **Quoting or selling in USD/EUR** is done with Odoo
**pricelists** (list in foreign currency); the journal entry and SENIAT
stay in VES. No extra module is required for that.

### Installation

Install **in this order** (each module depends on the previous one). User
language: **Spanish (`es_ES`)**, not `es_VE`. The user needs full
accounting features.

1. Official Accounting + `l10n_ve`. Company in Venezuela, VES currency,
  RIF and at least one VES rate. Sales and Purchase only if you use
   orders.
2. `territorial_pd` — states, municipalities and parishes (Mastercore).
3. `l10n_ve_fiscal_requirements` — SENIAT core (RIF, control, UT). Odoo
  then installs **`l10n_latam_base`** by itself (official Odoo 17 LATAM
  identification types). Do not download or tick it by hand; it already
  ships in the Odoo addons. In Accounting the taxes are named **Exempt,
  IVA 8%, IVA 16% and IVA 31%** (sale/purchase default is 16 %). Official
  `l10n_ve` still ships 12 % and 22 % (the Odoo change is not approved
  yet); on install/update those records are **replaced in place** 12 % →
  16 % and 22 % → 31 %, and `appl_type` is set. Mark SDCF (0 % with no
  tax credit) by hand.
4. `l10n_ve_withholding` — withholding base (no menu of its own).
5. `l10n_ve_withholding_iva`
6. `l10n_ve_withholding_islr`
7. `l10n_ve_withholding_muni` (optional)
8. `l10n_ve_withholding_src` (optional)
9. `l10n_ve_igtf` (optional)
10. `l10n_ve_fiscal_book` — after VAT withholding
11. `l10n_ve_imex` — after the fiscal book (optional)
12. `l10n_ve_vat_write_off` (optional)
13. `l10n_ve_sale_purchase` — after ISLR + Sales/Purchase (optional)
14. `l10n_ve_split_invoice` — can be installed after step 2 (optional)
15. BCV rate: install `currency_rate_update`
  (OCA/currency 17.0) and then `currency_rate_update_bcv`. Otherwise set
  the rate by hand (company in VES, USD/EUR enabled).

After each withholding module: create the **journal** on the company and
review the accounts (the hook tries to fill them). On the partner: person
type, VAT agent / ISLR concept / territorial municipality / SRC as needed.

See each addon's README for views, fields and data.

### Dependencies

This repo **does not ship** Odoo Accounting nor the official `l10n_ve`
chart: install those first. Odoo then pulls the rest of the chain.

**Odoo 17 (official / Enterprise), not in this repo:**

- `account` — Accounting (almost every addon)
- `contacts` — Contacts (`territorial_pd`)
- `base_vat` — Tax ID / VAT validation
- `l10n_latam_base` — LATAM identification types (**official Odoo 17**,
  do not download it). Pulled automatically by
  `l10n_ve_fiscal_requirements`; official `l10n_ve` does **not** depend
  on it.
- `l10n_ve` — official VE chart and fiscal pack
- `product` — Products (`l10n_ve_withholding_islr`)
- `sale_management` and `purchase` — only if you use `l10n_ve_sale_purchase`

**OCA (official rate), not in this repo:**

- `currency_rate_update`
  ([OCA/currency 17.0](https://github.com/OCA/currency/tree/17.0/currency_rate_update))
  — rate-provider base. Required by `currency_rate_update_bcv` (that
  addon **is** in this repo).

**Per addon (this repo + external):**

| Addon | Depends on |
| ----- | ---------- |
| `territorial_pd` | `base`, `contacts` |
| `l10n_ve_fiscal_requirements` | `account`, `base_vat`, `l10n_latam_base`, `l10n_ve`, `territorial_pd` |
| `l10n_ve_withholding` | `account`, `l10n_ve_fiscal_requirements` |
| `l10n_ve_withholding_iva` | `account`, `l10n_ve_fiscal_requirements`, `l10n_ve_withholding` |
| `l10n_ve_withholding_islr` | `account`, `product`, `l10n_ve_fiscal_requirements`, `l10n_ve_withholding` |
| `l10n_ve_withholding_muni` | `account`, `l10n_ve_fiscal_requirements`, `l10n_ve_withholding`, `territorial_pd` |
| `l10n_ve_withholding_src` | `account`, `l10n_ve_fiscal_requirements`, `l10n_ve_withholding` |
| `l10n_ve_igtf` | `account`, `l10n_ve_fiscal_requirements`, `l10n_ve_withholding` |
| `l10n_ve_fiscal_book` | `account`, `l10n_ve_fiscal_requirements`, `l10n_ve_withholding_iva` |
| `l10n_ve_imex` | `account`, `l10n_ve_fiscal_requirements`, `l10n_ve_fiscal_book`, `l10n_ve_withholding_iva` |
| `l10n_ve_vat_write_off` | `account`, `l10n_ve_fiscal_book` |
| `l10n_ve_sale_purchase` | `sale_management`, `purchase`, `l10n_ve_withholding_islr` |
| `l10n_ve_split_invoice` | `account`, `l10n_ve_fiscal_requirements` |
| `currency_rate_update_bcv` | `currency_rate_update` (OCA/currency) |

## Módulos / Modules


| Módulo / Module                                                     | Español                                                                                                                 | English                                                                                                             |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [territorial_pd](territorial_pd/)                                 | Estados, municipios y parroquias de Venezuela. Municipio y parroquia en la dirección del contacto. Catálogo Mastercore. | Venezuelan states, municipalities and parishes. Municipality and parish on the partner address. Mastercore catalog. |
| [l10n_ve_fiscal_requirements](l10n_ve_fiscal_requirements/)       | Núcleo SENIAT: RIF/cédula/pasaporte, número de control, UT, consulta SENIAT, bancos SUDEBAN y tipo de contribuyente.    | SENIAT core: RIF/ID/passport, control number, tax unit, SENIAT lookup, SUDEBAN banks and taxpayer type.             |
| [l10n_ve_withholding](l10n_ve_withholding/)                       | Base compartida de retenciones. Aplica el write-off al registrar el pago.                                               | Shared withholding engine. Applies the write-off when registering a payment.                                        |
| [l10n_ve_withholding_iva](l10n_ve_withholding_iva/)               | Retención de IVA (75 % o 100 %). Comprobante y TXT 99035.                                                               | VAT withholding (75 % or 100 %). Voucher and TXT 99035.                                                             |
| [l10n_ve_withholding_islr](l10n_ve_withholding_islr/)             | Retención de ISLR por concepto SENIAT y tipo de persona. Comprobante y XML.                                             | Income-tax withholding by SENIAT concept and person type. Voucher and XML.                                          |
| [l10n_ve_withholding_muni](l10n_ve_withholding_muni/)             | Retención al pagar proveedores (ordenanza y actividad). No es IMI (predial) ni la patente de la empresa.                | Withholding on vendor payments (ordinance/activity). Not IMI (property tax) nor the company's own patente.          |
| [l10n_ve_withholding_src](l10n_ve_withholding_src/)               | Retención SRC (compromiso de responsabilidad social) en contrataciones públicas.                                        | SRC withholding (social responsibility) for public contracts.                                                       |
| [l10n_ve_igtf](l10n_ve_igtf/)                                     | IGTF en pagos con diarios de divisas/cripto y, opcional, en facturas de compra.                                         | IGTF on foreign-currency/crypto payments and, optionally, on vendor bills.                                          |
| [l10n_ve_fiscal_book](l10n_ve_fiscal_book/)                       | Libros de compras y ventas (PDF y Excel).                                                                               | Purchase and sale fiscal books (PDF and Excel).                                                                     |
| [l10n_ve_imex](l10n_ve_imex/)                                     | Declaraciones aduaneras DUA/DVI (Forma 86) para importación y exportación.                                              | DUA/DVI customs declarations (Form 86) for import and export.                                                       |
| [l10n_ve_vat_write_off](l10n_ve_vat_write_off/)                   | Ajuste manual de crédito fiscal IVA (línea tipo 04 del libro).                                                          | Manual VAT credit write-off (type-04 book line).                                                                    |
| [l10n_ve_sale_purchase](l10n_ve_sale_purchase/)                   | Copia el concepto ISLR del producto a pedidos y facturas.                                                               | Copies the product ISLR concept to orders and invoices.                                                             |
| [l10n_ve_split_invoice](l10n_ve_split_invoice/)                   | Parte facturas de cliente que superan el límite de líneas.                                                              | Splits customer invoices that exceed the line limit.                                                                |
| [currency_rate_update_bcv](currency_rate_update_bcv/)             | Tasas del BCV (USD, EUR, CNY, RUB, TRY) para Currency Rate Update.                                                      | BCV rates (USD, EUR, CNY, RUB, TRY) for Currency Rate Update.                                                       |






## Available addons


| addon                                                             | version     | maintainers                                                                                                                                                                                                                                                                                                                                 | summary                                                                           |
| ----------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| [territorial_pd](territorial_pd/)                                 | 17.0.1.2.0  | <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a> <a href="https://github.com/odoo-mastercore"><img src="https://github.com/odoo-mastercore.png?size=40" width="40" height="40" alt="odoo-mastercore"/></a>                                           | Venezuelan Municipalities and Parishes (Mastercore)                               |
| [l10n_ve_fiscal_book](l10n_ve_fiscal_book/)                       | 17.0.1.3.1  | <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a>                                                                                                                                                                                                       | Fiscal Report For Venezuela (Libros Fiscales)                                     |
| [l10n_ve_fiscal_requirements](l10n_ve_fiscal_requirements/)       | 17.0.1.17.0 | <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a>                                                                                                                                                                                                       | Venezuelan Fiscal Requirements                                                    |
| [l10n_ve_igtf](l10n_ve_igtf/)                                     | 17.0.1.2.0  | <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a>                                                                                                                                                                                                       | IGTF on vendor bills and payments in foreign currency / crypto journals (Odoo 17) |
| [l10n_ve_imex](l10n_ve_imex/)                                     | 17.0.1.1.0  | <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a>                                                                                                                                                                                                       | Imex (Import and Export Customs Declaration)                                      |
| [l10n_ve_sale_purchase](l10n_ve_sale_purchase/)                   | 17.0.1.1.0  | <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a>                                                                                                                                                                                                       | ISLR Sale and Purchase Functionalities                                            |
| [l10n_ve_split_invoice](l10n_ve_split_invoice/)                   | 17.0.1.1.0  | <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a>                                                                                                                                                                                                       | Split Invoices for Venezuela                                                      |
| [l10n_ve_vat_write_off](l10n_ve_vat_write_off/)                   | 17.0.1.1.0  | <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a>                                                                                                                                                                                                       | VAT Write Off (Ajustes de Crédito Fiscal)                                         |
| [l10n_ve_withholding](l10n_ve_withholding/)                       | 17.0.1.0.0  | <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a>                                                                                                                                                                                                       | Venezuelan Withholding Base                                                       |
| [l10n_ve_withholding_islr](l10n_ve_withholding_islr/)             | 17.0.1.4.0  | <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a>                                                                                                                                                                                                       | Management Withholding ISLR Venezuelan Laws                                       |
| [l10n_ve_withholding_iva](l10n_ve_withholding_iva/)               | 17.0.1.2.0  | <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a>                                                                                                                                                                                                       | Management Withholding VAT Venezuelan Laws                                        |
| [l10n_ve_withholding_muni](l10n_ve_withholding_muni/)             | 17.0.1.8.0  | <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a>                                                                                                                                                                                                       | Local Withholding Venezuelan Laws (Municipal Withholdings)                        |
| [l10n_ve_withholding_src](l10n_ve_withholding_src/)               | 17.0.1.2.0  | <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a>                                                                                                                                                                                                       | Compromiso de Responsabilidad Social (SRC)                                        |
| [currency_rate_update_bcv](currency_rate_update_bcv/)             | 17.0.1.1.3  | <a href="https://github.com/lapinzon"><img src="https://github.com/lapinzon.png?size=40" width="40" height="40" alt="lapinzon"/></a> <a href="https://github.com/andyengit"><img src="https://github.com/andyengit.png?size=40" width="40" height="40" alt="andyengit"/></a> <a href="https://github.com/guillermm"><img src="https://github.com/guillermm.png?size=40" width="40" height="40" alt="guillermm"/></a> | OCA version for BCV scrapping rates                                               |




## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

---

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.