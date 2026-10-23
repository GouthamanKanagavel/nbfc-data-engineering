SELECT
    loan_id,
    total_principal_due,
    total_successful_payment,
    estimated_outstanding_principal,
    payment_coverage_pct,
    collection_efficiency_pct
FROM {{ ref('fact_loan_qa') }}
WHERE estimated_outstanding_principal <>
      GREATEST(
          total_principal_due - total_successful_payment,
          0
      )
   OR (
       total_principal_due = 0
       AND payment_coverage_pct <> 0
   )
   OR (
       total_principal_due <> 0
       AND payment_coverage_pct <>
           ROUND(
               total_successful_payment
               / total_principal_due * 100,
               2
           )
   )
   OR (
       total_scheduled_emi = 0
       AND collection_efficiency_pct <> 0
   )
   OR (
       total_scheduled_emi <> 0
       AND collection_efficiency_pct <>
           ROUND(
               total_successful_collection
               / total_scheduled_emi * 100,
               2
           )
   )