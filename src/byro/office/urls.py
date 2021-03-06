from django.conf.urls import include, url

from .views import accounts, dashboard, members, realtransactions, settings

office_urls = [
    url('^settings/registration$', settings.RegistrationConfigView.as_view(), name='settings.registration'),
    url('^settings$', settings.ConfigurationView.as_view(), name='settings.base'),
    url('^$', dashboard.DashboardView.as_view(), name='dashboard'),
    url(r'^members/typeahead', members.MemberListTypeaheadView.as_view(), name='members.typeahead'),
    url(r'^members/list', members.MemberListView.as_view(), name='members.list'),
    url(r'^members/add', members.MemberCreateView.as_view(), name='members.add'),
    url(r'^members/view/(?P<pk>\d+)/', include([
        url('data$', members.MemberDataView.as_view(), name='members.data'),
        url('finance$', members.MemberFinanceView.as_view(), name='members.finance'),
        url('$', members.MemberDashboardView.as_view(), name='members.dashboard'),
    ])),
    url('^realtransaction/list', realtransactions.RealTransactionListView.as_view(), name='realtransactions.list'),
    url('^accounts/$', accounts.AccountListView.as_view(), name='accounts.list'),
    url('^accounts/add$', accounts.AccountCreateView.as_view(), name='accounts.add'),
    url('^accounts/(?P<pk>\d+)/$', accounts.AccountDetailView.as_view(), name='accounts.detail'),
    url('^accounts/(?P<pk>\d+)/delete$', accounts.AccountDeleteView.as_view(), name='accounts.delete'),
]
