from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('reader', '0004_float_numbers')]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.CharField(
                    auto_created=True, primary_key=True,
                    max_length=25, serialize=False
                )),
                ('name', models.CharField(
                    help_text='The name of the category. '
                    'Must be unique and cannot be changed once set',
                    max_length=25, unique=True, serialize=False
                )),
                ('description', models.CharField(
                    help_text='A description for the category.',
                    max_length=250
                )),
            ],
            options={'verbose_name_plural': 'categories'},
        ),
        migrations.AddField(
            model_name='series',
            name='categories',
            field=models.ManyToManyField(
                blank=True, to='reader.Category'
            ),
        ),
    ]
