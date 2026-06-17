from backend.rag.tools import (
    get_loan_balance,
    get_emi_schedule,
    get_account_details,
    get_payment_history,
    get_complaint_status,
)

customer_id = 1001

print("========== LOAN ==========")
print(get_loan_balance(customer_id))

print("\n========== EMI ==========")
print(get_emi_schedule(customer_id))

print("\n========== ACCOUNT ==========")
print(get_account_details(customer_id))

print("\n========== PAYMENTS ==========")
print(get_payment_history(customer_id))

print("\n========== COMPLAINTS ==========")
print(get_complaint_status(customer_id))