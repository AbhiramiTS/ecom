import django_filters
from django_filters import DateFilter, CharFilter

from .models import *

class ProductNameFilter(django_filters.FilterSet):
	name = CharFilter(field_name='name', lookup_expr='icontains')


	class Meta:
		model = Product
		fields = ['name']
		# exclude = ['name', 'date_created','price','category','description']
