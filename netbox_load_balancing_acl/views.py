# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.views import generic
from . import filtersets, forms, models, tables


class LBRoutingRuleView(generic.ObjectView):
    queryset = models.LBRoutingRule.objects.all()


class LBRoutingRuleListView(generic.ObjectListView):
    queryset = models.LBRoutingRule.objects.all()
    table = tables.LBRoutingRuleTable
    filterset = filtersets.LBRoutingRuleFilterSet
    filterset_form = forms.LBRoutingRuleFilterForm


class LBRoutingRuleEditView(generic.ObjectEditView):
    queryset = models.LBRoutingRule.objects.all()
    form = forms.LBRoutingRuleForm


class LBRoutingRuleDeleteView(generic.ObjectDeleteView):
    queryset = models.LBRoutingRule.objects.all()


class LBRoutingRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = models.LBRoutingRule.objects.all()
    table = tables.LBRoutingRuleTable


class LBAclView(generic.ObjectView):
    queryset = models.LBAcl.objects.all()


class LBAclListView(generic.ObjectListView):
    queryset = models.LBAcl.objects.all()
    table = tables.LBAclTable
    filterset = filtersets.LBAclFilterSet
    filterset_form = forms.LBAclFilterForm


class LBAclEditView(generic.ObjectEditView):
    queryset = models.LBAcl.objects.all()
    form = forms.LBAclForm


class LBAclDeleteView(generic.ObjectDeleteView):
    queryset = models.LBAcl.objects.all()


class LBAclBulkDeleteView(generic.BulkDeleteView):
    queryset = models.LBAcl.objects.all()
    table = tables.LBAclTable


class LBListenerCertificateView(generic.ObjectView):
    queryset = models.LBListenerCertificate.objects.all()


class LBListenerCertificateListView(generic.ObjectListView):
    queryset = models.LBListenerCertificate.objects.all()
    table = tables.LBListenerCertificateTable
    filterset = filtersets.LBListenerCertificateFilterSet
    filterset_form = forms.LBListenerCertificateFilterForm


class LBListenerCertificateEditView(generic.ObjectEditView):
    queryset = models.LBListenerCertificate.objects.all()
    form = forms.LBListenerCertificateForm


class LBListenerCertificateDeleteView(generic.ObjectDeleteView):
    queryset = models.LBListenerCertificate.objects.all()


class LBListenerCertificateBulkDeleteView(generic.BulkDeleteView):
    queryset = models.LBListenerCertificate.objects.all()
    table = tables.LBListenerCertificateTable


class LBMemberHAView(generic.ObjectView):
    queryset = models.LBMemberHA.objects.all()


class LBMemberHAListView(generic.ObjectListView):
    queryset = models.LBMemberHA.objects.all()
    table = tables.LBMemberHATable
    filterset = filtersets.LBMemberHAFilterSet
    filterset_form = forms.LBMemberHAFilterForm


class LBMemberHAEditView(generic.ObjectEditView):
    queryset = models.LBMemberHA.objects.all()
    form = forms.LBMemberHAForm


class LBMemberHADeleteView(generic.ObjectDeleteView):
    queryset = models.LBMemberHA.objects.all()


class LBMemberHABulkDeleteView(generic.BulkDeleteView):
    queryset = models.LBMemberHA.objects.all()
    table = tables.LBMemberHATable
