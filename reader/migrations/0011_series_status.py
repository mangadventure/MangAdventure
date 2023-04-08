from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('reader', '0010_null_volumes')]

    operations = [
        migrations.AddField(
            model_name='series',
            name='status',
            field=models.CharField(
                choices=[
                    ('ongoing', 'Ongoing'),
                    ('completed', 'Completed'),
                    ('hiatus', 'On Hiatus'),
                    ('canceled', 'Canceled')
                ],
                default='ongoing', max_length=10,
                help_text='The publication status of the series.'
            )
        ),
        migrations.RunSQL(
            sql="""
            UPDATE reader_series SET status = 'completed' WHERE completed;
            """,
            reverse_sql="""
            UPDATE reader_series SET completed =
                (status == 'completed') OR (status == 'canceled');
            """
        ),
        migrations.RemoveField(
            model_name='series',
            name='completed'
        )
    ]
