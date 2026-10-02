class PaymentGateway:
    def get_payment_url(self, authority):
        raise NotImplementedError

    def request_payment(self, amount, callback_url):
        raise NotImplementedError

    def verify_payment(self, authority, amount):
        raise NotImplementedError