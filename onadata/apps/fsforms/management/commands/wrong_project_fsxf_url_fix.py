from django.core.management.base import BaseCommand, CommandError

from onadata.apps.fsforms.models import FInstance


class Command(BaseCommand):
    help = 'Fix project form id worng in url'

    def handle(self, *args, **options):
        site_ids = [85886, 858830, 85900, 85901, 85785, 85882, 85885]
        sent_project_form_id = 863881
        original_project_form_id = 1639571
        finstances = FInstance.objects.filter(project_fxf=sent_project_form_id, site__in=site_ids)
        for fi in finstances:
            if fi.project_fxf.xf.id_string != fi.instance.survey_type.slug:
                self.stdout.write('Faulty   .. "%s"' % str(fi.instance.id))
            else:
                self.stdout.write('ok   .. "%s"' % str(fi.instance.id))