from django import template

register = template.Library()


@register.simple_tag(name='get_src_attrs')
def get_src_attrs(placeholder, image, slick=False):
    """
    :param placeholder: url of static image
    :param image: url of real image
    :param slick: slick carousel requires `data-LAZY`, semantic-ui uses `data-SRC` attribute
    :return: src attribute with temporary static placeholder image, real image will be fetched later from data-attr
    """
    lazy_attr_name = 'lazy' if slick else 'src'
    return f'src={placeholder} data-{lazy_attr_name}={image}'
