# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView
from . import models, views

urlpatterns = [
    path("routing-rules/", views.LBRoutingRuleListView.as_view(), name="lbroutingrule_list"),
    path("routing-rules/add/", views.LBRoutingRuleEditView.as_view(), name="lbroutingrule_add"),
    path(
        "routing-rules/delete/",
        views.LBRoutingRuleBulkDeleteView.as_view(),
        name="lbroutingrule_bulk_delete",
    ),
    path("routing-rules/<int:pk>/", views.LBRoutingRuleView.as_view(), name="lbroutingrule"),
    path(
        "routing-rules/<int:pk>/edit/",
        views.LBRoutingRuleEditView.as_view(),
        name="lbroutingrule_edit",
    ),
    path(
        "routing-rules/<int:pk>/delete/",
        views.LBRoutingRuleDeleteView.as_view(),
        name="lbroutingrule_delete",
    ),
    path(
        "routing-rules/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="lbroutingrule_changelog",
        kwargs={"model": models.LBRoutingRule},
    ),
    path(
        "routing-rules/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="lbroutingrule_journal",
        kwargs={"model": models.LBRoutingRule},
    ),
    path("acls/", views.LBAclListView.as_view(), name="lbacl_list"),
    path("acls/add/", views.LBAclEditView.as_view(), name="lbacl_add"),
    path("acls/delete/", views.LBAclBulkDeleteView.as_view(), name="lbacl_bulk_delete"),
    path("acls/<int:pk>/", views.LBAclView.as_view(), name="lbacl"),
    path("acls/<int:pk>/edit/", views.LBAclEditView.as_view(), name="lbacl_edit"),
    path("acls/<int:pk>/delete/", views.LBAclDeleteView.as_view(), name="lbacl_delete"),
    path(
        "acls/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="lbacl_changelog",
        kwargs={"model": models.LBAcl},
    ),
    path(
        "acls/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="lbacl_journal",
        kwargs={"model": models.LBAcl},
    ),
    path("listener-certificates/", views.LBListenerCertificateListView.as_view(), name="lblistenercertificate_list"),
    path("listener-certificates/add/", views.LBListenerCertificateEditView.as_view(), name="lblistenercertificate_add"),
    path(
        "listener-certificates/delete/",
        views.LBListenerCertificateBulkDeleteView.as_view(),
        name="lblistenercertificate_bulk_delete",
    ),
    path("listener-certificates/<int:pk>/", views.LBListenerCertificateView.as_view(), name="lblistenercertificate"),
    path(
        "listener-certificates/<int:pk>/edit/",
        views.LBListenerCertificateEditView.as_view(),
        name="lblistenercertificate_edit",
    ),
    path(
        "listener-certificates/<int:pk>/delete/",
        views.LBListenerCertificateDeleteView.as_view(),
        name="lblistenercertificate_delete",
    ),
    path(
        "listener-certificates/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="lblistenercertificate_changelog",
        kwargs={"model": models.LBListenerCertificate},
    ),
    path(
        "listener-certificates/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="lblistenercertificate_journal",
        kwargs={"model": models.LBListenerCertificate},
    ),
    path("member-ha/", views.LBMemberHAListView.as_view(), name="lbmemberha_list"),
    path("member-ha/add/", views.LBMemberHAEditView.as_view(), name="lbmemberha_add"),
    path(
        "member-ha/delete/",
        views.LBMemberHABulkDeleteView.as_view(),
        name="lbmemberha_bulk_delete",
    ),
    path("member-ha/<int:pk>/", views.LBMemberHAView.as_view(), name="lbmemberha"),
    path("member-ha/<int:pk>/edit/", views.LBMemberHAEditView.as_view(), name="lbmemberha_edit"),
    path(
        "member-ha/<int:pk>/delete/",
        views.LBMemberHADeleteView.as_view(),
        name="lbmemberha_delete",
    ),
    path(
        "member-ha/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="lbmemberha_changelog",
        kwargs={"model": models.LBMemberHA},
    ),
    path(
        "member-ha/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="lbmemberha_journal",
        kwargs={"model": models.LBMemberHA},
    ),
]
