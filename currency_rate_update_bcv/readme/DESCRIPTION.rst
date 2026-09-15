Este módulo es un proveedor de tasa de cambio para `Currency Rate Update`_.

Consultará la página web del Banco Central de Venezuela para obtener las tasas de:

Dólar (USD), Euro (EUR), Yuan (CNY), Rublo (RUB), Lira (TRY)

Migrado a 17.0 desde la rama
`16.0 de OCA/l10n-venezuela`_ (Luis Pinzón). El nombre técnico en 16.0
era ``res_currency_rate_provider_BCV``; en 17.0 se llama
``currency_rate_update_bcv``, igual que en 18.0. En esta rama también se
hizo backport a 17.0 del endurecimiento del scrap publicado en
`currency_rate_update_bcv 18.0`_ (timeout ``(10, 60)``, chequeo HTTP 200
y claves de fecha ISO). Depende de ``currency_rate_update``
(OCA/currency 17.0).

.. _Currency Rate Update: https://github.com/OCA/currency/tree/17.0/currency_rate_update
.. _16.0 de OCA/l10n-venezuela: https://github.com/OCA/l10n-venezuela/tree/16.0/res_currency_rate_provider_BCV
.. _currency_rate_update_bcv 18.0: https://github.com/OCA/l10n-venezuela/tree/18.0/currency_rate_update_bcv
