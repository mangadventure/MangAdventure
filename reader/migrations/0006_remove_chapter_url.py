from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0005_categories'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chapter',
            name='url',
        ),
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.CharField(
                auto_created=True, default='', max_length=25,
                primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(
                help_text='The name of the category. '
                'Must be unique and cannot be changed once set.',
                max_length=25, unique=True
            ),
        ),
    ]
