from django import forms
from django.template import loader

class CustomHTMLSlug(forms.Widget):
    template_name = 'admin/sims/simstore/components/customize_slug.html'
    def __init__(self, choices=(), attrs=None, *args, **kwargs):
        super().__init__(attrs, *args, **kwargs)
        self.choices = choices

    def render(self, name, value, attrs=None, renderer=None):
        template = loader.get_template(self.template_name)
        context = {
            'value': value,
        }
        return template.render(context)

    def value_from_datadict(self, data, files, name):
        return data.get(name)