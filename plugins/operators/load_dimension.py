from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 origin_table="",
                 query="",
                 destination_table="",
                 append=False,
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.origin_table = origin_table
        self.query = query
        self.destination_table = destination_table
        self.append = append

    def execute(self, context):
        aws_hook = AwsHook("aws_credentials")
        credentials = aws_hook.get_credentials()
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        
        if not self.append:
            redshift.run(f"DELETE FROM {self.destination_table}")
            self.log.info(f"Dropped {self.destination_table} table")
            
        redshift.run(self.query)
        self.log.info(f'Executed {self.query} SQL dimension table query.')
