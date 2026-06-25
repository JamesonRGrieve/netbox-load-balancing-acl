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
