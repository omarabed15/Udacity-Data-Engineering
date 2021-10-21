from airflow.hooks.postgres_hook import PostgresHook
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'
    
    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 staging_table="",
                 source_location="",
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.staging_table = staging_table
        self.source_location = source_location
        self.execution_date = kwargs.get('execution_date')

    def execute(self, context):
        aws_hook = AwsHook("aws_credentials")
        credentials = aws_hook.get_credentials()
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        staging_sql_start = f"""
                DROP TABLE IF EXISTS {self.staging_table};
                COPY {self.staging_table}
            """
        staging_sql_end = f"""
                ACCESS_KEY_ID {credentials.access_key}
                SECRET_ACCESS_KEY {credentials.secret_key}
                json 'auto'
                timeformat 'epochmillisecs'
                region 'us-west-2';
            """
        if self.execution_date:
            year = self.execution_date.strftime('%Y')
            month = self.execution_date.strftime('%m')
            staging_sql_middle = f'FROM {self.source_location}/{year}/{month}/'
        else: 
            staging_sql_middle = f'FROM {self.source_location}'

        staging_sql = f'{staging_sql_start} {staging_sql_middle} {staging_sql_end}'

        redshift.run(staging_sql)
        self.log.info(f'Staged {self.staging_table} {staging_sql_middle} to redshift.')
