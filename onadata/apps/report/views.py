from django.shortcuts import render
from onadata.apps.report.report_utils import get_multiple_options_count
from django.views.generic import View
from django.http import JsonResponse,

class GetSelectTypeCount(View):
    def get(self, request, **kwargs):
    	question_name = request.POST.get('question_name')
        response = get_multiple_options_count(pk, fsxf_id, question_name)
        status = 200 if response.get('status', 'ok') == "failed" else 500
        return JsonResponse(json.loads(response.get('result', {}), status=status)