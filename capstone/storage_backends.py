from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'media' # Puts all uploaded files inside the media/ folder in my S3 bucket.
    file_overwrite = False #  Prevents overwriting files with the same name
    default_acl = None  # to stop using ACLs