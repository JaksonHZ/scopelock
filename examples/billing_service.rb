# Agente duplicando o método em Ruby
class BillingService
  def format_currency(amount)
    "R$ #{'%.2f' % amount}"
  end
end
