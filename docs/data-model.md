# Data Model

This document describes the implemented Import-mode semantic model in
[the Power BI project](../powerbi/ecommerce-analysis.pbip), replacing the earlier
proposal. Evidence comes from the saved [TMDL definition](../powerbi/ecommerce-analysis.SemanticModel/definition/model.tmdl),
[Power Query staging expressions](../powerbi/ecommerce-analysis.SemanticModel/definition/expressions.tmdl),
and [relationships](../powerbi/ecommerce-analysis.SemanticModel/definition/relationships.tmdl).
This is a review of the saved definitions, not a new refresh or verification of
loaded row counts.

## Analytical tables and grains

The analytical core consists of four fact tables and four dimensions. Customer
and purchase date are shared dimensions; product and seller relate to sales.
The saved model also contains the calculated _Measures table as a measure
container, not an additional analytical fact or dimension.

The eight stg_ queries (Customers, OrderItems, Payments, Reviews, Orders,
Products, Sellers, and CategoryTranslation) are named M expressions in
expressions.tmdl, not loaded semantic tables. agg_OrderReviews is also a named
M expression: a non-loaded transformation helper with Enable Load disabled.
It has no table definition, Import partition, or table reference in model.tmdl.
_Measures uses the calculated source `{ BLANK() }` as a container for measures.

| Fact | Grain / logical row identifier | Implemented source and preparation |
| --- | --- | --- |
| [FactSales](../powerbi/ecommerce-analysis.SemanticModel/definition/tables/FactSales.tmdl) | One order item; (order_id, order_item_id) | stg_OrderItems from olist_order_items_dataset.csv, left-merged with stg_Orders on order_id to obtain customer, order status, and order timestamps |
| [FactPayments](../powerbi/ecommerce-analysis.SemanticModel/definition/tables/FactPayments.tmdl) | One payment-sequence record within an order; (order_id, payment_sequential), not one row per installment | stg_Payments from olist_order_payments_dataset.csv, left-merged with stg_Orders for customer_id, order_status, and order_purchase_timestamp |
| [FactReviews](../powerbi/ecommerce-analysis.SemanticModel/definition/tables/FactReviews.tmdl) | One source review/order pair; (review_id, order_id), not one row per order | stg_Reviews from olist_order_reviews_dataset.csv, left-merged with stg_Orders for customer_id, order_status, and order_purchase_timestamp; individual reviews retained |
| [FactOrderExperience](../powerbi/ecommerce-analysis.SemanticModel/definition/tables/FactOrderExperience.tmdl) | One row per order; order_id | stg_Orders from olist_orders_dataset.csv, left-merged with agg_OrderReviews on order_id; includes delivery fields and AvgReviewScore |

The composite identifiers describe grains supported by the raw-data profile;
they are not declared composite primary-key constraints in TMDL. Orders have a
unique, non-null order_id in that profile. All four facts derive OrderDate
from the date portion of order_purchase_timestamp. FactReviews also derives
ReviewCreationDate and ReviewAnswerDate.

The customer_id, product_id, and seller_id dimension columns serve as the
one-side relationship keys; they do not have explicit isKey declarations.
DimDate.Date does have isKey. FactOrderExperience.order_id describes its logical
order grain, not a relationship to a loaded review helper. A static review
does not independently prove uniqueness in refreshed data.

Monetary source fields price, freight_value, and payment_value are parsed as
fixed-decimal Currency.Type with the en-US locale in expressions.tmdl. Their
fact columns use TMDL decimal. Both monetary columns and explicit monetary
measures use Brazilian Real (BRL / R$) formats and pt-BR currency hints.

## Dimensions

| Dimension | Grain / relationship key | Source and implemented attributes |
| --- | --- | --- |
| [DimCustomer](../powerbi/ecommerce-analysis.SemanticModel/definition/tables/DimCustomer.tmdl) | One customer_id | stg_Customers from olist_customers_dataset.csv; customer_unique_id, customer_zip_code_prefix, customer_city, customer_state |
| [DimProduct](../powerbi/ecommerce-analysis.SemanticModel/definition/tables/DimProduct.tmdl) | One product_id | stg_Products from olist_products_dataset.csv, left-merged with stg_CategoryTranslation from product_category_name_translation.csv; source product metadata, product_category_name_english, and product_category |
| [DimSeller](../powerbi/ecommerce-analysis.SemanticModel/definition/tables/DimSeller.tmdl) | One seller_id | stg_Sellers from olist_sellers_dataset.csv; seller_zip_code_prefix, seller_city, seller_state |
| [DimDate](../powerbi/ecommerce-analysis.SemanticModel/definition/tables/DimDate.tmdl) | One calendar day; Date is marked as a key | Generated with List.Dates from the minimum through maximum FactSales.OrderDate, inclusive; Year, Quarter, MonthNumber, MonthName, YearMonth, Day, DayName, DayOfWeek |

