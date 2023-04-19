class Locale:
    def get_attr(self, attr_name: str, is_plural: bool = False):
        try:
            return getattr(self, f"_{attr_name}") + ("s" if is_plural else "")
        except AttributeError:
            raise AttributeError(f"Attribute '{attr_name}' not found")
