# Business Insights

This document records the implemented Power BI analysis. Numerical results below
are verified from the repository's [Executive Overview](images/executive-overview.png),
[Sales Analysis](images/sales-analysis.png), and
[Customer Experience](images/customer-experience.png) screenshots, at their displayed
precision. They were not recalculated during this documentation review. TMDL
verifies the definitions and formatting, not evaluated measure results. The
visible Executive Overview and Customer Experience slicers show All; no exact
unrounded monetary total is inferred from the rounded cards.

Sources: [Power BI project](../powerbi/ecommerce-analysis.pbip),
[implemented measures](../powerbi/ecommerce-analysis.SemanticModel/definition/tables/_Measures.tmdl),
[relationships](../powerbi/ecommerce-analysis.SemanticModel/definition/relationships.tmdl),
and [report pages](../powerbi/ecommerce-analysis.Report/definition/pages/pages.json).
See [the data model](data-model.md) for table grains and implementation details.

## Report structure

The three analysis pages are:

| Page | Implemented analysis |
| --- | --- |
| Executive Overview | Sales, orders, customers, average order value, average review score, monthly sales, category/state sales, and review-score distribution |
| Sales Analysis | Sales, orders, items, average item price, monthly sales and freight ratio, category comparison, and seller sales |
| Customer Experience | Review-score distribution and monthly averages, delivery time and rates, state-level delivery comparisons, and average order-level review score by delivery status |

The saved project also contains a separate **Validation** page. It is additional
to the three analysis pages, not a fourth business-insight section.

## Sales Performance

**Observed results**

| Dashboard result | Verified value | Implemented definition |
| --- | ---: | --- |
| Total Sales | Approximately R$13.59M | Total Sales sums FactSales.price |
| Average Order Value | R$137.75 | Total Sales divided by Total Orders |
| Total Orders | Approximately 98.7K | Distinct FactSales.order_id values |
| Items Sold | Approximately 112.7K | Item Sold counts FactSales rows |
| Unique Customers | Approximately 96.1K | Distinct DimCustomer.customer_unique_id values |

Total Sales excludes freight; the model has separate Total Freight and
Sales + Freight measures. The staging queries now parse price, freight_value,
and payment_value directly as fixed-decimal Currency.Type using the en-US locale;
their fact columns are TMDL decimal. Monetary columns and measures use Brazilian Real
(BRL / R$) formats with pt-BR currency hints. Locale parsing is not a currency
conversion. The previous whole-number staging issue is no longer present.
The rounded sales total above is read from the current screenshots, not obtained
by relabeling the obsolete total or inferring additional precision.

Total Orders covers orders represented in FactSales. Unique Customers is
dimension-based; Single-direction filtering does not propagate sales fact
filters back to DimCustomer, so it should not be treated as a date-filtered
count of purchasing customers without checking filter context.

**Interpretation and business implication:** Item rows exceed distinct orders,
consistent with some orders containing multiple items. Use order counts and
item counts as separate workload indicators. The monthly sales visual supports
period comparison, but no verified growth rate, seasonality, profit, or
repeat-purchase rate is established by the supplied figures.

## Product & Seller Performance

**Observed implementation:** Sales Analysis compares Total Sales by
DimProduct.product_category and DimSeller.seller_id. Its category matrix also
contains Total Orders, Item Sold, Average Item Price, and Freight % of Sales.
The latter is Total Freight divided by Total Sales, not a profit-margin measure.

No category/seller rankings, contributions, or values were supplied as verified
results. Chart definitions alone do not establish which category or seller
leads, whether sales are concentrated, or whether a seller is profitable.

**Interpretation and business implication:** Use the implemented category and
seller comparisons to identify segments for closer review after inspecting the
actual values under consistent filters. Compare sales alongside item volume,
average item price, and freight ratio before deciding priorities. Product and
seller dimensions filter FactSales, not FactReviews or FactOrderExperience;
the current model does not support attributing their review scores directly
to individual products or sellers through those filters.

## Customer Experience

**Observed result:** Average Review Score is **4.09**. The implemented measure
averages individual FactReviews.review_score values. The report includes a
review-score distribution and a monthly review-average visual.

**Interpretation:** The average summarizes recorded reviews, not every customer's
experience. It does not establish how unreviewed orders would have been rated.
The delivery-status comparison below uses order-level averages, so its weighting
differs from this overall review-row average.

**Monthly interpretation:** Partial months and low-volume periods can distort
monthly review averages or make them volatile. Check review counts and period
completeness before interpreting a monthly change as a sustained improvement or
deterioration; no specific month is identified as anomalous here. DimDate filters
the facts through OrderDate, so the monthly review comparison represents
purchase-date cohorts, not the month in which reviews were submitted.

**Business implication:** Review the score distribution and supporting review
volume alongside the average before prioritizing experience improvements.
Compare periods with consistent filters and comparable coverage.

## Delivery Performance

**Observed results**

| Dashboard result | Verified value | Implemented measure / scope |
| --- | ---: | --- |
| Average Delivery Time | 12.50 days | Average Delivery Days evaluates purchase-to-customer-delivery DATEDIFF per distinct FactSales order and averages the results |
| Late Delivery Rate | 8.11% | Late Delivery % divides Late Deliveries by Delivered Orders, using FactSales |
| On-Time Delivery Rate | 91.89% | On-Time Delivery % is 1 - Late Delivery % |
| Average Review Score for On-Time deliveries | Exact value not labeled in the screenshot | Experience Avg Review filtered to FactOrderExperience.DeliveryStatus = "On-Time"; also defined by On-Time Avg Review |
| Average Review Score for Late deliveries | Exact value not labeled in the screenshot | Experience Avg Review filtered to FactOrderExperience.DeliveryStatus = "Late"; also defined by Late Avg Review |

Late Deliveries compares actual and estimated customer-delivery timestamps per
order. Delivered Orders counts orders with a nonblank actual delivery timestamp.
Average Delivery Days has no explicit missing-delivery filter in its DAX, so
12.50 days is documented as the verified dashboard result rather than a newly
validated delivered-only statistic. The on-time percentage is the implemented
complement of the late percentage, not a separately counted measure.

The delivery-versus-review chart uses
[FactOrderExperience](../powerbi/ecommerce-analysis.SemanticModel/definition/tables/FactOrderExperience.tmdl),
which has one row per order. Before the left merge into orders,
[agg_OrderReviews](../powerbi/ecommerce-analysis.SemanticModel/definition/expressions.tmdl)
groups multiple reviews per order and computes AvgReviewScore using List.Average.
It is a non-loaded Power Query transformation helper with Enable Load disabled,
not a semantic-model table. FactOrderExperience stores the merged AvgReviewScore;
no relationship to the helper is needed or present.
Experience Avg Review then averages these nonblank order-level scores.
This supports the comparison without joining item-level facts directly to
individual reviews and multiplying records. An order without an actual delivery
timestamp has a null DeliveryStatus and is not in either named status group.

**Interpretation:** Late deliveries are associated with lower average review
scores than on-time deliveries in the saved Customer Experience chart. Exact
group averages are not labeled, so the previously supplied point estimates are
not retained as repository-verified results. This is an **association, not
evidence of causation**. The comparison
does not control for differences in order mix or other aspects of the customer
experience and does not prove that changing delivery status would produce a
particular score increase.

**Business implication:** Delivery reliability is a supported area for further
operational investigation. Use the implemented state-level delivery comparisons
to investigate where delays occur, checking volumes before prioritizing action.
No worst-performing state, root cause, or expected financial benefit is claimed
without additional verified results.
