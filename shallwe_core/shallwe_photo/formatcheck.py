from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile


class ImageValidationError(ValueError):
    pass


class NotAnImageError(ImageValidationError):
    pass


class InvalidImageFormatError(ImageValidationError):
    pass


class ImageSizeExceedsLimitError(ImageValidationError):
    pass


class ImageDimensionsError(ImageValidationError):
    pass


class ImageNotSquareError(ImageValidationError):
    pass


def validate_is_image(uploaded_image: InMemoryUploadedFile):
    if not uploaded_image.content_type.startswith('image/'):
        raise NotAnImageError(
            f"Not an image: {uploaded_image.content_type}"
        )


def validate_image_size(uploaded_image: InMemoryUploadedFile):
    max_size_bytes = settings.ALLOWED_PHOTO_MAX_SIZE
    if uploaded_image.size > max_size_bytes:
        raise ImageSizeExceedsLimitError(
            f"File size exceeds the maximum allowed size of {max_size_bytes} bytes"
        )


def validate_image_format(uploaded_image: InMemoryUploadedFile):
    allowed_formats = tuple('image/' + format_ for format_ in settings.ALLOWED_PHOTO_FORMATS)
    if uploaded_image.content_type not in allowed_formats:
        raise InvalidImageFormatError(
            f"Invalid image format: {uploaded_image.content_type}. Allowed formats: {', '.join(allowed_formats)}"
        )


def validate_image_dimensions(image: Image):
    min_dimensions = settings.ALLOWED_PHOTO_MIN_DIMENSIONS
    max_dimensions = settings.ALLOWED_PHOTO_MAX_DIMENSIONS
    if image.size[0] < min_dimensions[0] or image.size[1] < min_dimensions[1]:
        raise ImageDimensionsError(
            f"Image dimensions should be at least {min_dimensions[0]}x{min_dimensions[1]} pixels"
        )
    if image.size[0] > max_dimensions[0] or image.size[1] > max_dimensions[1]:
        raise ImageDimensionsError(
            f"Image dimensions exceed the maximum allowed size of {max_dimensions[0]}x{max_dimensions[1]} pixels"
        )


def validate_image_square(image: Image):
    if image.size[0] != image.size[1]:
        raise ImageNotSquareError("Image must be a square")


def clean_image(uploaded_image):

    validate_is_image(uploaded_image)
    validate_image_size(uploaded_image)
    validate_image_format(uploaded_image)

    image = Image.open(uploaded_image)

    validate_image_dimensions(image)
    validate_image_square(image)

    return image
