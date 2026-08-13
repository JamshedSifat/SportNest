# shop/management/commands/seed_categories.py

from django.core.management.base import BaseCommand
from shop.models import MainCategory, SubCategory

class Command(BaseCommand):
    help = 'Seed initial categories and subcategories'
    
    def handle(self, *args, **kwargs):
        
        SubCategory.objects.all().delete()
        MainCategory.objects.all().delete()
        
        self.stdout.write('Old categories deleted.')
        
        categories = [
            {
                'name': 'Football',
                'icon': '⚽',
                'description': 'Everything for football fans - jerseys, boots, balls & more',
                'order': 1,
                'subcategories': [
                    'Premier League', 'La Liga', 'Serie A', 'Bundesliga', 
                    'Ligue 1', 'Champions League', 'Europa League', 'International Teams',
                    'Training Gear'
                ]
            },
            {
                'name': 'Cricket',
                'icon': '🏏',
                'description': 'Cricket bats, balls, protective gear & team jerseys',
                'order': 2,
                'subcategories': [
                    'IPL', 'BPL', 'PSL', 'ICC World Cup', 
                    'T20 World Cup', 'Asia Cup', 'International Teams', 'Cricket Bats'
                ]
            },
            {
                'name': 'Basketball',
                'icon': '🏀',
                'description': 'Basketball equipment, shoes & apparel',
                'order': 3,
                'subcategories': [
                    'NBA', 'EuroLeague', 'Basketball Shoes', 'Basketballs', 'Training Gear'
                ]
            },
            {
                'name': 'Tennis',
                'icon': '🎾',
                'description': 'Tennis rackets, balls & sportswear',
                'order': 4,
                'subcategories': [
                    'Tennis Rackets', 'Tennis Balls', 'Tennis Shoes', 'Tennis Apparel'
                ]
            },
            {
                'name': 'Badminton',
                'icon': '🏸',
                'description': 'Badminton rackets, shuttlecocks & accessories',
                'order': 5,
                'subcategories': [
                    'Badminton Rackets', 'Shuttlecocks', 'Badminton Shoes', 'Accessories'
                ]
            },
            {
                'name': 'Fitness',
                'icon': '💪',
                'description': 'Gym equipment, supplements & activewear',
                'order': 6,
                'subcategories': [
                    'Home Gym', 'Weights', 'Yoga', 'Supplements', 'Activewear'
                ]
            },
            {
                'name': 'Accessories',
                'icon': '🎒',
                'description': 'Bags, water bottles, caps & more',
                'order': 7,
                'subcategories': [
                    'Sports Bags', 'Water Bottles', 'Caps', 'Socks', 'Wristbands'
                ]
            },
        ]
        
        for cat_data in categories:
            main_cat = MainCategory.objects.create(
                name=cat_data['name'],
                icon=cat_data['icon'],
                description=cat_data['description'],
                order=cat_data['order']
            )
            self.stdout.write(self.style.SUCCESS(f'✅ {main_cat.name}'))
            
            for idx, sub_name in enumerate(cat_data['subcategories']):
                SubCategory.objects.create(
                    main_category=main_cat,
                    name=sub_name,
                    order=idx + 1
                )
                self.stdout.write(f'   └─ {sub_name}')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 All categories seeded!'))