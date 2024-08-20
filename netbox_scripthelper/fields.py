
from django import forms
from django.conf import settings
from extras.scripts import ScriptVariable
from utilities.forms import widgets
from utilities.forms.fields import ExpandableNameField


class DynamicChoiceField(forms.ChoiceField):
    """
    Dynamic selection field for a object, backed by NetBox's REST API.
    """

    widget = widgets.APISelect

    def __init__(self, query_params=None, initial_params=None, null_option=None, disabled_indicator=None,
                 fetch_trigger=None, empty_label=None, *args, **kwargs):
        self.query_params = query_params or {}
        self.initial_params = initial_params or {}
        self.null_option = null_option
        self.disabled_indicator = disabled_indicator
        self.fetch_trigger = fetch_trigger

        self.to_field_name = kwargs.get('to_field_name')
        self.empty_option = empty_label or ""

        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = {
            'data-empty-option': self.empty_option
        }

        # Set value-field attribute if the field specifies to_field_name
        if self.to_field_name:
            attrs['value-field'] = self.to_field_name

        # Set the string used to represent a null option
        if self.null_option is not None:
            attrs['data-null-option'] = self.null_option

        # Set the disabled indicator, if any
        if self.disabled_indicator is not None:
            attrs['disabled-indicator'] = self.disabled_indicator

        # Set the fetch trigger, if any.
        if self.fetch_trigger is not None:
            attrs['data-fetch-trigger'] = self.fetch_trigger

        # Attach any static query parameters
        if (len(self.query_params) > 0):
            widget.add_query_params(self.query_params)

        return attrs

    def clean(self, value):
        """
        When null option is enabled and "None" is sent as part of a form to be submitted, it is sent as the
        string 'null'.  This will check for that condition and gracefully handle the conversion to a NoneType.
        """
        if self.null_option is not None and value == settings.FILTERS_NULL_CHOICE_VALUE:
            return None
        return super().clean(value)

    def validate(self, value):
        """
        No validation is required as the choices is dynamic.
        """
        return


class DynamicChoiceVar(ScriptVariable):
    form_field = DynamicChoiceField

    def __init__(self, api_url, query_params=None, null_option=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.api_url = api_url
        self.field_attrs.update({
            'query_params': query_params,
            'null_option': null_option,
        })

    def as_field(self):
        form_field = super().as_field()
        form_field.widget.attrs['data-url'] = self.api_url

        return form_field


class ExpandableStringVar(ScriptVariable):
    form_field = ExpandableNameField
