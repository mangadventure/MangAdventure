from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('reader', '0008_chapter_views')]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='modified',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='series',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='series',
            name='modified',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='alias',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='chapter',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='alias',
            constraint=models.UniqueConstraint(
                fields=('name', 'content_type', 'object_id'),
                name='unique_alias_content_object'
            ),
        ),
        migrations.AddConstraint(
            model_name='chapter',
            constraint=models.UniqueConstraint(
                fields=('series', 'volume', 'number'),
                name='unique_chapter_number'
            ),
        ),
        migrations.AddConstraint(
            model_name='chapter',
            constraint=models.CheckConstraint(
                check=models.Q(('number__gte', 0)),
                name='chapter_number_positive'
            ),
        ),
        migrations.AddConstraint(
            model_name='page',
            constraint=models.CheckConstraint(
                check=models.Q(('number__gte', 1)),
                name='page_number_nonzero'
            ),
        ),
    ]
