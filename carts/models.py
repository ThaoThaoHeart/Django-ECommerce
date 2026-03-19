from django.db import models
from djangoecommerce import settings
from catalog.models import Product, Variation

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()

    def variation_ids(self):
        return {variation.pk for variation in self.variations.all()}

    def matches_variations(self, variations):
        selected_variation_ids = {variation.pk for variation in variations}
        return self.variation_ids() == selected_variation_ids

    @classmethod
    def find_matching_item(cls, *, cart, product, variations):
        candidate_items = cls.objects.filter(cart=cart, product=product).prefetch_related("variations")
        return next(
            (item for item in candidate_items if item.matches_variations(variations)),
            None,
        )

    def __str__(self):
        return self.product.name
    