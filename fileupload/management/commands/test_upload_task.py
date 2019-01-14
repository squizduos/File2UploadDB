from django.core.management.base import BaseCommand

from fileupload.tasks import DocumentTask


class Command(BaseCommand):
    help = 'Tests some file'

    def add_arguments(self, parser):
        parser.add_argument('document_id', nargs='+', type=int)

    def handle(self, *args, **options):
        task = DocumentTask()
        for document_id in options['document_id']:
            task_run = task.delay(document_id)
            print(task_run.task_id)
