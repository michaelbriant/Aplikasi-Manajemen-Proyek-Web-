# Generated by Django 5.2 on 2025-06-13 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyek', '0005_penutupanproyek'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(blank=True, choices=[('Berlangsung', 'Berlangsung'), ('Berhenti', 'Berhenti'), ('Selesai', 'Selesai')], max_length=20, null=True, verbose_name='Status Proyek'),
        ),
    ]
