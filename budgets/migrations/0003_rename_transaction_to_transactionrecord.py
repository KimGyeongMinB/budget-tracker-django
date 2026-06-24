from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("budgets", "0002_transaction"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Transaction",
            new_name="TransactionRecord",
        ),
        migrations.AlterField(
            model_name="transactionrecord",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="transaction_records",
                to="budgets.category",
            ),
        ),
        migrations.AlterField(
            model_name="transactionrecord",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transaction_records",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
