__table_args__ = (
    Index("idx_ui_user", "user_id"),
    Index("idx_ui_article", "article_id"),
    Index("idx_ui_user_article", "user_id", "article_id"),
)