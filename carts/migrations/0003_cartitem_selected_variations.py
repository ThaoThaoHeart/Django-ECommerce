from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		("carts", "0002_cart_session_key"),
	]

	operations = [
		migrations.AddField(
			model_name="cartitem",
			name="selected_variations",
			field=models.CharField(blank=True, default="", max_length=500),
		),
	]