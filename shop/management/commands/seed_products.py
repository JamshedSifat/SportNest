# shop/management/commands/seed_products.py

from django.core.management.base import BaseCommand
from shop.models import Product, SubCategory, Brand
from django.utils.text import slugify
from django.core.files.base import ContentFile
import requests

class Command(BaseCommand):
    help = 'Seed 60+ sample products with images'
    
    def handle(self, *args, **kwargs):
        
        Brand.objects.all().delete()
        
        brand_names = [
            'Nike', 'Adidas', 'Puma', 'SS', 'Gray Nicolls', 'Yonex',
            'Under Armour', 'New Balance', 'Reebok', 'Wilson', 'Macron', 'Hummel'
        ]
        brands = {}
        for name in brand_names:
            brand, _ = Brand.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
            brands[name] = brand
            self.stdout.write(f'✅ Brand: {name}')
        
        subcategories = SubCategory.objects.all()
        if not subcategories.exists():
            self.stdout.write(self.style.ERROR('No subcategories! Run: py manage.py seed_categories first'))
            return
        
        Product.objects.all().delete()
        
        products_data = [
            # ===== ⚽ FOOTBALL BOOTS (6) =====
            {'name': 'Nike Mercurial Superfly 9 Elite FG', 'price': 15999, 'compare': 19999, 'brand': 'Nike', 'sub': 'Premier League', 'stock': 25, 'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600'},
            {'name': 'Adidas Predator Edge.1 FG', 'price': 12999, 'compare': 15999, 'brand': 'Adidas', 'sub': 'La Liga', 'stock': 30, 'image': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=600'},
            {'name': 'Puma Future Ultimate FG', 'price': 11999, 'compare': 14999, 'brand': 'Puma', 'sub': 'Champions League', 'stock': 20, 'image': 'https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=600'},
            {'name': 'Nike Phantom GT2 Elite FG', 'price': 14999, 'compare': 17999, 'brand': 'Nike', 'sub': 'International Teams', 'stock': 22, 'image': 'https://images.unsplash.com/photo-1511886929837-354d827aae26?w=600'},
            {'name': 'Adidas X Speedportal.1 FG', 'price': 13999, 'compare': 16999, 'brand': 'Adidas', 'sub': 'Bundesliga', 'stock': 18, 'image': 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600'},
            {'name': 'Nike Tiempo Legend 10 Elite FG', 'price': 16999, 'compare': 19999, 'brand': 'Nike', 'sub': 'Serie A', 'stock': 15, 'image': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=600'},
            
            # ===== 🌍 NATIONAL TEAM JERSEYS (12) =====
            {'name': 'Brazil Home Jersey 2026 - Neymar #10', 'price': 4999, 'compare': 6999, 'brand': 'Nike', 'sub': 'International Teams', 'stock': 50, 'image': 'https://images.unsplash.com/photo-1580087256394-dc91c1283d89?w=600'},
            {'name': 'Argentina Home Jersey - Messi #10', 'price': 5499, 'compare': 7499, 'brand': 'Adidas', 'sub': 'International Teams', 'stock': 45, 'image': 'https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=600'},
            {'name': 'France Home Jersey 2026 - Mbappe #10', 'price': 4999, 'compare': 6999, 'brand': 'Nike', 'sub': 'International Teams', 'stock': 55, 'image': 'https://images.unsplash.com/photo-1551958219-acbc608e6377?w=600'},
            {'name': 'England Home Jersey 2026', 'price': 4999, 'compare': 6999, 'brand': 'Nike', 'sub': 'International Teams', 'stock': 40, 'image': 'https://images.unsplash.com/photo-1580087256394-dc91c1283d89?w=600'},
            {'name': 'Germany Home Jersey 2026', 'price': 4499, 'compare': 5999, 'brand': 'Adidas', 'sub': 'International Teams', 'stock': 38, 'image': 'https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=600'},
            {'name': 'Spain Home Jersey 2026', 'price': 4499, 'compare': 5999, 'brand': 'Adidas', 'sub': 'International Teams', 'stock': 35, 'image': 'https://images.unsplash.com/photo-1551958219-acbc608e6377?w=600'},
            {'name': 'Portugal Home Jersey 2026 - Ronaldo #7', 'price': 4999, 'compare': 6999, 'brand': 'Nike', 'sub': 'International Teams', 'stock': 60, 'image': 'https://images.unsplash.com/photo-1587280501638-b5e2c5e5d5c0?w=600'},
            {'name': 'Italy Away Jersey 2026', 'price': 4499, 'compare': 5999, 'brand': 'Puma', 'sub': 'International Teams', 'stock': 40, 'image': 'https://images.unsplash.com/photo-1587280501638-b5e2c5e5d5c0?w=600'},
            {'name': 'Netherlands Home Jersey 2026', 'price': 3999, 'compare': 5499, 'brand': 'Nike', 'sub': 'International Teams', 'stock': 30, 'image': 'https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=600'},
            {'name': 'Belgium Home Jersey 2026', 'price': 3999, 'compare': 5499, 'brand': 'Adidas', 'sub': 'International Teams', 'stock': 28, 'image': 'https://images.unsplash.com/photo-1580087256394-dc91c1283d89?w=600'},
            {'name': 'Croatia Home Jersey 2026', 'price': 3499, 'compare': 4999, 'brand': 'Nike', 'sub': 'International Teams', 'stock': 25, 'image': 'https://images.unsplash.com/photo-1551958219-acbc608e6377?w=600'},
            {'name': 'Bangladesh Home Jersey 2026', 'price': 2499, 'compare': 3499, 'brand': 'Macron', 'sub': 'International Teams', 'stock': 100, 'image': 'https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=600'},
            
            # ===== 🏆 LEAGUE CLUB JERSEYS (10) =====
            {'name': 'Manchester United Home Jersey 2026', 'price': 4499, 'compare': 5999, 'brand': 'Adidas', 'sub': 'Premier League', 'stock': 45, 'image': 'https://images.unsplash.com/photo-1580087256394-dc91c1283d89?w=600'},
            {'name': 'Real Madrid Home Jersey 2026', 'price': 4999, 'compare': 6999, 'brand': 'Adidas', 'sub': 'La Liga', 'stock': 50, 'image': 'https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=600'},
            {'name': 'Barcelona Home Jersey 2026', 'price': 4499, 'compare': 5999, 'brand': 'Nike', 'sub': 'La Liga', 'stock': 48, 'image': 'https://images.unsplash.com/photo-1551958219-acbc608e6377?w=600'},
            {'name': 'Bayern Munich Home Jersey 2026', 'price': 4499, 'compare': 5999, 'brand': 'Adidas', 'sub': 'Bundesliga', 'stock': 35, 'image': 'https://images.unsplash.com/photo-1587280501638-b5e2c5e5d5c0?w=600'},
            {'name': 'PSG Home Jersey 2026', 'price': 4999, 'compare': 6999, 'brand': 'Nike', 'sub': 'Ligue 1', 'stock': 40, 'image': 'https://images.unsplash.com/photo-1580087256394-dc91c1283d89?w=600'},
            {'name': 'Juventus Home Jersey 2026', 'price': 3999, 'compare': 5499, 'brand': 'Adidas', 'sub': 'Serie A', 'stock': 32, 'image': 'https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=600'},
            {'name': 'Liverpool Home Jersey 2026', 'price': 4499, 'compare': 5999, 'brand': 'Nike', 'sub': 'Premier League', 'stock': 42, 'image': 'https://images.unsplash.com/photo-1551958219-acbc608e6377?w=600'},
            {'name': 'Manchester City Home Jersey 2026', 'price': 4499, 'compare': 5999, 'brand': 'Puma', 'sub': 'Premier League', 'stock': 38, 'image': 'https://images.unsplash.com/photo-1587280501638-b5e2c5e5d5c0?w=600'},
            {'name': 'AC Milan Home Jersey 2026', 'price': 3999, 'compare': 5499, 'brand': 'Puma', 'sub': 'Serie A', 'stock': 30, 'image': 'https://images.unsplash.com/photo-1580087256394-dc91c1283d89?w=600'},
            {'name': 'Arsenal Home Jersey 2026', 'price': 3999, 'compare': 5499, 'brand': 'Adidas', 'sub': 'Premier League', 'stock': 36, 'image': 'https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=600'},
            
            # ===== ⚽ FOOTBALLS (4) =====
            {'name': 'Nike Premier League Flight Ball', 'price': 3499, 'compare': 4500, 'brand': 'Nike', 'sub': 'Premier League', 'stock': 60, 'image': 'https://images.unsplash.com/photo-1614632537197-38a17061c2bd?w=600'},
            {'name': 'Adidas UCL Pro Ball Istanbul 2026', 'price': 3999, 'compare': 5499, 'brand': 'Adidas', 'sub': 'Champions League', 'stock': 40, 'image': 'https://images.unsplash.com/photo-1553778263-73a83e43d4e6?w=600'},
            {'name': 'Puma La Liga Official Match Ball', 'price': 2999, 'compare': 3999, 'brand': 'Puma', 'sub': 'La Liga', 'stock': 50, 'image': 'https://images.unsplash.com/photo-1486286701207-1d58e93311ef?w=600'},
            {'name': 'Adidas FIFA World Cup 2026 Ball', 'price': 4499, 'compare': 5999, 'brand': 'Adidas', 'sub': 'International Teams', 'stock': 35, 'image': 'https://images.unsplash.com/photo-1553778263-73a83e43d4e6?w=600'},
            
            # ===== ⚽ TRAINING GEAR (3) =====
            {'name': 'Nike Training Cones Set (20 pcs)', 'price': 999, 'compare': 1499, 'brand': 'Nike', 'sub': 'Training Gear', 'stock': 100, 'image': 'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=600'},
            {'name': 'Adidas Speed Rope Pro', 'price': 799, 'compare': 1199, 'brand': 'Adidas', 'sub': 'Training Gear', 'stock': 85, 'image': 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600'},
            {'name': 'Nike Training Bibs (Set of 10)', 'price': 1499, 'compare': 1999, 'brand': 'Nike', 'sub': 'Training Gear', 'stock': 45, 'image': 'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=600'},
            
            # ===== 🏏 CRICKET (8) =====
            {'name': 'SS Premium English Willow Bat', 'price': 7999, 'compare': 15000, 'brand': 'SS', 'sub': 'IPL', 'stock': 15, 'image': 'https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=600'},
            {'name': 'SS Batting Gloves Pro', 'price': 2499, 'compare': 3500, 'brand': 'SS', 'sub': 'BPL', 'stock': 50, 'image': 'https://images.unsplash.com/photo-1624526267942-ab0ff8a3e972?w=600'},
            {'name': 'SS Batting Pads Elite', 'price': 3499, 'compare': 4500, 'brand': 'SS', 'sub': 'ICC World Cup', 'stock': 35, 'image': 'https://images.unsplash.com/photo-1595063167284-087aaede2f9c?w=600'},
            {'name': 'SS Kashmir Willow Bat', 'price': 3499, 'compare': 5000, 'brand': 'SS', 'sub': 'Cricket Bats', 'stock': 40, 'image': 'https://images.unsplash.com/photo-1589800115721-1c3a8c6d1f06?w=600'},
            {'name': 'Gray Nicolls Pro Gloves', 'price': 2999, 'compare': 4000, 'brand': 'Gray Nicolls', 'sub': 'T20 World Cup', 'stock': 30, 'image': 'https://images.unsplash.com/photo-1622219809260-ce065f3c1c7b?w=600'},
            {'name': 'SS Cricket Helmet Pro', 'price': 4499, 'compare': 5999, 'brand': 'SS', 'sub': 'ICC World Cup', 'stock': 30, 'image': 'https://images.unsplash.com/photo-1596478300473-41002f1b4e47?w=600'},
            {'name': 'Wicket Keeper Gloves Premium', 'price': 1999, 'compare': 2999, 'brand': 'Gray Nicolls', 'sub': 'IPL', 'stock': 25, 'image': 'https://images.unsplash.com/photo-1622219809260-ce065f3c1c7b?w=600'},
            {'name': 'Bangladesh Cricket Jersey 2026', 'price': 2499, 'compare': 3499, 'brand': 'SS', 'sub': 'International Teams', 'stock': 60, 'image': 'https://images.unsplash.com/photo-1580087256394-dc91c1283d89?w=600'},
            
            # ===== 🏀 BASKETBALL (5) =====
            {'name': 'Nike Air Zoom Pegasus 40', 'price': 12999, 'compare': 15999, 'brand': 'Nike', 'sub': 'NBA', 'stock': 30, 'image': 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=600'},
            {'name': 'Adidas Ultraboost Light', 'price': 13999, 'compare': 16999, 'brand': 'Adidas', 'sub': 'Basketball Shoes', 'stock': 25, 'image': 'https://images.unsplash.com/photo-1579338559194-a162d19bf842?w=600'},
            {'name': 'Under Armour Curry 11', 'price': 11999, 'compare': 14999, 'brand': 'Under Armour', 'sub': 'NBA', 'stock': 20, 'image': 'https://images.unsplash.com/photo-1574623452334-1e0ac2b3ccb4?w=600'},
            {'name': 'Wilson NBA Official Basketball', 'price': 2999, 'compare': 3999, 'brand': 'Wilson', 'sub': 'Basketballs', 'stock': 45, 'image': 'https://images.unsplash.com/photo-1519861531496-8f8bbd4c25e8?w=600'},
            {'name': 'LA Lakers LeBron James Jersey', 'price': 3999, 'compare': 5499, 'brand': 'Nike', 'sub': 'NBA', 'stock': 35, 'image': 'https://images.unsplash.com/photo-1587280501638-b5e2c5e5d5c0?w=600'},
            
            # ===== 🎾 TENNIS (4) =====
            {'name': 'Yonex VCORE Pro 97', 'price': 8999, 'compare': 12000, 'brand': 'Yonex', 'sub': 'Tennis Rackets', 'stock': 20, 'image': 'https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=600'},
            {'name': 'Nike Court Air Zoom Vapor Pro', 'price': 10999, 'compare': 13999, 'brand': 'Nike', 'sub': 'Tennis Shoes', 'stock': 18, 'image': 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600'},
            {'name': 'Wilson Pro Staff RF97', 'price': 11999, 'compare': 14999, 'brand': 'Wilson', 'sub': 'Tennis Rackets', 'stock': 15, 'image': 'https://images.unsplash.com/photo-1617083934555-ac7dcdbda3c2?w=600'},
            {'name': 'Dunlop ATP Tennis Balls (4 Pack)', 'price': 599, 'compare': 899, 'brand': 'Wilson', 'sub': 'Tennis Balls', 'stock': 120, 'image': 'https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?w=600'},
            
            # ===== 🏸 BADMINTON (3) =====
            {'name': 'Yonex Astrox 100 ZZ', 'price': 7499, 'compare': 9999, 'brand': 'Yonex', 'sub': 'Badminton Rackets', 'stock': 25, 'image': 'https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=600'},
            {'name': 'Yonex Aerosensa 50 Shuttlecocks', 'price': 1499, 'compare': 2000, 'brand': 'Yonex', 'sub': 'Shuttlecocks', 'stock': 100, 'image': 'https://images.unsplash.com/photo-1613918431703-aa50889e3be9?w=600'},
            {'name': 'Yonex Power Cushion 65 Z3', 'price': 5999, 'compare': 7999, 'brand': 'Yonex', 'sub': 'Badminton Shoes', 'stock': 30, 'image': 'https://images.unsplash.com/photo-1600133275922-c6764a58b5c1?w=600'},
            
            # ===== 👟 RUNNING (4) =====
            {'name': 'Puma Deviate Nitro 2', 'price': 11999, 'compare': 14999, 'brand': 'Puma', 'sub': 'Activewear', 'stock': 20, 'image': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600'},
            {'name': 'New Balance Fresh Foam 1080v13', 'price': 10999, 'compare': 13999, 'brand': 'New Balance', 'sub': 'Activewear', 'stock': 28, 'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600'},
            {'name': 'Reebok Floatride Energy 5', 'price': 6999, 'compare': 8999, 'brand': 'Reebok', 'sub': 'Activewear', 'stock': 35, 'image': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=600'},
            {'name': 'Nike Invincible 3 Running Shoes', 'price': 13999, 'compare': 16999, 'brand': 'Nike', 'sub': 'Activewear', 'stock': 22, 'image': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600'},
            
            # ===== 💪 FITNESS (5) =====
            {'name': 'Nike Pro Yoga Mat Premium', 'price': 2999, 'compare': 3999, 'brand': 'Nike', 'sub': 'Yoga', 'stock': 45, 'image': 'https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=600'},
            {'name': 'Adidas Adjustable Dumbbell 20kg', 'price': 14999, 'compare': 19999, 'brand': 'Adidas', 'sub': 'Weights', 'stock': 10, 'image': 'https://images.unsplash.com/photo-1605296867304-46d5465a13f1?w=600'},
            {'name': 'Reebok Resistance Bands Set', 'price': 1499, 'compare': 2499, 'brand': 'Reebok', 'sub': 'Home Gym', 'stock': 65, 'image': 'https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=600'},
            {'name': 'Under Armour Compression Shirt', 'price': 2499, 'compare': 3499, 'brand': 'Under Armour', 'sub': 'Activewear', 'stock': 55, 'image': 'https://images.unsplash.com/photo-1434682881908-b43d0467b798?w=600'},
            {'name': 'Nike Pro Training Shorts', 'price': 1999, 'compare': 2999, 'brand': 'Nike', 'sub': 'Activewear', 'stock': 70, 'image': 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600'},
            
            # ===== 🎒 ACCESSORIES (7) =====
            {'name': 'Puma Large Sports Bag 60L', 'price': 2499, 'compare': 3499, 'brand': 'Puma', 'sub': 'Sports Bags', 'stock': 60, 'image': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600'},
            {'name': 'Nike Insulated Water Bottle 1L', 'price': 899, 'compare': 1299, 'brand': 'Nike', 'sub': 'Water Bottles', 'stock': 80, 'image': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600'},
            {'name': 'Adidas Sports Cap Black', 'price': 799, 'compare': 1199, 'brand': 'Adidas', 'sub': 'Caps', 'stock': 90, 'image': 'https://images.unsplash.com/photo-1588850561407-ed78c282e36b?w=600'},
            {'name': 'Nike Elite Crew Socks (3 Pairs)', 'price': 699, 'compare': 999, 'brand': 'Nike', 'sub': 'Socks', 'stock': 150, 'image': 'https://images.unsplash.com/photo-1586115457255-2c5daab2a0a3?w=600'},
            {'name': 'Puma Wristband Set (2 pcs)', 'price': 499, 'compare': 799, 'brand': 'Puma', 'sub': 'Wristbands', 'stock': 100, 'image': 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600'},
            {'name': 'Nike Gym Towel Large', 'price': 699, 'compare': 999, 'brand': 'Nike', 'sub': 'Accessories', 'stock': 80, 'image': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600'},
            {'name': 'Adidas Sports Backpack 30L', 'price': 1999, 'compare': 2999, 'brand': 'Adidas', 'sub': 'Sports Bags', 'stock': 45, 'image': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600'},
            
            # ===== 🏊 SWIMMING (2) =====
            {'name': 'Nike Swim Goggles Pro', 'price': 1499, 'compare': 1999, 'brand': 'Nike', 'sub': 'Accessories', 'stock': 50, 'image': 'https://images.unsplash.com/photo-1600965962361-9035dbfd1c50?w=600'},
            {'name': 'Adidas Swimming Cap', 'price': 399, 'compare': 599, 'brand': 'Adidas', 'sub': 'Accessories', 'stock': 120, 'image': 'https://images.unsplash.com/photo-1600965962361-9035dbfd1c50?w=600'},
        ]
        
        created = 0
        for i, data in enumerate(products_data):
            subcategory = SubCategory.objects.filter(name=data['sub']).first()
            if not subcategory:
                subcategory = SubCategory.objects.first()
            
            brand = brands.get(data['brand'])
            discount = int(((data['compare'] - data['price']) / data['compare']) * 100)
            
            product = Product.objects.create(
                name=data['name'],
                sku=f'SN-{i+1000}',
                price=data['price'],
                compare_at_price=data['compare'],
                discount_percentage=discount,
                brand=brand,
                subcategory=subcategory,
                stock=data['stock'],
                is_active=True,
                is_in_stock=True,
                is_featured=i < 10,
                is_new_arrival=i >= 55,
                is_bestseller=i < 8,
                description=f'Premium {data["name"]} from {data["brand"]}. High-quality sports gear designed for peak performance.',
            )
            
            image_url = data.get('image')
            if image_url:
                try:
                    self.stdout.write(f'  📥 {product.name}...')
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        product.image.save(f'{product.sku}.jpg', ContentFile(response.content), save=True)
                        self.stdout.write(f'  🖼️  Saved!')
                except Exception as e:
                    self.stdout.write(f'  ⚠️  {str(e)[:40]}')
            
            created += 1
            self.stdout.write(self.style.SUCCESS(f'✅ [{created}] {product.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 {created} products created!'))
        self.stdout.write(f'📊 {len(brands)} Brands | {created} Products | 🖼️ With Images')