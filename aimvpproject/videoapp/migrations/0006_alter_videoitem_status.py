# Generated by Django 5.0.3 on 2024-03-22 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videoapp', '0005_alter_videoitem_path_alter_videoitem_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videoitem',
            name='status',
            field=models.CharField(choices=[('0', 'Processing'), ('1', 'Processed')], default='0', max_length=1),
        ),
    ]
