# Generated by Django 5.1.1 on 2024-10-08 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0004_alter_invoice_invoice_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoiceNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_number', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_number',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]