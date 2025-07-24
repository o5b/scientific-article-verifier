from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    """Модель для хранения информации об авторах статей."""
    full_name = models.CharField(
        verbose_name=_("Full Name"),
        max_length=255,
        # unique=True,
    )

    first_name = models.CharField(
        verbose_name=_('First Name'),
        max_length=50,
        blank=True,
    )

    middle_name = models.CharField(
        verbose_name=_('Middle Name'),
        max_length=50,
        blank=True,
    )

    last_name = models.CharField(
        verbose_name=_('Last Name'),
        max_length=50,
        blank=True,
    )

    # ORCID: Открытый идентификатор исследователя и участника
    orcid = models.CharField(
        verbose_name='ORCID',
        max_length=255,
        unique=True, # ORCID должен быть уникальным
        null=True, # Может отсутствовать
        blank=True,
        db_index=True, # Индексируем для быстрого поиска
        help_text=_('ORCID: Open Researcher and Contributor ID (Ex.: Stephen Hawking — https://orcid.org/0000-0002-9079-593X)'),
    )

    affiliation = models.JSONField(
        verbose_name=_('Affiliation'),
        blank=True,
        null=True
    )

    created = models.DateTimeField(
        verbose_name=_("Created"),
        auto_now_add=True
    )

    updated = models.DateTimeField(
        verbose_name=_("Updated"),
        auto_now=True
    )

    order = models.PositiveIntegerField(
        verbose_name=_('Order'),
        default=0,
    )

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")
        ordering = ['order']

    def __str__(self):
        # if self.orcid:
        return f'{self.full_name}, {self.orcid}' if self.orcid else f'{self.full_name}'
        # return f'{self.full_name}'


