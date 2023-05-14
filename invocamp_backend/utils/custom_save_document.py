# import default_storage
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.core.files.storage import default_storage
import uuid


def save_document(serializer, instance, subdirectory):
  file = serializer.validated_data.get(subdirectory)
  if file is not None:
    # Remove the existing file
    if getattr(instance, subdirectory):
      default_storage.delete(getattr(instance, subdirectory).name)
    # Save the new file
    ext_name = file.name.split('.')[-1]
    uuid_name = uuid.uuid4().hex

    filename = f"{subdirectory}/{uuid_name}-{subdirectory}.{ext_name}"
    file_path = default_storage.save(filename, ContentFile(file.read()))
    setattr(instance, subdirectory, file_path)
  return instance
