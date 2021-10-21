from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 tables=[],
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id=redshift_conn_id,
        self.tables = tables

    def execute(self, context):
        for table in self.tables:
            results = redshift.get_records(f"SELECT COUNT(*) FROM {table}")
            if results < 1:
                raise ValueError(f"Data quality check failed. No results found in table '{table}'.")
                self.log.info(f"Data quality check failed. No results found in table '{table}'.")
#           TODO: Would be great to separate this operator into specific suboperators that specifically check for things like null values in columns, etc. but that is overloading this operator. The new operator would need to take inputs like table, column, value, and operator to know what to check for and what to validate.
