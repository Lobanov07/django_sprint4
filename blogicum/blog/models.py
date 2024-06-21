from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class BaseModel(models.Model):

    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию.")

    created_at = models.DateTimeField(
        "Добавлено",
        auto_now=False,
        auto_now_add=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(
        "Заголовок",
        max_length=256)

    description = models.TextField("Описание")

    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text=("Идентификатор страницы для URL; разрешены символы "
                   "латиницы, цифры, дефис и подчёркивание."))

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(
        "Название места",
        max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BaseModel):

    title = models.CharField(
        "Заголовок",
        max_length=256)

    text = models.TextField("Текст")

    pub_date = models.DateTimeField(
        "Дата и время публикации",
        help_text=("Если установить дату и время в будущем "
                   "— можно делать отложенные публикации."))

    author = models.ForeignKey(
        User,
        verbose_name="Автор публикации",
        on_delete=models.CASCADE,
        related_name='posts')

    image = models.ImageField(
        verbose_name='Фото',
        upload_to='post_images/',
        blank=True,)

    location = models.ForeignKey(
        Location,
        verbose_name="Местоположение",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts')

    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts')

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ("pub_date", "title")

    def get_absolute_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title


class Comment(BaseModel):
    text = models.TextField(
        verbose_name="Текст комментария",)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,)

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",)

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"{self.author}: {self.text[:20]}"
