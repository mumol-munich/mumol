from model_utils import Choices
from django.utils.translation import gettext as _


DPTYPE = Choices(
    (('integer'), _('integer')),
    (('numeric'), _('numeric')),
    (('varchar'), _('varchar')),
    (('boolean'), _('boolean')),
    (('select'), _('select')),
    (('multiple'), _('multiple')),
)

DPVALIDATOR = Choices(
    (('regex'), _('RegexValidator')),
    (('email'), _('EmailValidator')),
    (('maxval'), _('MaxValueValidator')),
    (('minval'), _('MinValueValidator')),
    (('maxlen'), _('MaxLengthValidator')),
    (('minlen'), _('MinLengthValidator')),
    (('decval'), _('DecimalValidator')),
)

DPSTATUS = Choices(
    (('positive'), _('Positive')),
    (('negative'), _('Negative')),
    (('unknown'), _('Unknown')),
    (('na'), _('Not Available')),
)

STYPE = Choices(
    (('solid'), _('Solid')),
    (('liquid'), _('Liquid')),
    (('na'), _('Not Available'))
)