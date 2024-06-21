from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Count
from blog.models import Post, Category, Comment
from django.http import Http404
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView)
from .forms import PostForm, CommentForm
from django.urls import reverse

POSTS_PER_PAGE = 10


def post_filter():

    return Post.objects.select_related(
        'author',
        'location',
        'category',
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


User = get_user_model()


class ProfileView(DetailView):
    model = Post
    template = "blog/profile.html"


class RedirectionPostMixin:
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class RedirectionProfileMixin:
    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostMixin:
    model = Post


class PostFormMixin(PostMixin):
    form_class = PostForm


class SetAutorMixin:
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class HomePage(ListView):
    model = Post

    template_name = 'blog/index.html'
    ordering = 'id'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        return post_filter()


class PostCreateView(
    LoginRequiredMixin,
    PostFormMixin,
    SetAutorMixin,
    RedirectionProfileMixin,
    CreateView,
):
    template_name = 'blog/create.html'


class ProfilePostListView(ListView):
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PER_PAGE
    model = Post

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return Post.objects.select_related(
            'author',
            'location',
            'category',
        ).filter(
            author=self.author
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class EditProfileView(LoginRequiredMixin, RedirectionProfileMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )

    def get_object(self, queryset=None):
        return self.request.user


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'author',
            'location',
            'category',
        )

    def get_object(self, queryset=None):

        post = super().get_object(queryset)
        if post.author != self.request.user and (
            post.is_published is False
            or post.category.is_published is False
            or post.pub_date > timezone.now()
        ):
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
            'author'
        )
        return context


class CommentMixin(RedirectionPostMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class CommentFormMixin(CommentMixin):
    form_class = CommentForm


class EditContentMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CommentFormMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            post_filter(),
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)


class CommentUpdateView(EditContentMixin, CommentFormMixin, UpdateView):
    pass


class CommentDeleteView(EditContentMixin, CommentMixin, DeleteView):
    pass


class PostIdCreateMixin:
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class PostUpdateView(
    EditContentMixin,
    PostFormMixin,
    PostIdCreateMixin,
    SetAutorMixin,
    RedirectionPostMixin,
    UpdateView,
):
    pass


class PostDeleteView(
    EditContentMixin,
    PostMixin,
    PostIdCreateMixin,
    RedirectionProfileMixin,
    DeleteView,
):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class CategoryListView(ListView):

    template_name = 'blog/category.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        return post_filter().filter(
            category__slug=self.kwargs['category_slug'],
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug'],
        )
        return context