DimCustomer relates through customer_id, not customer_unique_id. DimProduct's
product_category chooses a nonblank English translation, otherwise a nonblank
original category, otherwise "Unknown". These are existing query steps, not
changes made during this documentation review.

DimDate has dataCategory Time. MonthName sorts by MonthNumber and DayName by
DayOfWeek (Monday = 1). Its range is based only on FactSales; coverage of dates
in the other facts has not been established by this static review.

## Active analytical relationships

The ten relationships below are active, one-to-many, with cross-filter
direction **Single**, from the dimension (one side) to the fact (many side).
The saved TMDL uses default relationship properties for these entries: none
has an inactive, cardinality, or bothDirections override. The defaults are
active, fromCardinality many, toCardinality one, and oneDirection; fromColumn
is the fact endpoint and toColumn is the dimension endpoint. Single/OneDirection filters the
fromColumn table from the toColumn table, as described in
[Microsoft's relationship reference](https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.singlecolumnrelationship).

| One side | Many side | Active | Cross-filter direction |
| --- | --- | --- | --- |
| DimCustomer.customer_id | FactSales.customer_id | Yes | Single |
| DimCustomer.customer_id | FactPayments.customer_id | Yes | Single |
| DimCustomer.customer_id | FactReviews.customer_id | Yes | Single |
| DimCustomer.customer_id | FactOrderExperience.customer_id | Yes | Single |
| DimProduct.product_id | FactSales.product_id | Yes | Single |
| DimSeller.seller_id | FactSales.seller_id | Yes | Single |
| DimDate.Date | FactSales.OrderDate | Yes | Single |
| DimDate.Date | FactPayments.OrderDate | Yes | Single |
| DimDate.Date | FactReviews.OrderDate | Yes | Single |
| DimDate.Date | FactOrderExperience.OrderDate | Yes | Single |

Customer and DimDate filters apply across all four facts. Product and seller
filters apply to FactSales, not to payments, reviews, or order experience.
DimDate filters use purchase date, including for payments and reviews; they
do not represent payment receipt dates or review event dates.

There are no saved relationships between the four analytical fact tables.
There are also no DimDate relationships to ReviewCreationDate or ReviewAnswerDate;
the earlier proposal's optional review-date links are not implemented.

The table above lists **all ten relationships**, each active, one-to-many, and
Single-direction. There are no inactive, bidirectional, helper, or direct
fact-to-fact relationships. There are no LocalDateTable or date-template tables
in the current definition, and no automatic date relationships. model.tmdl
records `__PBI_TimeIntelligenceEnabled = 0`.

## Order experience and review aggregation

FactOrderExperience provides one row per order so delivery performance and
review scores can be analyzed together without directly relating the four
analytical facts to each other.

[agg_OrderReviews](../powerbi/ecommerce-analysis.SemanticModel/definition/expressions.tmdl)
is a non-loaded Power Query helper. It selects order_id and review_score from
stg_Reviews, groups by order_id, and
computes AvgReviewScore with List.Average([review_score]). Thus duplicate
reviews **per order** (multiple review records sharing an order_id) are
aggregated before the merge; this is not removal of exact duplicate records.
FactReviews retains the individual review rows.

FactOrderExperience selects order_id, customer_id, order_status,
order_purchase_timestamp, order_delivered_customer_date, and
order_estimated_delivery_date from stg_Orders. It left-merges the order-level
aggregate and expands only AvgReviewScore. Because the aggregate has one row
per order_id, this merge preserves the order grain. Orders without a matching
review remain present with a null AvgReviewScore.

The query then creates:

| Field | Implemented calculation |
| --- | --- |
| DeliveryStatus | Null if actual customer delivery is null; otherwise "Late" if actual delivery timestamp exceeds estimated delivery timestamp, else "On-Time" |
| DeliveryDays | Duration.Days(actual customer delivery timestamp - purchase timestamp) |
| DelayDays | Null if actual customer delivery is null; otherwise Duration.Days(actual delivery timestamp - estimated delivery timestamp) |
| OrderDate | Date portion of order_purchase_timestamp |

DeliveryDays and DelayDays are currently declared as string columns in TMDL,
even though the M expressions calculate day durations. This records the saved
metadata; it does not assert that their semantic types have been corrected.
AvgReviewScore is double, DeliveryStatus is string, and the three retained
timestamps and OrderDate are dateTime columns. OrderDate also carries the
date-only annotation. order_id, customer_id, and order_status are strings.

The existing [_Measures table](../powerbi/ecommerce-analysis.SemanticModel/definition/tables/_Measures.tmdl)
defines Experience Orders as COUNTROWS(FactOrderExperience) and Experience Avg
Review as AVERAGE(FactOrderExperience[AvgReviewScore]). The latter averages
order-level scores, so reviewed orders have equal weight rather than each
individual review having equal weight. AvgReviewScore itself is a stored column,
not a DAX measure.

## Verified implemented measures

All 25 measures below are declared in _Measures.tmdl. The expressions and
descriptions reflect the saved implementation, not new measure proposals.

| Measure | Implemented calculation / scope |
| --- | --- |
| Total Sales | SUM(FactSales[price]) |
| Total Freight | SUM(FactSales[freight_value]) |
| Sales + Freight | [Total Sales] + [Total Freight] |
| Total Orders | DISTINCTCOUNT(FactSales[order_id]) |
| Item Sold | COUNTROWS(FactSales) |
| Average Order Value | DIVIDE([Total Sales], [Total Orders]) |
| Average Item Price | AVERAGE(FactSales[price]) |
| Order Customers | DISTINCTCOUNT(FactSales[customer_id]) |
| Unique Customers | DISTINCTCOUNT(DimCustomer[customer_unique_id]) |
| Total Payment Value | SUM(FactPayments[payment_value]) |
| Payment Transactions | COUNTROWS(FactPayments) |
| Average Review Score | AVERAGE(FactReviews[review_score]) |
| Total Reviews | COUNTROWS(FactReviews) |
| Positive Review % | DIVIDE(CALCULATE(COUNTROWS(FactReviews), FactReviews[review_score] >= 4), [Total Reviews]) |
| Freight % of Sales | DIVIDE([Total Freight], [Total Sales]) |
| Average Delivery Days | AVERAGEX over VALUES(FactSales[order_id]); for each order, CALCULATE evaluates DATEDIFF from MIN(order_purchase_timestamp) to MAX(order_delivered_customer_date), in DAY units |
| Late Deliveries | Counts distinct FactSales order_id values whose per-order MAX(order_delivered_customer_date) exceeds MAX(order_estimated_delivery_date), each evaluated with CALCULATE |
| Delivered Orders | Counts distinct FactSales order_id values with a nonblank per-order MAX(order_delivered_customer_date), evaluated with CALCULATE |
| Late Delivery % | DIVIDE([Late Deliveries], [Delivered Orders]) |
| On-Time Delivery % | 1 - [Late Delivery %] |
| Experience Orders | COUNTROWS(FactOrderExperience) |
| Experience Avg Review | AVERAGE(FactOrderExperience[AvgReviewScore]) |
| On-Time Avg Review | CALCULATE([Experience Avg Review], FactOrderExperience[DeliveryStatus] = "On-Time") |
| Late Avg Review | CALCULATE([Experience Avg Review], FactOrderExperience[DeliveryStatus] = "Late") |
| Review Score Gap | [On-Time Avg Review] - [Late Avg Review] |

The delivery KPI measures still use FactSales; they do not use the DeliveryDays
or DelayDays columns in FactOrderExperience. Average Delivery Days has no
explicit filter excluding missing delivery timestamps. On-Time Delivery % is
implemented as a complement, with no explicit blank/zero-denominator guard of
its own. These are implementation details, not assertions of validated results.

Total Orders counts orders represented in FactSales, whereas Experience Orders
counts order-level experience rows. Average Review Score weights individual
reviews; Experience Avg Review averages nonblank order-level scores. Unique
Customers is dimension-based and is not filtered back from FactSales by the
Single-direction relationships. No additional order-status exclusion is present
in the Total Sales or Total Payment Value expressions.

## Why separate fact grains matter

Joining order items, payment records, and review records directly on order_id
would multiply rows whenever an order has multiple records in more than one
table. This can inflate sales, payments, review counts, and the weight given
to particular orders in score averages. The separate facts preserve each
analytical grain; order-level review aggregation supports the delivery/score
comparison without that multiplication.

For context, the saved raw-data profile reports 112,650 item rows across 98,666
orders, 103,886 payment rows across 99,440 orders, and 99,224 review rows across
98,673 orders. Those are source profiling counts, not newly measured counts of
the loaded Power BI tables. The profile reports 100% distinct-key match rates
for the six core source relationships; category translation has 610 null
product category rows and two unmatched distinct category values. See the
[data dictionary](data-dictionary.md) and
[profile report](../data/processed/data-profile.json) for the source evidence.

This documentation does not infer business conclusions from the model, claim
a successful refresh, or change any data, measures, relationships, or Power BI
artifacts.
