from __future__ import unicode_literals
import json
from rest_framework import serializers
from onadata.apps.report.models import ReportDashboard
from rest_framework.exceptions import ValidationError

class ReportSerializer(serializers.ModelSerializer):
    dashboardData = serializers.JSONField(binary=False)
    project = serializers.PrimaryKeyRelatedField(read_only=True)
    pk = serializers.ReadOnlyField()
    class Meta:
        model = ReportDashboard
        fields = ('dashboardData', 'project', 'pk')

    def update(self, instance, validated_data):
        print "here"
        dashboardData = validated_data.pop('dashboardData') if 'dashboardData' in validated_data else None
        try:
            instance.dashboardData = json.loads(dashboardData)
            instance.save()
        
        except Exception as e:
            raise ValidationError("Got error on: {}".format(e))

        return instance





