from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Post, Author, Category, User
from datetime import datetime
from .filters import PostFilter
from .forms import PostForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.template.loader import render_to_string


class PostList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['value1'] = None
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['categories'] = Category.objects.all()
        context['authors'] = Author.objects.all()
        context['form'] = PostForm()
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'


class PostSearch(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'search'
    queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['value1'] = None
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


# дженерик для добавления объекта
class PostAdd(PermissionRequiredMixin, CreateView):
    model = Post
    template_name = 'add.html'
    context_object_name = 'add'
    queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 10
    form_class = PostForm  # добавляем форм класс, чтобы получать доступ к форме через метод POST
    permission_required = ('news.add_post',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['value1'] = None
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['categories'] = Category.objects.all()
        context['authors'] = Author.objects.all()
        context['form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса

        if form.is_valid():  # если пользователь ввёл всё правильно и нигде не ошибся, то сохраняем новый товар
            form.save()

        return super().get(request, *args, **kwargs)


# дженерик для редактирования объекта
class PostUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = 'add.html'
    form_class = PostForm
    permission_required = ('news.change_post',)

# метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


# дженерик для удаления товара
class PostDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'post_delete.html'
    queryset = Post.objects.all
    success_url = '/news/'
    permission_required = ('news.delete_post',)


    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    @method_decorator(login_required, name='dispatch')
    class ProtectedView(TemplateView):
        template_name = 'protected_page.html'

    @login_required
    def add_subscribe(request, **kwargs):
        pk = request.GET.get('pk', )
        print('Пользователь', request.user, 'добавлен в подписчики категории:', Category.objects.get(pk=pk))
        Category.objects.get(pk=pk).subscribers.add(request.user)
        return redirect('/news/')







