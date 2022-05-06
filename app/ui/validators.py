from django.core.validators import RegexValidator, EmailValidator, MinLengthValidator

## new
alnum_us_minus_space = dict(regex='^[A-Za-z0-9_\- ]+$',
             msg='Only alphanumeric characters, -, _ and space are allowed')
alnum_us_minus_space_val = RegexValidator(alnum_us_minus_space['regex'], alnum_us_minus_space['msg'])
