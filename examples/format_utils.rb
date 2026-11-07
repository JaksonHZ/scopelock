# Utilitário de formatação em Ruby
module FormatUtils
  def self.format_currency_brl(amount)
    "R$ #{'%.2f' % amount}"
  end

  def self.slugify_text(text)
    text.downcase.strip.gsub(/[^a-z0-9]+/, '-')
  end
end
