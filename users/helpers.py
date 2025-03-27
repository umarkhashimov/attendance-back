from django.contrib.contenttypes.models import ContentType

from .models import LogAdminActionsModel

def record_action(action_number, user, content_type=None, object_id=None, action_message=None):

    content_type_instance = ContentType.objects.get_for_model(content_type) if content_type else None

    log = LogAdminActionsModel.objects.create(action_number=action_number,
                                        user=user,
                                        content_type=content_type_instance,
                                        object_id=object_id,
                                        message=action_message)

    return log