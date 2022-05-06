from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import *


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100, required=False, label = 'First Name')
    last_name = forms.CharField(
        max_length=100, required=False, label = 'Last Name')
    email = forms.EmailField(
        max_length=150, help_text='Please provide a valid email address.', label = 'Email address')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password1', 'password2', )
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.items():
            placeholder = field.label
            if field.required:
                placeholder += '*'
            field.widget.attrs.update(dict(placeholder = placeholder))
            field.label = ''

class ProjectAddForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProjectAddForm, self).__init__(*args, **kwargs)
        self.fields['users'].required = False
        for key, field in self.fields.items():
            if isinstance(field.widget, forms.SelectMultiple):
                continue
            placeholder = field.label
            if field.required:
                placeholder += '*'
            field.widget.attrs.update(dict(placeholder = placeholder))
            field.label = ''

class MethodAddForm(ModelForm):
    class Meta:
        model = AnalysisMethod
        fields = '__all__'
        widgets = dict(
            name = forms.TextInput(attrs = dict(id = 'id_name_method'))
        )
    def __init__(self, *args, **kwargs):
        super(MethodAddForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.items():
            placeholder = field.label
            if field.required:
                placeholder += '*'
            field.widget.attrs.update(dict(placeholder = placeholder))
            field.label = ''

class GeneAddForm(ModelForm):
    class Meta:
        model = Gene
        fields = '__all__'
        widgets = dict(
            name = forms.TextInput(attrs = dict(id = 'id_name_gene'))
        )
    def __init__(self, *args, **kwargs):
        super(GeneAddForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.items():
            placeholder = field.label
            if field.required:
                placeholder += '*'
            field.widget.attrs.update(dict(placeholder = placeholder))
            field.label = ''

# class ChipsetAddForm(ModelForm):
#     class Meta:
#         model = Chipset
#         fields = '__all__'
#         widgets = dict(
#             name = forms.TextInput(attrs = dict(id = 'id_name_chipset'))
#         )


class SpecificationAddForm(ModelForm):
    class Meta:
        model = Specification
        exclude = ('name',)
        widgets = dict(
            gene = forms.Select(attrs = dict(multiple = True))
        )

class ChipsetSpecificationAddForm(ModelForm):
    class Meta:
        model = ChipsetSpecification
        exclude = ('project', )
        widgets = dict(
            gene = forms.Select(attrs = dict(multiple = True)),
            name = forms.TextInput(attrs = dict(id = 'id_name_chipset'))
        )

class DatapointTypeAddForm(ModelForm):
    class Meta:
        model = DatapointType
        exclude = ('validators', 'options')
    def __init__(self, *args, **kwargs):
        super(DatapointTypeAddForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                print(field.widget)
                continue
            placeholder = field.label
            if field.required:
                placeholder += '*'
            field.widget.attrs.update(dict(placeholder = placeholder))
            field.label = ''

class DatapointValidatorAddForm(ModelForm):
    class Meta:
        model = DatapointValidator
        fields = '__all__'

class PatientAddForm(ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'dateofbirth': forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD', 'type': 'date'}),
        }

class ProjectIdAddForm(ModelForm):
    class Meta:
        model = ProjectId
        fields = ('project', 'projectid',)
        labels = dict(projectid = 'Project Specific Patient ID')
    def __init__(self, *args, **kwargs):
        super(ProjectIdAddForm, self).__init__(*args, **kwargs)
        self.fields['projectid'].required = False


class SampleAddForm(ModelForm):
    class Meta:
        model = Sample
        # fields = ('dateofreceipt', 'mutation', 'type', 'location', 'icd10')
        fields = ('dateofreceipt', 'visit',)
        widgets = {
            'dateofreceipt': forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD', 'type': 'date'})
        }
        # labels = dict(mutation = 'Mutation Burden', dateofreceipt = 'Date of Entry', icd10 = 'ICD10')
        labels = dict(dateofreceipt = 'Date of Entry', visit = 'Visit of the day')
    # def __init__(self, *args, **kwargs):
    #     super(SampleAddForm, self).__init__(*args, **kwargs)
    #     self.fields['type'].required = False
    #     self.fields['location'].required = False
    #     self.fields['icd10'].required = False