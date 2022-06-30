from django.core.validators import MinValueValidator
from django.db import migrations, models

from reader.models import _NonZeroIntegerField


class Migration(migrations.Migration):
    dependencies = [('reader', '0009_constraints')]

    operations = [
        migrations.AlterModelOptions(
            name='chapter',
            options={
                'get_latest_by': ('published', 'modified')
            }
        ),
        migrations.AlterField(
            model_name='chapter',
            name='number',
            field=models.FloatField(
                help_text='The number of the chapter.',
                default=0, validators=(MinValueValidator(0),)
            )
        ),
        migrations.AlterField(
            model_name='chapter',
            name='volume',
            field=_NonZeroIntegerField(
                null=True, blank=True, help_text=(
                    'The volume of the chapter. '
                    'Leave blank if the series has no volumes.'
                )
            )
        ),
        migrations.RunSQL(
            sql='UPDATE reader_chapter SET volume = NULL WHERE volume = 0;',
            reverse_sql=(
                'UPDATE reader_chapter SET volume = 0 WHERE volume IS NULL;'
            )
        ),
        migrations.AddConstraint(
            model_name='chapter',
            constraint=models.CheckConstraint(
                name='volume_number_positive',
                check=models.Q(
                    ('volume__isnull', True),
                    ('volume__gt', 0), _connector='OR'
                )
            )
        )
    ]
