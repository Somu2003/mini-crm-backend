class AIService:
    def generate_message_suggestions(self, objective):
        return [
            f"Hi {{name}}, special offer for {objective}!",
            f"Hello {{name}}, don't miss out!",
            f"{{name}}, exclusive deal inside!"
        ]
