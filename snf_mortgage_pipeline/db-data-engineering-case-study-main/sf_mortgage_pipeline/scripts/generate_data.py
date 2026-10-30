import csv, json
from pathlib import Path

out = Path(__file__).resolve().parents[1] / "data"
out.mkdir(exist_ok=True)
apps = [
 {"application_id":"APP1001","applicant_id":"C1001","applicant_name":"Jordan Lee","loan_amount":380000,"property_value":400000,"monthly_gross_income":12000},
 {"application_id":"APP1002","applicant_id":"C1002","applicant_name":"Taylor Morgan","loan_amount":490000,"property_value":500000,"monthly_gross_income":9000},
 {"application_id":"APP1003","applicant_id":"C1003","applicant_name":"Casey Patel","loan_amount":250000,"property_value":350000,"monthly_gross_income":8000},
 {"application_id":"APP1004","applicant_id":"C1004","applicant_name":"Riley Chen","loan_amount":200000,"property_value":300000,"monthly_gross_income":7000},
 {"application_id":"APP1005","applicant_id":"C1005","applicant_name":"Alex Rivera","loan_amount":180000,"property_value":300000,"monthly_gross_income":6000},
 {"application_id":"APP1006","applicant_id":"C1006","applicant_name":"Sam Kim","loan_amount":None,"property_value":280000,"monthly_gross_income":6500}
]
(out/"mortgage_applications.json").write_text(json.dumps(apps, indent=2), encoding="utf-8")
rows = [
 {"applicant_id":"C1001","ssn":"900-00-1001","fico_score":740,"monthly_debt":2500},
 {"applicant_id":"C1002","ssn":"900-00-1002","fico_score":700,"monthly_debt":4200},
 {"applicant_id":"C1003","ssn":"900-00-1003","fico_score":610,"monthly_debt":1000},
 {"applicant_id":"C1004","ssn":"900-00-1004","fico_score":645,"monthly_debt":2800},
 {"applicant_id":"C1005","ssn":"900-00-1005","fico_score":680,"monthly_debt":1500}
]
with (out/"credit_bureau.csv").open("w", newline="", encoding="utf-8") as f:
 w=csv.DictWriter(f, fieldnames=["applicant_id","ssn","fico_score","monthly_debt"]); w.writeheader(); w.writerows(rows)
print("Generated synthetic JSON and CSV in", out)
