from django import forms
from django.contrib.auth.forms import AuthenticationForm
from shop.models import MainCategory, SubCategory, Brand, Product, ProductImage


class AdminLoginForm(AuthenticationForm):
    """Custom Admin Login Form"""

    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-green-500 focus:outline-none transition-all duration-300',
            'placeholder': 'admin@sportnest.com',
            'autocomplete': 'email',
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-green-500 focus:outline-none transition-all duration-300',
            'placeholder': '••••••••',
        })
    )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(
                "Access denied. Only staff members can access the admin panel.",
                code='not_staff'
            )


class MainCategoryForm(forms.ModelForm):
    class Meta:
        model = MainCategory
        fields = ['name', 'slug', 'icon', 'image', 'description', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'slug': forms.TextInput(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'icon': forms.TextInput(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'description': forms.Textarea(attrs={'class': 'w-full border rounded-xl px-4 py-2', 'rows': 4}),
            'order': forms.NumberInput(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['main_category', 'name', 'slug', 'image', 'description', 'order', 'is_active']
        widgets = {
            'main_category': forms.Select(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'name': forms.TextInput(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'slug': forms.TextInput(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'description': forms.Textarea(attrs={'class': 'w-full border rounded-xl px-4 py-2', 'rows': 4}),
            'order': forms.NumberInput(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'slug', 'logo', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'slug': forms.TextInput(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'sku',
            'subcategory', 'brand',
            'description', 'specifications',
            'price', 'compare_at_price',
            'stock', 'is_active', 'is_featured', 'is_new_arrival', 'is_bestseller',
            'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'slug': forms.TextInput(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'sku': forms.TextInput(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'subcategory': forms.Select(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'brand': forms.Select(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'description': forms.Textarea(attrs={'class': 'w-full border rounded-xl px-4 py-2', 'rows': 5}),
            'specifications': forms.Textarea(attrs={'class': 'w-full border rounded-xl px-4 py-2', 'rows': 5, 'placeholder': '{"Size":"L","Material":"Cotton"}'}),
            'price': forms.NumberInput(attrs={'class': 'w-full border rounded-xl px-4 py-2', 'step': '0.01'}),
            'compare_at_price': forms.NumberInput(attrs={'class': 'w-full border rounded-xl px-4 py-2', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full border rounded-xl px-4 py-2'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
            'is_new_arrival': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
            'is_bestseller': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'order']
        widgets = {
            'order': forms.NumberInput(attrs={'class': 'w-full border rounded-xl px-3 py-2'}),
        }