from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID'
                )),
                ('series', models.ForeignKey(
                    on_delete=models.deletion.CASCADE, to='reader.Series'
                )),
                ('user', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='bookmarks', to=settings.AUTH_USER_MODEL
                )),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='bookmark',
            unique_together={('series', 'user')},
        ),
    ]
