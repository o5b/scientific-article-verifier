from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    """Information about article authors."""
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
        return f'{self.full_name}, {self.orcid}' if self.orcid else f'{self.full_name}'


class Article(models.Model):
    """Basic model for storing a scientific article and its metadata."""

    users = models.ManyToManyField(
        to=User,
        through='ArticleUser',
        related_name='articles',
        verbose_name=_("Users"),
        help_text=_("Users associated with this article")
        # blank=True,
    )

    title = models.TextField(
        verbose_name=_("Article Title")
    )

    authors = models.ManyToManyField(
        to=Author,
        through='ArticleAuthor',
        related_name='articles',
        verbose_name=_("Authors"),
        blank=True,
    )

    abstract = models.TextField(
        verbose_name=_("Abstract"),
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

    pdf_file = models.FileField(
        upload_to='articles_pdf/',
        verbose_name=_("PDF fail"),
        max_length=500,
        blank=True,
        null=True,
    )

    pdf_text = models.TextField(
        verbose_name=_("Text from PDF"),
        help_text=_("Text content of pdf file."),
        null=True,
        blank=True,
    )

    pdf_url = models.URLField(
        verbose_name=_("URL PDF"),
        max_length=2048,
        null=True,
        blank=True,
        help_text=_("PDF download link")
    )

    # --- Источник основной записи ---
    primary_source_api = models.CharField(
        verbose_name=_("Main Source API"),
        max_length=100,
        null=True,
        blank=True,
        help_text=_("The API from which the primary metadata for this post (title, abstract) was taken.")
    )

    # --- Метаданные публикации ---
    publication_date = models.DateField(
        verbose_name=_("Date of publication"),
        null=True,
        blank=True
    )

    journal_name = models.CharField(
        verbose_name=_("Name of the journal/source"),
        max_length=512,
        null=True,
        blank=True
    )

    # Можно добавить volume, issue, pages etc.
    # --- Unpaywall OA Info ---
    oa_status = models.CharField(
        verbose_name=_("Open Access Status"),
        max_length=50,
        null=True,
        blank=True,
        help_text=_("Open Access status from Unpaywall (e.g., gold, green, bronze, closed)")
    )

    best_oa_url = models.URLField(
        verbose_name=_("URL of the best OA version"),
        max_length=2048, # URL могут быть длинными
        null=True,
        blank=True,
        help_text=_("Link to the best OA version (HTML/landing) from Unpaywall")
    )

    best_oa_pdf_url = models.URLField(
        verbose_name=_("URL PDF of the best OA version"),
        max_length=2048,
        null=True,
        blank=True,
        help_text=_("Link to PDF of the best OA version from Unpaywall")
    )

    oa_license = models.CharField(
        verbose_name=_("OA version license"),
        max_length=100,
        null=True,
        blank=True,
        help_text=_("OA version license from Unpaywall (e.g., cc-by, cc-by-nc)")
    )

    is_user_initiated = models.BooleanField(
        verbose_name=_("Added by user directly"),
        default=False, # По умолчанию False. Будет True, только если пользователь сам инициировал добавление.
        db_index=True, # Индексируем для быстрого поиска основных статей пользователя
        help_text=_("True if this article was added directly by the user, not as a related link.")
    )

    created_at = models.DateTimeField(
        verbose_name=_("Date of creation"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Date of update"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("Scientific article")
        verbose_name_plural = _("Scientific articles")
        ordering = ['-updated_at', '-created_at']

    def __str__(self):
        return self.title[:100]


class ArticleAuthor(models.Model):
    """Intermediate model for the relationship between Article and Author."""
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
        verbose_name=_("Date of creation"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Date of update"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("Author associated with the article")
        verbose_name_plural = _("Authors associated with articles")
        unique_together = ('article', 'author') # Автор не может быть дважды в одной статье
        # constraints = [
        #     models.UniqueConstraint(fields=['article'], name='unique_author_per_article')
        # ]


class ArticleContent(models.Model):
    """Raw article content from various APIs and in various formats."""
    article = models.ForeignKey(
        Article,
        related_name='contents',
        on_delete=models.CASCADE,
        verbose_name=_("Article")
    )

    source_api_name = models.CharField(
        verbose_name=_("Source API Name"),
        max_length=100,
        help_text=_("Ex.: 'pubmed', 'crossref_api', 'arxiv_api'")
    )

    format_type = models.CharField(
        verbose_name=_("Format type"),
        max_length=50,
        help_text=_("Ex.: 'json_metadata', 'full_text_xml_pmc', 'xml_fulltext_jats', 'abstract_text', 'references_list_json'")
    )

    content = models.TextField( # Используем TextField; для JSON можно использовать JSONField, если СУБД поддерживает
        verbose_name=_("Content")
    )

    retrieved_at = models.DateTimeField(
        verbose_name=_("Date and time of upload"),
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.article.title[:30]}... - {self.source_api_name} ({self.format_type})"

    class Meta:
        verbose_name = _("Article content from the source")
        verbose_name_plural = _("Article content from sources")
        unique_together = ('article', 'source_api_name', 'format_type') # Для одной статьи, один тип контента от одного API


class ReferenceLink(models.Model):
    """A model for storing references within an article and their relationship to other articles in the database."""

    class StatusChoices(models.TextChoices):
        PENDING_DOI_INPUT = 'pending_doi_input', _('Waiting for input/DOI search')
        DOI_LOOKUP_IN_PROGRESS = 'doi_lookup_in_progress', _('Searching DOI for reference')
        DOI_PROVIDED_NEEDS_LOOKUP = 'doi_provided_needs_lookup', _('DOI found, waiting for article to be uploaded')
        ARTICLE_FETCH_IN_PROGRESS = 'article_fetch_in_progress', _('Loading article by DOI')
        ARTICLE_LINKED = 'article_linked', _('Article found and linked')
        ARTICLE_NOT_FOUND = 'article_not_found', _('Article not found by DOI')
        MANUAL_ENTRY = 'manual_entry', _('Data entered manually')
        MANUAL_METADATA_ONLY = 'manual_metadata_only', _('Metadata entered manually (no connection)')
        ERROR_DOI_LOOKUP = 'error_doi_lookup', _('Error while searching DOI')
        ERROR_ARTICLE_FETCH = 'error_article_fetch', _('Error loading article')
        ERROR_PROCESSING = 'error_processing', _('Error while processing')

    source_article = models.ForeignKey(
        Article,
        related_name='references_made',
        on_delete=models.CASCADE,
        verbose_name=_("Source article")
    )

    raw_reference_text = models.TextField(
        verbose_name=_("Original text of the reference"),
        null=True,
        blank=True,
        help_text=_("The link text as it appears in the original article.")
    )

    target_article_doi = models.CharField(
        verbose_name=_("DOI of the cited article"),
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text=_("DOI of the article being referenced. Can be entered/edited by the user.")
    )

    resolved_article = models.ForeignKey(
        Article,
        related_name='cited_by_references',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Related article in DB")
    )

    manual_data_json = models.JSONField(
        verbose_name=_("Manually entered data"),
        null=True,
        blank=True,
        help_text=_("JSON with metadata of the cited article if it is added manually (title, authors, year, etc.).")
    )

    status = models.CharField(
        verbose_name=_("Reference status"),
        max_length=50,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING_DOI_INPUT
    )

    log_messages = models.TextField(
        verbose_name=_("Processing logs"),
        null=True,
        blank=True,
        help_text=_("Messages about the search process, loading, errors.")
    )

    created_at = models.DateTimeField(
        verbose_name=_("Date of creation"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Date of update"),
        auto_now=True
    )

    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ['order'] # ordering = ['-created_at']
        verbose_name = _("Bibliographic reference")
        verbose_name_plural = _("Bibliographic references")

    def __str__(self):
        if self.resolved_article:
            return f"Reference from '{self.source_article.title[:20]}...' to '{self.resolved_article.title[:20]}...'"
        elif self.target_article_doi:
            return f"From '{self.source_article.title[:20]}...' to DOI: {self.target_article_doi}"
        return f"Reference ID {self.id} from '{self.source_article.title[:20]}...'"


class AnalyzedSegment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='analyzed_segments',
        verbose_name=_("Target article")
    )

    # Ключ секции, из которой взят сегмент (из article.structured_content или заголовок из other_sections)
    section_key = models.CharField(
        verbose_name=_("Section Key/Title"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("For example, introduction, methods, or a custom section header.")
    )

    segment_text = models.TextField(
        verbose_name=_("Segment text"),
        help_text=_("A user-selected or automatically extracted piece of text.")
    )

    # Ссылки, которые подтверждают/относятся к этому сегменту текста
    cited_references = models.ManyToManyField(
        ReferenceLink,
        related_name='supporting_segments',
        blank=True, # Сегмент может быть и без прямых ссылок
        verbose_name=_("Cited/Related References")
    )

    # Текстовое представление инлайн-цитат, найденных в segment_text (опционально, для справки)
    inline_citation_markers = models.JSONField(
        verbose_name=_("Inline quotation markers"),
        null=True,
        blank=True,
        default=list,
        help_text=_("List of text citation markers found in the segment, e.g. ['[1]', '(Smith 2023)']")
    )

    # Поля для будущего анализа LLM
    llm_analysis_notes = models.TextField(
        verbose_name=_("LLM Analysis Notes"),
        null=True,
        blank=True
    )

    llm_veracity_score = models.FloatField(
        verbose_name=_("Veracity score from LLM"),
        null=True,
        blank=True
    )

    llm_model_name =  models.CharField(
        verbose_name=_("Name of LLM model"),
        max_length=100,
        help_text=_("Ex.: 'gpt-4o-mini'"),
        null=True,
        blank=True,
    )

    prompt_used = models.TextField(
        verbose_name=_("Prompt used"),
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, # Если пользователя удалят, сегмент останется
        null=True,
        blank=True,     # Может быть создан системой или пользователем
        verbose_name=_("User who created/modified the segment")
    )

    created_at = models.DateTimeField(
        verbose_name=_("Date of creation"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("Analyzed text segment")
        verbose_name_plural = _("Analyzed text segments")
        ordering = ['article', 'created_at']
        # Можно добавить unique_together, если, например, текст сегмента в рамках одной статьи и секции должен быть уникальным
        # unique_together = ('article', 'section_key', 'segment_text_hash') # (потребует поля хеша)

    def __str__(self):
        section_info = f"Section: {self.section_key}" if self.section_key else "General text"
        return f"Segment from '{self.article.title[:30]}...' ({section_info}): '{self.segment_text[:50]}...'"


class ArticleUser(models.Model):
    """Intermediate model for the relationship between Article and User."""
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    structured_content = models.JSONField(
        verbose_name=_("Structured content"),
        null=True,
        blank=True,
        default=dict, # default=dict, чтобы можно было сразу добавлять ключи
        help_text=_("Contents of the article, divided into sections (Ex.: abstract, introduction, methods, results, discussion, conclusion)")
    )

    # --- Данные для LLM и ручного ввода ---
    cleaned_text_for_llm = models.TextField(
        verbose_name=_("Cleaned text for LLM"),
        null=True,
        blank=True,
        help_text=_("Full text of the article, cleaned and prepared for LLM analysis. Can be added manually.")
    )

    # --- Источник основной записи ---
    primary_source_api = models.CharField(
        verbose_name=_("Primary Source API"),
        max_length=100,
        null=True,
        blank=True,
        help_text=_("The API from which the primary metadata for this post (title, abstract) was taken.")
    )

    is_manually_added_full_text = models.BooleanField(
        verbose_name=_("Полный текст добавлен вручную"),
        default=False,
        help_text=_("Indicates whether the full text of the article was added manually by the user.")
    )

    created_at = models.DateTimeField(
        verbose_name=_("Date of creation"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Date of update"),
        auto_now=True
    )

    # order = models.PositiveIntegerField(
    #     verbose_name=_("Порядок"),
    #     default=0
    # )

    class Meta:
        verbose_name = _("User associated with the article")
        verbose_name_plural = _("Users associated with articles")
        unique_together = ('article', 'user') # Пользователь не может быть дважды связан со статьёй
        # constraints = [
        #     models.UniqueConstraint(fields=['article'], name='unique_author_per_article')
        # ]

    def regenerate_cleaned_text_from_structured(self):
        """
        Generates cleaned_text_for_llm from structured_content.
        Sections are added in a predefined order.
        """
        if not self.structured_content or not isinstance(self.structured_content, dict):
            # Если нет структурированного контента оставляем пустым
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
                    old_version = ArticleUser.objects.get(pk=self.pk)
                    if old_version.structured_content != self.structured_content or \
                        (not self.cleaned_text_for_llm and self.structured_content):
                            self.regenerate_cleaned_text_from_structured()
                except ArticleUser.DoesNotExist:
                    self.regenerate_cleaned_text_from_structured() # Для нового объекта
            else: # Новый объект
                self.regenerate_cleaned_text_from_structured()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'ArticleUser (article id: {self.article.id}, user id: {self.user.id})'
