class FormatText:
    def __init__(self, raw_text: str):
        self.value = raw_text

    def _format(self):
        return self.value.strip().lower()
