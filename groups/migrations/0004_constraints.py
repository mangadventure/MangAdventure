from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('groups', '0003_alter_group_id')]

    operations = [
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='role',
            constraint=models.UniqueConstraint(
                fields=('member', 'role', 'group'),
                name='unique_member_role'
            ),
        ),
    ]
