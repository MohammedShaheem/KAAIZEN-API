from notification.models import UserDevice


class SaveTokenService:
    
    @staticmethod
    def save_device_token(user, token):
        device, _ = UserDevice.objects.update_or_create(
            fcm_token=token,
            defaults={"user": user},
        )

        return device