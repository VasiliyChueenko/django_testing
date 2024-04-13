from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

import pytest


@pytest.mark.django_db
def test_news_count(client, list_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_comments_order(client, news, list_comments):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    sorted_comments = sorted(all_comments, key=lambda x: x.id)
    for i in range(1, len(sorted_comments)):
        assert sorted_comments[i - 1].created < sorted_comments[i].created


@pytest.mark.django_db
def test_comments_order(client, news, list_comments):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    sorted_comments = sorted(all_comments, key=lambda x: x.id)
    for i in range(1, len(sorted_comments)):
        assert sorted_comments[i - 1].id < sorted_comments[i].id


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
@pytest.mark.django_db
def test_anonymous_client_has_no_form(parametrized_client, status, comment):
    url = reverse('news:detail', args=(comment.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is status
    if status:
        form = response.context['form']
        assert isinstance(form, CommentForm)
