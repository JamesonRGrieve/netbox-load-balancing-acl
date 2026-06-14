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
