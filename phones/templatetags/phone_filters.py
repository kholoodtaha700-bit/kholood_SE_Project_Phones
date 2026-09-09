from django import template
from categories.models import Category

register = template.Library()

@register.inclusion_tag('phones/includes/filter.html', takes_context=True)
def render_category_filter(context):
    request = context['request']
    selected_category = request.GET.get('category', '')
    categories = Category.objects.all()
    
    return {
        'categories': categories,
        'selected_category': selected_category,
    }