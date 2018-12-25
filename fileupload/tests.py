from django.test import TestCase
from fileupload.tasks import DocumentTask
from fileupload.models import Document
from authentitcation.models import User

class CeleryTest(TestCase):
    POSTGRES_DB_CONFIG = {
        "db_type": "PostgreSQL",
        "db_username": "postgres",
        "db_password": "postgres",
        "db_host": "postgres",
        "db_port": 5432,
        "db_sid": "not applicable",
        "db_name": "simple"
    }

    def testUploadCSVFileInPostgres(self):
        user = User.objects.create_user("our_newfag", "email@email.com")
        # task = DocumentTask()
        