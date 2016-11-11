# -*- coding: utf-8 -*-
import json
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.forms.models import model_to_dict
from django.http import request, Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from board.models import Phone
from board.utils import parse_int
from news.forms import NewsForm, CommentForm, BlackPostForm
from news.models import News, NewsCategory, BlackList, BlackListComment
from personal.models import UserData, PaidService


class NewsList(ListView):
    model = News
    paginate_by = 10
    # queryset = News.objects.all().order_by('-creation_date')

    # @method_decorator(login_required)
    # def dispatch(self, request, *args, **kwargs):
    #     """
    #     Декорируем диспетчер функцией login_required, чтобы запретить просмотр отображения неавторизованными
    #     пользователями
    #     """
    #     return super(NewsCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(NewsList, self).get_context_data(**kwargs)
        # Add in the publisher
        context['category_title'] = NewsCategory.objects.get(slug=self.request.path[1:])
        context['some_important_news'] = News.objects.get(id=622)
        # context['some_importantnews'] = 'just a text'
        return context

    def get_queryset(self):
        """
        Список наших объектов будет состоять лишь из приватных и не удаленных статей
        """
        slug_kohana = self.request.path
        return News.objects.filter(category__slug=slug_kohana[1:]).order_by('-creation_date')
        # return News.objects.all().order_by('-creation_date')


class NewsCreate(CreateView):
    model = News
    form_class = NewsForm

    def form_valid(self, form):
        # Мы используем ModelForm, а его метод save() возвращает инстанс
        # модели, связанный с формой. Аргумент commit=False говорит о том, что
        # записывать модель в базу рановато.
        instance = form.save(commit=False)

        # Теперь, когда у нас есть несохранённая модель, можно ей чего-нибудь
        # накрутить. Например, заполнить внешний ключ на auth.User. У нас же
        # блог, а не анонимный имижборд, правда?
        instance.author = self.request.user

        # А теперь можно сохранить в базу
        instance.save()

        return redirect(instance.get_absolute_url())
    # def get_object(self):
    #     """
    #     Для неавторизованного пользователя возвращает 404 ошибку
    #     Конечно мы можем как и в предыдущем примере использовать декоратор login_required
    #     """
    #     object = super(NewsCreate, self).get_object()
    #     if not self.request.user.is_authenticated():
    #         raise Http404
    #     return object


class NewsUpdate(UpdateView):
    model = News
    form_class = NewsForm


class NewsDetail(DetailView):
    model = News


class NewsDelete(DeleteView):
    model = News
    success_url = reverse_lazy('news-list')


class Oplata(TemplateView):
    template_name = 'personal_payment.html'
    
    def get_context_data(self, **kwargs):
        context = super(Oplata, self).get_context_data(**kwargs)
        context['available_bases'] = PaidService.objects.filter(name__startswith='base_')
        return context
        
        
class BlackListList(ListView):
    model = BlackList
    queryset = BlackList.objects.all().order_by('-post_date').prefetch_related(
        'phone', 'blacklistcomment_set')
    template_name = 'news/black_list.html'
    paginate_by = 10
    
    
class BlackListCreate(CreateView):
    form_class = BlackPostForm
    template_name = 'news/black_list_form.html'
    success_url = '/black_list'
    
    def form_valid(self, form):
        str_phones = self.request.POST['phone'].split(',')
        instance = form.save(commit=False)
        instance.author = self.request.user
        instance.save()
        print instance
        for str_phone in str_phones:
            phone = parse_int(str_phone)
            if len(str(phone)) == 9:
                phone_obj, created = Phone.objects.get_or_create(phone=phone)
                print phone_obj.phone
                phone_obj.agent = 5
                phone_obj.save()
                instance.phone.add(phone_obj)
        return redirect('/black_list')


class BlackListDetail(DetailView):
    model = BlackList
    template_name = "news/black_list_detail.html"

   
def add_black_comment(request):
    if request.is_ajax() and request.method == 'POST':
        if request.POST.get('text', None):
            blc = BlackListComment.objects.create(
                author=request.user,
                post_id=request.POST['post_id'],
                text=request.POST['text'])
            return render(request, 'news/black_comment.html', {'comment': blc})


def del_black_comment(request):
    if request.is_ajax() and request.method == "POST" and request.user.is_admin:
        comment = BlackListComment.objects.get(id=request.POST['id'])
        comment.delete()
        return HttpResponse('done')