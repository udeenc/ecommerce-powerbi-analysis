# Data Dictionary

This document describes all nine CSV datasets in data/raw/, using the actual
results in [data-profile.json](../data/processed/data-profile.json) produced by
[profile_data.py](../scripts/data-cleaning/profile_data.py). The report contains
no profiling errors. The generated JSON is ignored by Git; see the
[README](../README.md#data-profiling) to reproduce it.

## Interpretation

- Counts, inferred types, null counts, percentages, and key candidates are copied
  from the full-data profile, not from a sample.
- **Nullable (observed)** is **Yes** when at least one null was found, otherwise
  **No**. This is an observation, not a schema constraint or a guarantee about
  future records.
- Null means an empty or whitespace-only field. Literal NA, NULL, and NaN remain
  strings. Null percentages use all rows as the denominator and are displayed
  to four decimal places.
- Types describe inference from non-null values, not enforced database or
  Power BI types. Leading-zero postal codes remain strings. Timestamp time
  zones are not established by the profile.
- Candidate keys are observed unique, non-null single columns or minimal pairs.
  Each parenthesized pair is one composite candidate; alternatives are separated
  by semicolons. Larger combinations were not searched. No primary key is
  formally declared or selected here; business validation is still required.
- Duplicate counts count exact parsed rows beyond their first occurrence.
- Descriptions are conservative interpretations of source column names.
  The profile establishes structure and completeness, not business definitions,
  monetary currency, or measurement rules. Uncertain meanings are noted rather
  than assumed. No cleaning, renaming, or model changes were performed.

## olist_customers_dataset.csv

Rows: **99,441**. Columns: **5**. Duplicate rows: **0**.

Candidate primary keys (observed): (`customer_id`).

| Column | Inferred type | Nullable (observed) | Null count | Null percentage | Description |
| --- | --- | --- | ---: | ---: | --- |
| `customer_id` | string | No | 0 | 0.0000% | Customer identifier recorded in the dataset. |
| `customer_unique_id` | string | No | 0 | 0.0000% | Additional customer identifier; cross-order identity semantics are not established by the profile. |
| `customer_zip_code_prefix` | string | No | 0 | 0.0000% | Customer postal-code prefix. |
| `customer_city` | string | No | 0 | 0.0000% | Customer city label. |
| `customer_state` | string | No | 0 | 0.0000% | Customer state code. |

## olist_geolocation_dataset.csv

Rows: **1,000,163**. Columns: **5**. Duplicate rows: **261,831**.

Candidate primary keys (observed): None found among single columns and pairs.

| Column | Inferred type | Nullable (observed) | Null count | Null percentage | Description |
| --- | --- | --- | ---: | ---: | --- |
| `geolocation_zip_code_prefix` | string | No | 0 | 0.0000% | Postal-code prefix associated with the location. |
| `geolocation_lat` | decimal | No | 0 | 0.0000% | Latitude value; coordinate reference system is not established by the profile. |
| `geolocation_lng` | decimal | No | 0 | 0.0000% | Longitude value; coordinate reference system is not established by the profile. |
| `geolocation_city` | string | No | 0 | 0.0000% | City label associated with the location. |
| `geolocation_state` | string | No | 0 | 0.0000% | State code associated with the location. |

## olist_order_items_dataset.csv

Rows: **112,650**. Columns: **7**. Duplicate rows: **0**.

Candidate primary keys (observed): (`order_id`, `order_item_id`).

| Column | Inferred type | Nullable (observed) | Null count | Null percentage | Description |
| --- | --- | --- | ---: | ---: | --- |
| `order_id` | string | No | 0 | 0.0000% | Order identifier recorded in the dataset. |
| `order_item_id` | integer | No | 0 | 0.0000% | Item identifier within an order; unique together with order_id in this data. |
| `product_id` | string | No | 0 | 0.0000% | Product identifier recorded in the dataset. |
| `seller_id` | string | No | 0 | 0.0000% | Seller identifier recorded in the dataset. |
| `shipping_limit_date` | datetime | No | 0 | 0.0000% | Recorded shipping-limit timestamp; precise deadline rule is not established by the profile. |
| `price` | decimal | No | 0 | 0.0000% | Recorded item price; currency and inclusion of taxes or discounts are not established by the profile. |
| `freight_value` | decimal | No | 0 | 0.0000% | Recorded freight amount for the item row; currency and allocation rules are not established by the profile. |

## olist_order_payments_dataset.csv

Rows: **103,886**. Columns: **5**. Duplicate rows: **0**.

Candidate primary keys (observed): (`order_id`, `payment_sequential`).

| Column | Inferred type | Nullable (observed) | Null count | Null percentage | Description |
| --- | --- | --- | ---: | ---: | --- |
| `order_id` | string | No | 0 | 0.0000% | Order identifier recorded in the dataset. |
| `payment_sequential` | integer | No | 0 | 0.0000% | Payment sequence value within an order; unique together with order_id in this data. |
| `payment_type` | string | No | 0 | 0.0000% | Recorded payment-method label. |
| `payment_installments` | integer | No | 0 | 0.0000% | Recorded installment count; treatment of special values is not established by the profile. |
| `payment_value` | decimal | No | 0 | 0.0000% | Recorded payment amount; currency is not established by the profile. |

## olist_order_reviews_dataset.csv

Rows: **99,224**. Columns: **7**. Duplicate rows: **0**.

Candidate primary keys (observed): (`review_id`, `order_id`); (`order_id`, `review_answer_timestamp`).

| Column | Inferred type | Nullable (observed) | Null count | Null percentage | Description |
| --- | --- | --- | ---: | ---: | --- |
| `review_id` | string | No | 0 | 0.0000% | Review identifier; not unique by itself in this data. |
| `order_id` | string | No | 0 | 0.0000% | Order identifier recorded in the dataset. |
| `review_score` | integer | No | 0 | 0.0000% | Recorded numeric review score; rating-scale meaning is not established by the profile. |
| `review_comment_title` | string | Yes | 87,658 | 88.3435% | Review comment title text. |
| `review_comment_message` | string | Yes | 58,274 | 58.7297% | Review comment body text. |
| `review_creation_date` | datetime | No | 0 | 0.0000% | Recorded review-creation timestamp; exact triggering event is not established by the profile. |
| `review_answer_timestamp` | datetime | No | 0 | 0.0000% | Recorded review-answer timestamp; exact triggering event is not established by the profile. |

## olist_orders_dataset.csv

Rows: **99,441**. Columns: **8**. Duplicate rows: **0**.

Candidate primary keys (observed): (`order_id`); (`customer_id`).

| Column | Inferred type | Nullable (observed) | Null count | Null percentage | Description |
| --- | --- | --- | ---: | ---: | --- |
| `order_id` | string | No | 0 | 0.0000% | Order identifier recorded in the dataset. |
| `customer_id` | string | No | 0 | 0.0000% | Customer identifier recorded in the dataset. |
| `order_status` | string | No | 0 | 0.0000% | Recorded order-status label. |
| `order_purchase_timestamp` | datetime | No | 0 | 0.0000% | Recorded order-purchase timestamp. |
| `order_approved_at` | datetime | Yes | 160 | 0.1609% | Recorded order-approval timestamp. |
| `order_delivered_carrier_date` | datetime | Yes | 1,783 | 1.7930% | Recorded carrier-delivery timestamp; precise handoff event is not established by the profile. |
| `order_delivered_customer_date` | datetime | Yes | 2,965 | 2.9817% | Recorded customer-delivery timestamp. |
| `order_estimated_delivery_date` | datetime | No | 0 | 0.0000% | Recorded estimated customer-delivery date/time. |

## olist_products_dataset.csv

Rows: **32,951**. Columns: **9**. Duplicate rows: **0**.

Candidate primary keys (observed): (`product_id`).

| Column | Inferred type | Nullable (observed) | Null count | Null percentage | Description |
| --- | --- | --- | ---: | ---: | --- |
| `product_id` | string | No | 0 | 0.0000% | Product identifier recorded in the dataset. |
| `product_category_name` | string | Yes | 610 | 1.8512% | Product category label as stored in the source. |
| `product_name_lenght` | integer | Yes | 610 | 1.8512% | Recorded product-name length; counting unit is not established by the profile. Source spelling retained. |
| `product_description_lenght` | integer | Yes | 610 | 1.8512% | Recorded product-description length; counting unit is not established by the profile. Source spelling retained. |
| `product_photos_qty` | integer | Yes | 610 | 1.8512% | Recorded product photo count. |
| `product_weight_g` | integer | Yes | 2 | 0.0061% | Recorded product weight in grams, as indicated by the column name. |
| `product_length_cm` | integer | Yes | 2 | 0.0061% | Recorded product length in centimeters, as indicated by the column name. |
| `product_height_cm` | integer | Yes | 2 | 0.0061% | Recorded product height in centimeters, as indicated by the column name. |
| `product_width_cm` | integer | Yes | 2 | 0.0061% | Recorded product width in centimeters, as indicated by the column name. |

## olist_sellers_dataset.csv

Rows: **3,095**. Columns: **4**. Duplicate rows: **0**.

Candidate primary keys (observed): (`seller_id`).

| Column | Inferred type | Nullable (observed) | Null count | Null percentage | Description |
| --- | --- | --- | ---: | ---: | --- |
| `seller_id` | string | No | 0 | 0.0000% | Seller identifier recorded in the dataset. |
| `seller_zip_code_prefix` | string | No | 0 | 0.0000% | Seller postal-code prefix. |
| `seller_city` | string | No | 0 | 0.0000% | Seller city label. |
| `seller_state` | string | No | 0 | 0.0000% | Seller state code. |

## product_category_name_translation.csv

Rows: **71**. Columns: **2**. Duplicate rows: **0**.

Candidate primary keys (observed): (`product_category_name`); (`product_category_name_english`).

| Column | Inferred type | Nullable (observed) | Null count | Null percentage | Description |
| --- | --- | --- | ---: | ---: | --- |
| `product_category_name` | string | No | 0 | 0.0000% | Product category label as stored in the source. |
| `product_category_name_english` | string | No | 0 | 0.0000% | English category label supplied by the translation dataset. |
