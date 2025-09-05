from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(db_index=True, max_length=64)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('asset_type', models.CharField(choices=[('STOCK', 'Stock'), ('BOND', 'Bond'), ('CRYPTO', 'Crypto'), ('CASH', 'Cash'), ('FUND', 'Fund'), ('ETF', 'ETF'), ('FOREX', 'Forex'), ('FOREIGN_STOCK', 'Foreign stock')], db_index=True, max_length=32)),
                ('currency', models.CharField(blank=True, max_length=10)),
                ('exchange', models.CharField(blank=True, max_length=64)),
                ('isin', models.CharField(blank=True, db_index=True, max_length=32)),
                ('cusip', models.CharField(blank=True, max_length=32)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['symbol', 'name'],
                'indexes': [models.Index(fields=['symbol'], name='assets_asset_symbol_idx'), models.Index(fields=['isin'], name='assets_asset_isin_idx')],
            },
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolios', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-is_default', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Holding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=8, default='0', max_digits=20)),
                ('average_price', models.DecimalField(blank=True, decimal_places=8, max_digits=20, null=True)),
                ('currency', models.CharField(blank=True, max_length=10)),
                ('acquired_at', models.DateTimeField(blank=True, null=True)),
                ('in_portfolio', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='holdings', to='assets.Asset')),
                ('portfolio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='holdings', to='assets.Portfolio')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='holdings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='holding',
            constraint=models.UniqueConstraint(fields=['user', 'asset', 'portfolio'], name='unique_user_asset_portfolio'),
        ),
    ]
