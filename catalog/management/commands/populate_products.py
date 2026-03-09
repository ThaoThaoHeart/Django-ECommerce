from django.core.management.base import BaseCommand
from django.utils.text import slugify
import random
from faker import Faker

from catalog.models import Category, Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        fake = Faker()

        category_products = {
            'Guitars': ['Yamaha Acoustic Guitar', 'Pro Bass Guitar', 'Classic Acoustic Guitar'],
            'Keyboards': ['Accordion', 'Electric Keyboard', 'Grand Piano'],
            'Drums': ['Bass Drum', 'Cymbal', 'Snare Drum'],
            'Software': ['Bass Guitar Software', 'EQ Software', 'Piano Software'],
        }

        category_names = list(category_products.keys())

        for name in category_names:
            Category.objects.get_or_create(name=name, defaults={'slug': slugify(name)})

        Product.objects.filter(category__in=category_names).delete()

        created_count = 0
        for category_name, product_names in category_products.items():
            category_slug = slugify(category_name)

            for index, product_name in enumerate(product_names, start=1):
                Product.objects.create(
                    category=category_name,
                    name=product_name,
                    slug=f"{category_slug}-{index}",
                    description=fake.paragraph(nb_sentences=4),
                    price=round(random.uniform(49.0, 999.0), 2),
                    stock=random.randint(1, 50),
                    image=f"products/{category_slug}/{category_slug}-{index}.jpg",
                    is_active=True,
                )
                created_count += 1

        print(f'Created {created_count} products.')
