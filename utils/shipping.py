class ShippingProvider:

    def validate_tracking_code(self, tracking_code):
        raise NotImplementedError

    def get_tracking_info(self, tracking_code):
        raise NotImplementedError

    def is_delivered(self, tracking_code):
        raise NotImplementedError