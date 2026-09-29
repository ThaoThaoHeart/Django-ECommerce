import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from catalog.models import Category, Product, Variation


CATALOG = {
    'Guitars': {
        'products': [
            'Yamaha Acoustic Guitar', 'Pro Bass Guitar', 'Classic Acoustic Guitar',
            'Electric Guitar Starter Pack', 'Travel Guitar', 'Twelve-String Guitar', 'Hollow Body Jazz Guitar',
        ],
        'variations': {'color': ['Natural', 'Black'], 'size': ['Full Size', '3/4']},
        'blurb': 'Balanced tone, comfortable neck profile and solid tuning stability for players at every level.',
    },
    'Keyboards': {
        'products': [
            'Accordion', 'Electric Keyboard', 'Grand Piano', 'Digital Stage Piano',
            'MIDI Controller', 'Synthesizer', 'Portable Keyboard',
        ],
        'variations': {'color': ['Black', 'White'], 'key_count': ['61 Keys', '88 Keys']},
        'blurb': 'Expressive, velocity-sensitive keys and rich onboard sounds for practice, stage and studio.',
    },
    'Drums': {
        'products': [
            'Bass Drum', 'Cymbal', 'Snare Drum', 'Electronic Drum Kit', 'Cajon', 'Floor Tom',
        ],
        'variations': {'color': ['Black', 'Red'], 'material': ['Maple', 'Birch']},
        'blurb': 'Punchy attack and warm sustain from carefully selected shells and hardware built to last.',
    },
    'Software': {
        'products': [
            'Bass Guitar Software', 'EQ Software', 'Piano Software', 'Drum Machine Plugin', 'Mastering Suite',
        ],
        'variations': {'package_set': ['Standard', 'Pro']},
        'blurb': 'Studio-grade processing that runs on every major DAW, with lifetime updates included.',
    },
}


class Command(BaseCommand):
    help = 'Replace the demo catalog with a fresh set of categories, products and variations.'

    def handle(self, *args, **options):
        rng = random.Random(42)
        Product.objects.filter(category__name__in=CATALOG).delete()

        product_count = variation_count = 0
        for category_name, spec in CATALOG.items():
            category, _ = Category.objects.get_or_create(name=category_name, defaults={'slug': slugify(category_name)})

            for product_name in spec['products']:
                product = Product.objects.create(
                    category=category,
                    name=product_name,
                    slug=slugify(product_name),
                    description=f"The {product_name} from our {category_name.lower()} collection. {spec['blurb']}",
                    price=Decimal(str(round(rng.uniform(49.0, 999.0), 2))),
                    # Roughly one in eight products is out of stock so the storefront shows both states.
                    stock=0 if rng.random() < 0.125 else rng.randint(1, 50),
                )
                product_count += 1

                variations = [
                    Variation(product=product, variation_category=variation_category, variation_value=value)
                    for variation_category, values in spec['variations'].items()
                    for value in values
                ]
                Variation.objects.bulk_create(variations)
                variation_count += len(variations)

        self.stdout.write(self.style.SUCCESS(f'Created {product_count} products and {variation_count} variations.'))
