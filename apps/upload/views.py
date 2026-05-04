from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from minio.commonconfig import Tags
from django.core.cache import cache
from urllib.parse import urlparse
from minio.error import S3Error
from datetime import timedelta
from minio import Minio
import mimetypes
import time
import os


def get_minio_client():
    return Minio(
        endpoint=os.getenv("MINIO_ENDPOINT", "minio:9000"),
        access_key=os.getenv("MINIO_USER", "minio"),
        secret_key=os.getenv("MINIO_PASSWORD", "minio123"),
        secure=False
    )


@csrf_exempt
@permission_classes([IsAuthenticated])
def upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        file_obj = request.FILES["file"]
        file_name = file_obj.name
        full_path = request.POST.get("path", "").strip("/")
        time_seconds = request.POST.get("time")
        # Get authenticated user from request
        user_id = request.user.id if request.user.is_authenticated else None
        if not user_id:
            return JsonResponse({"error": "Foydalanuvchi topilmadi"}, status=403)
        if "/" not in full_path:
            return JsonResponse({"error": "Path formati noto'g'ri. Masalan: bucket/folder/fileName"}, status=400)
        bucket_name, object_path = full_path.split("/", 1)
        client = get_minio_client()
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        try:
            client.put_object(
                bucket_name,
                object_path,
                file_obj.file,
                length=file_obj.size,
                content_type=file_obj.content_type,

            )
            tags = Tags()
            tags["user_id"] = str(user_id) if user_id else "null"
            client.set_object_tags(
                bucket_name,
                object_path,
                tags
            )
            expires_seconds = int(time_seconds) if time_seconds else 3600
            expires_delta = timedelta(seconds=expires_seconds)

            presigned_url = client.presigned_get_object(
                bucket_name,
                object_path,
                expires=expires_delta
            )
            app_port = os.getenv("APP_PORT")
            if app_port:
                parsed = urlparse(presigned_url)
                presigned_url = presigned_url.replace(
                    f"{parsed.scheme}://{parsed.netloc}",
                    f"http://localhost:{app_port}/api"
                )
            return JsonResponse({
                "message": "Fayl yuklandi",
                "url": presigned_url,
                "expires_in_seconds": expires_seconds,
            })
        except S3Error as err:
            return JsonResponse({"error": str(err)}, status=500)

    return JsonResponse({"error": "Fayl yuborilmadi"}, status=400)


@csrf_exempt
def download_file(request, file_path):
    client = get_minio_client()
    expiry_str = request.GET.get("X-Amz-Expires")
    date_str = request.GET.get("X-Amz-Date")
    if expiry_str and date_str:
        try:
            expiry = int(expiry_str)
            url_time_struct = time.strptime(date_str, "%Y%m%dT%H%M%SZ")
            url_timestamp = int(time.mktime(url_time_struct))
            now_timestamp = int(time.time())

            if now_timestamp > url_timestamp + expiry:
                return JsonResponse({"error": "Vaqti tugagan"}, status=403)
        except Exception:
            return JsonResponse({"error": "URL vaqti noto‘g‘ri formatda"}, status=400)

    parsed_path = urlparse(file_path).path.lstrip("/")

    if "/" not in parsed_path:
        return JsonResponse(
            {"error": "Path noto'g'ri formatda. Masalan: bucket/folder/file.jpg"},
            status=400
        )

    bucket_name, object_path = parsed_path.split("/", 1)

    try:
        tags = client.get_object_tags(bucket_name, object_path)
        user_id_tag = tags.get("user_id", "unknown")

        data = client.get_object(bucket_name, object_path)

        mime_type, _ = mimetypes.guess_type(object_path)
        if mime_type is None:
            mime_type = "application/octet-stream"

        response = HttpResponse(data.read(), content_type=mime_type)
        response["Content-Disposition"] = f'attachment; filename="{os.path.basename(object_path)}"'
        response["X-User-Id-Tag"] = user_id_tag

        data.close()
        data.release_conn()

        return response

    except S3Error:
        return JsonResponse({"error": "Fayl topilmadi"}, status=404)
