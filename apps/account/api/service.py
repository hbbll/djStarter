from apps.account.models import CustomUser
from django.core.cache import cache
from django.contrib.auth.hashers import check_password, make_password
import os
from minio.error import S3Error
from minio.commonconfig import Tags
from minio import Minio


class RoleService:
    @staticmethod
    def update_users(role):

        users = CustomUser.objects.filter(role=role)
        for user in users:
            if user.auth_token:
                token = str(user.auth_token)
                cache.delete(token)

        print(f"{users.count()} foydalanuvchining ma'lumotlari yangilandi.")


class UserService:
    @staticmethod
    def get_user_by_token(token):
        from django.core.cache import cache

        user_data = cache.get(str(token))

        if user_data:
            return {"success": True, "data": user_data}

        return {
            "success": False,
            "message": "Foydalanuvchi topilmadi yoki token eskirgan.",
        }

    @staticmethod
    def save_user(validated_data, user):
        old_password = validated_data.get("old_password")
        new_password = validated_data.get("new_password")
        new_password_confirm = validated_data.get("new_password_confirm")

        if old_password or new_password or new_password_confirm:
            if not old_password or not check_password(old_password, user.password):
                return {"success": False, "message": "Eski parol noto‘g‘ri"}
            if new_password != new_password_confirm:
                return {"success": False, "message": "Yangi parollar mos emas"}
            user.password = make_password(new_password)

        for key, value in validated_data.items():
            if key not in [
                "old_password",
                "new_password",
                "new_password_confirm",
                "image",
            ]:
                setattr(user, key, value)

        image = validated_data.get("image")
        if image:
            user.image = image

        user.save()

        return {
            "success": True,
            "message": "Foydalanuvchi ma'lumotlari muvaffaqiyatli yangilandi",
        }


def get_minio_client():
    return Minio(
        endpoint=os.getenv("MINIO_ENDPOINT", "minio:9000"),
        access_key=os.getenv("MINIO_USER", "minio"),
        secret_key=os.getenv("MINIO_PASSWORD", "minio123"),
        secure=False
    )


def upload_user_avatar(user_id, avatar):
    ext = os.path.splitext(avatar.name)[1].lower()
    bucket_name = os.getenv("MINIO_BUCKET_NAME", "default")
    object_path = f"{user_id}{ext}"
    client = get_minio_client()

    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)

    try:
        client.put_object(
            bucket_name,
            object_path,
            avatar.file,
            length=avatar.size,
            content_type=avatar.content_type,
        )
        tags = Tags()
        tags["user_id"] = str(user_id) if user_id else "null"
        client.set_object_tags(bucket_name, object_path, tags)

        app_port = os.getenv("APP_PORT")
        B_NAME = os.getenv("MINIO_BUCKET_NAME")
        url = f"http://localhost:{app_port}/auth/{B_NAME}/{object_path}"

        return {"success": True, "url": url}

    except S3Error as err:
        return {"success": False, "error": str(err)}
