"""
Utility functions for consistent error handling across the API
"""
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from .exceptions import (
    ResourceNotFoundException,
    InvalidDataException,
    DuplicateResourceException,
    UnauthorizedAccessException,
    ValidationException
)
import logging

logger = logging.getLogger(__name__)


def handle_resource_not_found(model_class, resource_id):
    """
    Helper to handle resource not found errors
    
    Args:
        model_class: Django model class
        resource_id: ID of the resource
        
    Raises:
        ResourceNotFoundException
    """
    try:
        return model_class.objects.get(pk=resource_id)
    except ObjectDoesNotExist:
        logger.warning(f"{model_class.__name__} with ID {resource_id} not found")
        raise ResourceNotFoundException(model_class.__name__, resource_id)


def handle_duplicate_check(model_class, field_name, field_value, exclude_id=None):
    """
    Helper to check for duplicate resources
    
    Args:
        model_class: Django model class
        field_name: Field to check for duplicates
        field_value: Value to check
        exclude_id: Optional ID to exclude from duplicate check (for updates)
        
    Raises:
        DuplicateResourceException
    """
    query = {field_name: field_value}
    if exclude_id:
        queryset = model_class.objects.filter(**query).exclude(pk=exclude_id)
    else:
        queryset = model_class.objects.filter(**query)
    
    if queryset.exists():
        logger.warning(f"Duplicate {model_class.__name__} found with {field_name}={field_value}")
        raise DuplicateResourceException(model_class.__name__, field_name)


def validate_field(field_value, field_name, required=None, field_type=None, **validators):
    """
    Helper to validate a field value
    
    Args:
        field_value: Value to validate
        field_name: Name of field (for error messages)
        required: Whether field is required (None means optional)
        field_type: Expected type (str, int, etc.)
        **validators: Additional validation functions
        
    Raises:
        InvalidDataException if validation fails
    """
    # Check required
    if required and not field_value:
        logger.warning(f"Required field '{field_name}' is empty")
        raise InvalidDataException(field_name, "This field is required")
    
    if not field_value and not required:
        return True
    
    # Check type
    if field_type and field_value is not None:
        if not isinstance(field_value, field_type):
            logger.warning(f"Field '{field_name}' has invalid type. Expected {field_type.__name__}")
            raise InvalidDataException(
                field_name,
                f"Must be of type {field_type.__name__}"
            )
    
    # Run custom validators
    for validator_name, validator_func in validators.items():
        if callable(validator_func):
            try:
                if not validator_func(field_value):
                    logger.warning(f"Field '{field_name}' failed {validator_name} validation")
                    raise InvalidDataException(field_name, f"Failed {validator_name} validation")
            except Exception as e:
                if isinstance(e, InvalidDataException):
                    raise
                logger.error(f"Error running validator {validator_name}: {str(e)}")
                raise InvalidDataException(field_name, f"Validation error: {str(e)}")
    
    return True


def safe_get_object(model_class, **filters):
    """
    Safely get a single object with error handling
    
    Args:
        model_class: Django model class
        **filters: Filter kwargs
        
    Returns:
        Object or raises ResourceNotFoundException
    """
    try:
        return model_class.objects.get(**filters)
    except ObjectDoesNotExist:
        filter_str = ", ".join(f"{k}={v}" for k, v in filters.items())
        logger.warning(f"{model_class.__name__} not found with filters: {filter_str}")
        raise ResourceNotFoundException(model_class.__name__, str(filters))


def check_authorization(user, resource_owner, action="modify"):
    """
    Check if user has authorization to perform action on resource
    
    Args:
        user: User attempting action
        resource_owner: User who owns the resource
        action: Action being performed
        
    Raises:
        UnauthorizedAccessException if not authorized
    """
    if user != resource_owner and not user.is_staff:
        logger.warning(
            f"Unauthorized attempt by user {user.id} to {action} "
            f"resource owned by {resource_owner.id}"
        )
        raise UnauthorizedAccessException(action, "this resource")


def format_serializer_errors(errors):
    """
    Convert DRF serializer errors to a more readable format
    
    Args:
        errors: Serializer errors dictionary
        
    Returns:
        Formatted error dictionary
    """
    formatted = {}
    for field, messages in errors.items():
        if isinstance(messages, list):
            formatted[field] = messages[0] if messages else "Invalid value"
        else:
            formatted[field] = str(messages)
    return formatted
