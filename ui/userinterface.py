from processor.processor import Processor

class UserInterface:
    def __init__(self, processor:Processor):
        self.processor = processor

    def start(self):
        wells_to_omit = self.processor.process()
        for key, value in wells_to_omit.items():
            print(f"--------{key}--------\n", value)