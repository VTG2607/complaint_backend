import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class UppercaseAndNumberValidator:
    """
    Validate that the password contains at least one uppercase letter
    and at least one number.
    """
    
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("The password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
        if not re.search(r'\d', password):
            raise ValidationError(
                _("The password must contain at least one number."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one uppercase letter and one number."
        )
