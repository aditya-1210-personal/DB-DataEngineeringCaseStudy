variable "database_name" { type=string, default="MORTGAGE_DB" }
variable "warehouse_name" { type=string, default="MORTGAGE_WH" }
resource "snowflake_database" "mortgage" { name=var.database_name }
resource "snowflake_warehouse" "mortgage" {
 name=var.warehouse_name
 warehouse_size="XSMALL"
 auto_suspend=60
 auto_resume=true
 initially_suspended=true
}
resource "snowflake_schema" "RAW" { database=snowflake_database.mortgage.name name="RAW" }
resource "snowflake_schema" "STAGE" { database=snowflake_database.mortgage.name name="STAGE" }
resource "snowflake_schema" "CURATED" { database=snowflake_database.mortgage.name name="CURATED" }
resource "snowflake_role" "pipeline" { name="MORTGAGE_PIPELINE_ROLE" }
resource "snowflake_role" "analyst" { name="MORTGAGE_ANALYST" }
resource "snowflake_role" "compliance" { name="COMPLIANCE_OFFICER" }
