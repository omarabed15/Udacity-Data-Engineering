from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadFactOperator(BaseOperator):

    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 origin_table="",
                 query="",
                 destination_table="",
                 *args, **kwargs):

        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.origin_table = origin_table
        self.query = query
        self.destination_table = destination_table

    def execute(self, context):
        aws_hook = AwsHook("aws_credentials")
        credentials = aws_hook.get_credentials()
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        
        redshift.run(self.query)
        self.log.info(f'Executed {self.query} SQL fact table query.')