class Article(models.Model):
    """Основная модель для хранения научной статьи и ее метаданных."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь"),
        help_text=_("Пользователь, добавивший статью в систему")
    )

    title = models.TextField(   # TextField для очень длинных названий
        verbose_name=_("Название статьи")
    )

    authors = models.ManyToManyField(
        to=Author,
        through='ArticleAuthor', # Промежуточная модель для указания порядка авторов
        related_name='articles',
        verbose_name=_("Авторы"),
        blank=True,
    )

    abstract = models.TextField(
        verbose_name=_("Аннотация"),
        null=True,
        blank=True
    )

    # --- Идентификаторы ---
    doi = models.CharField(
        verbose_name=_("DOI"),
        max_length=255,
        unique=True, # DOI должен быть уникальным
        null=True, # Может отсутствовать на начальном этапе
        blank=True,
        db_index=True # Индексируем для быстрого поиска
    )

    pubmed_id = models.CharField(
        verbose_name=_("PubMed ID"),
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )

    pmc_id = models.CharField(
        verbose_name=_("PubMed Central (PMC) ID"),
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )

    # arxiv_id = models.CharField(_("arXiv ID"), max_length=50, unique=True, null=True, blank=True, db_index=True)
    arxiv_id = models.CharField(
        verbose_name=_("arXiv ID"),
        max_length=50,
        null=True,
        blank=True
    )
    # Можно добавить другие идентификаторы по мере необходимости (PМCID, etc.)

    # --- Данные для LLM и ручного ввода ---
    cleaned_text_for_llm = models.TextField(
        verbose_name=_("Очищенный текст для LLM"),
        null=True,
        blank=True,
        help_text=_("Полный текст статьи, очищенный и подготовленный для анализа LLM. Может быть добавлен вручную.")
    )

    is_manually_added_full_text = models.BooleanField(
        verbose_name=_("Полный текст добавлен вручную"),
        default=False,
        help_text=_("Указывает, был ли полный текст статьи добавлен пользователем вручную.")
    )

    pdf_file = models.FileField(
        upload_to='articles_pdf/',
        verbose_name=_("PDF файл"),
        max_length=500,
        blank=True,
        null=True,
    )

    pdf_text = models.TextField(
        verbose_name=_("Текст из PDF"),
        help_text=_("Текстовое содержимое pdf файла полученное из MarkItDown, MarkerPDF или др."),
        null=True,
        blank=True,
    )

    pdf_url = models.URLField(
        verbose_name=_("URL PDF"),
        max_length=2048,
        null=True,
        blank=True,
        help_text=_("Ссылка на скачивание PDF")
    )

    # --- Источник основной записи ---
    primary_source_api = models.CharField(
        verbose_name=_("API основного источника"),
        max_length=100,
        null=True,
        blank=True,
        help_text=_("API, из которого были взяты основные метаданные для этой записи (title, abstract).")
    )

    # --- Метаданные публикации ---
    publication_date = models.DateField(
        verbose_name=_("Дата публикации"),
        null=True,
        blank=True
    )

    journal_name = models.CharField(
        verbose_name=_("Название журнала/источника"),
        max_length=512,
        null=True,
        blank=True
    )

    # Можно добавить volume, issue, pages etc.
    # --- Unpaywall OA Info ---
    oa_status = models.CharField(
        verbose_name=_("Статус Open Access"),
        max_length=50,
        null=True,
        blank=True,
        help_text=_("Статус Open Access от Unpaywall (e.g., gold, green, bronze, closed)")
    )

    best_oa_url = models.URLField(
        verbose_name=_("URL лучшей OA версии"),
        max_length=2048, # URL могут быть длинными
        null=True,
        blank=True,
        help_text=_("Ссылка на лучшую OA версию (HTML/лендинг) от Unpaywall")
    )

    best_oa_pdf_url = models.URLField(
        verbose_name=_("URL PDF лучшей OA версии"),
        max_length=2048,
        null=True,
        blank=True,
        help_text=_("Ссылка на PDF лучшей OA версии от Unpaywall")
    )

    oa_license = models.CharField(
        verbose_name=_("Лицензия OA версии"),
        max_length=100,
        null=True,
        blank=True,
        help_text=_("Лицензия OA версии от Unpaywall (e.g., cc-by, cc-by-nc)")
    )

    is_user_initiated = models.BooleanField(
        verbose_name=_("Добавлено пользователем напрямую"),
        default=False, # По умолчанию False. Будет True, только если пользователь сам инициировал добавление.
        db_index=True, # Индексируем для быстрого поиска основных статей пользователя
        help_text=_("True, если эта статья была добавлена пользователем напрямую, а не как связанная ссылка.")
    )

    structured_content = models.JSONField(
        verbose_name=_("Структурированное содержимое"),
        null=True,
        blank=True,
        default=dict, # default=dict, чтобы можно было сразу добавлять ключи
        help_text=_("Содержимое статьи, разбитое по секциям (например, abstract, introduction, methods, results, discussion, conclusion)")
    )

    # --- Временные метки ---
    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("Научная статья")
        verbose_name_plural = _("Научные статьи")
        ordering = ['-updated_at', '-created_at']

    def regenerate_cleaned_text_from_structured(self):
        """
        Формирует cleaned_text_for_llm из structured_content.
        Секции добавляются в предопределенном порядке.
        """
        if not self.structured_content or not isinstance(self.structured_content, dict):
            # Если нет структурированного контента, используем абстракт (если есть) или оставляем пустым
            # self.cleaned_text_for_llm = self.abstract if self.abstract else ""
            return None
        # Если только 'title' и/или 'abstract' то не продолжаем
        structured_content_keys = list(self.structured_content.keys())
        for key in ['title', 'abstract']:
            if key in structured_content_keys:
                structured_content_keys.remove(key)
        if not structured_content_keys:
            return None

        ordered_keys = ['title', 'abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion']
        text_parts = []
        processed_keys = set()

        for key in ordered_keys:
            if self.structured_content.get(key):
                section_text = str(self.structured_content[key])
                if key == 'title':
                    title_marker = f"--- {key.upper()} ---"
                else:
                    title_marker = f"\n--- {key.upper()} ---"
                # Убираем дублирование заголовка, если он уже есть в тексте секции
                # if not section_text.strip().upper().startswith(title_marker):
                #    text_parts.append(title_marker)
                text_parts.append(title_marker)
                text_parts.append(section_text)
                processed_keys.add(key)

        # Добавляем "other_sections"
        other_sections_data = self.structured_content.get('other_sections')
        if isinstance(other_sections_data, list):
            for sec_item in other_sections_data:
                if isinstance(sec_item, dict):
                    title = sec_item.get('title', 'OTHER SECTION').upper()
                    text = sec_item.get('text', '')
                    if text:
                        text_parts.append(f"\n--- {title} ---")
                        text_parts.append(text)

        # Добавляем любые другие ключи из structured_content, которые не были обработаны
        # (кроме 'full_body_fallback', который мы используем ниже, если ничего другого нет)
        for key, value in self.structured_content.items():
            if key not in processed_keys and key not in ['other_sections', 'full_body_fallback'] and value:
                text_parts.append(f"\n--- {key.upper()} (CUSTOM) ---")
                text_parts.append(str(value))
                processed_keys.add(key)

        # if not text_parts and self.structured_content.get('full_body_fallback'):
        #     text_parts.append(self.structured_content['full_body_fallback'])

        self.cleaned_text_for_llm = "\n\n".join(filter(None, [tp.strip() for tp in text_parts])).strip()
        # if not self.cleaned_text_for_llm and self.abstract: # Если после всего текста нет, а абстракт есть
            # self.cleaned_text_for_llm = self.abstract

    def save(self, *args, **kwargs):
        # Автоматически регенерируем cleaned_text_for_llm, если structured_content изменился
        # или если cleaned_text_for_llm пуст, а structured_content есть.
        # Это можно сделать более избирательно, если отслеживать изменения structured_content.
        # Для простоты, пока будем делать это при каждом save, если structured_content есть.
        if self.structured_content:
            # Проверяем, изменилось ли structured_content (если объект уже в БД)
            if self.pk:
                try:
                    old_version = Article.objects.get(pk=self.pk)
                    if old_version.structured_content != self.structured_content or \
                        (not self.cleaned_text_for_llm and self.structured_content):
                            self.regenerate_cleaned_text_from_structured()
                except Article.DoesNotExist:
                    self.regenerate_cleaned_text_from_structured() # Для нового объекта
            else: # Новый объект
                self.regenerate_cleaned_text_from_structured()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title[:100] # Возвращаем первые 100 символов названия


class ArticleAuthor(models.Model):
    """Промежуточная модель для связи Article и Author."""
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE
    )

    sequence = models.CharField(
        verbose_name=_('Sequence'),
        max_length=50,
        help_text=_('Ex.: "first", "additional"'),
        blank=True,
    )

    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True
    )

    # order = models.PositiveIntegerField(
    #     verbose_name=_("Порядок"),
    #     default=0
    # )

    class Meta:
        verbose_name = _("Автора статьи")
        verbose_name_plural = _("Авторы статей")
        # ordering = ['order']
        unique_together = ('article', 'author') # Автор не может быть дважды в одной статье
        # constraints = [
        #     models.UniqueConstraint(fields=['article'], name='unique_author_per_article')
        # ]


class ArticleContent(models.Model):
    """Хранение "сырого" контента статьи из различных API и в различных форматах."""
    article = models.ForeignKey(
        Article,
        related_name='contents',
        on_delete=models.CASCADE,
        verbose_name=_("Статья")
    )

    source_api_name = models.CharField(
        verbose_name=_("Название API источника"),
        max_length=100,
        help_text=_("Например, 'pubmed', 'crossref_api', 'arxiv_api'")
    )

    format_type = models.CharField(
        verbose_name=_("Тип формата"),
        max_length=50,
        help_text=_("Например, 'json_metadata', 'full_text_xml_pmc', 'xml_fulltext_jats', 'abstract_text', 'references_list_json'")
    )

    content = models.TextField( # Используем TextField; для JSON можно использовать JSONField, если СУБД поддерживает
        verbose_name=_("Содержимое")
    )

    retrieved_at = models.DateTimeField(
        verbose_name=_("Дата и время загрузки"),
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.article.title[:30]}... - {self.source_api_name} ({self.format_type})"

    class Meta:
        verbose_name = _("Контент статьи из источника")
        verbose_name_plural = _("Контент статей из источников")
        unique_together = ('article', 'source_api_name', 'format_type') # Для одной статьи, один тип контента от одного API


class ReferenceLink(models.Model):
    """Модель для хранения ссылок (references) внутри статьи и их связи с другими статьями в БД."""

    # class StatusChoices(models.TextChoices):
    #     PENDING_DOI_INPUT = 'pending_doi_input', _('Ожидает ввода/поиска DOI')
    #     DOI_LOOKUP_IN_PROGRESS = 'doi_lookup_in_progress', _('Идет поиск DOI для ссылки')
    #     DOI_PROVIDED_NEEDS_LOOKUP = 'doi_provided_needs_lookup', _('DOI найден, ожидает загрузки статьи')
    #     ARTICLE_FETCH_IN_PROGRESS = 'article_fetch_in_progress', _('Идет загрузка статьи по DOI')
    #     ARTICLE_LINKED = 'article_linked', _('Статья найдена и связана')
    #     ARTICLE_NOT_FOUND = 'article_not_found', _('Статья не найдена по DOI')
    #     MANUAL_ENTRY = 'manual_entry', _('Данные введены вручную')
    #     MANUAL_METADATA_ONLY = 'manual_metadata_only', _('Метаданные введены вручную (без связи)')
    #     ERROR_DOI_LOOKUP = 'error_doi_lookup', _('Ошибка при поиске DOI')
    #     ERROR_ARTICLE_FETCH = 'error_article_fetch', _('Ошибка при загрузке статьи')
    #     ERROR_PROCESSING = 'error_processing', _('Ошибка при обработке')
        
    class StatusChoices(models.TextChoices):
        PENDING_DOI_INPUT = 'pending_doi_input', _('Awaiting DOI input or lookup')
        DOI_LOOKUP_IN_PROGRESS = 'doi_lookup_in_progress', _('Searching for DOI')
        DOI_PROVIDED_NEEDS_LOOKUP = 'doi_provided_needs_lookup', _('DOI provided, awaiting article fetch')
        ARTICLE_FETCH_IN_PROGRESS = 'article_fetch_in_progress', _('Fetching article by DOI')
        ARTICLE_LINKED = 'article_linked', _('Article found and linked')
        ARTICLE_NOT_FOUND = 'article_not_found', _('Article not found by DOI')
        MANUAL_ENTRY = 'manual_entry', _('Manually entered data')
        MANUAL_METADATA_ONLY = 'manual_metadata_only', _('Manually entered metadata (not linked)')
        ERROR_DOI_LOOKUP = 'error_doi_lookup', _('Error during DOI lookup')
        ERROR_ARTICLE_FETCH = 'error_article_fetch', _('Error fetching article')
        ERROR_PROCESSING = 'error_processing', _('Processing error')

    source_article = models.ForeignKey(
        Article,
        related_name='references_made',
        on_delete=models.CASCADE,
        verbose_name=_("Исходная статья")
    )

    raw_reference_text = models.TextField(
        verbose_name=_("Исходный текст ссылки"),
        null=True,
        blank=True,
        help_text=_("Текст ссылки, как он представлен в исходной статье.")
    )

    target_article_doi = models.CharField(
        verbose_name=_("DOI цитируемой статьи"),
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text=_("DOI статьи, на которую ссылаются. Может быть введен/отредактирован пользователем.")
    )

    resolved_article = models.ForeignKey(
        Article,
        related_name='cited_by_references',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Связанная статья в БД")
    )

    manual_data_json = models.JSONField(
        verbose_name=_("Данные, введенные вручную"),
        null=True,
        blank=True,
        help_text=_("JSON с метаданными цитируемой статьи, если она добавляется вручную (title, authors, year, etc.).")
    )

    status = models.CharField(
        verbose_name=_("Статус ссылки"),
        max_length=50, # Убедитесь, что длина достаточна для новых значений
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING_DOI_INPUT
    )

    log_messages = models.TextField(
        verbose_name=_("Логи обработки"),
        null=True,
        blank=True,
        help_text=_("Сообщения о процессе поиска, загрузки, ошибках.")
    )

    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True
    )

    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ['order'] # ordering = ['-created_at']
        verbose_name = _("Библиографическая ссылка")
        verbose_name_plural = _("Библиографические ссылки")

    def __str__(self):
        if self.resolved_article:
            return f"Ссылка из '{self.source_article.title[:20]}...' на '{self.resolved_article.title[:20]}...'"
        elif self.target_article_doi:
            return f"Из '{self.source_article.title[:20]}...' на DOI: {self.target_article_doi}"
        return f"Ссылка ID {self.id} из '{self.source_article.title[:20]}...'"


class AnalyzedSegment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='analyzed_segments',
        verbose_name=_("Целевая статья")
    )

    # Ключ секции, из которой взят сегмент (из article.structured_content или заголовок из other_sections)
    section_key = models.CharField(
        verbose_name=_("Ключ/заголовок секции"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Например, introduction, methods, или заголовок пользовательской секции.")
    )

    segment_text = models.TextField(
        verbose_name=_("Текст сегмента"),
        help_text=_("Выделенный пользователем или автоматически извлеченный фрагмент текста.")
    )

    # Ссылки, которые подтверждают/относятся к этому сегменту текста
    cited_references = models.ManyToManyField(
        ReferenceLink,
        related_name='supporting_segments',
        blank=True, # Сегмент может быть и без прямых ссылок
        verbose_name=_("Цитируемые/связанные ссылки")
    )

    # Текстовое представление инлайн-цитат, найденных в segment_text (опционально, для справки)
    inline_citation_markers = models.JSONField(
        verbose_name=_("Маркеры инлайн-цитат"),
        null=True,
        blank=True,
        default=list,
        help_text=_("Список текстовых маркеров цитирования, найденных в сегменте, например, ['[1]', '(Smith 2023)']")
    )

    # Поля для будущего анализа LLM
    llm_analysis_notes = models.TextField(
        verbose_name=_("Заметки анализа LLM"),
        null=True,
        blank=True
    )

    llm_veracity_score = models.FloatField(
        verbose_name=_("Оценка достоверности LLM"),
        null=True,
        blank=True
    )

    llm_model_name =  models.CharField(
        verbose_name=_("Название LLM модели"),
        max_length=100,
        help_text=_("Например: 'gpt-4o-mini'"),
        null=True,
        blank=True,
    )

    prompt_used = models.TextField(
        verbose_name=_("Использованный промпт"),
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, # Если пользователя удалят, сегмент останется
        null=True,
        blank=True,     # Может быть создан системой или пользователем
        verbose_name=_("Пользователь, создавший/изменивший сегмент")
    )

    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("Анализируемый сегмент текста")
        verbose_name_plural = _("Анализируемые сегменты текста")
        ordering = ['article', 'created_at']
        # Можно добавить unique_together, если, например, текст сегмента в рамках одной статьи и секции должен быть уникальным
        # unique_together = ('article', 'section_key', 'segment_text_hash') # (потребует поля хеша)

    def __str__(self):
        section_info = f"Секция: {self.section_key}" if self.section_key else "Общий текст"
        return f"Сегмент из '{self.article.title[:30]}...' ({section_info}): '{self.segment_text[:50]}...'"
