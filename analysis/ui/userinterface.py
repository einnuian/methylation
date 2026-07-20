from processor.processor import Processor

class UserInterface:
    def __init__(self, processor:Processor):
        self.processor = processor

    def start(self):
        self.processor.process()
        for key, value in self.processor.targets.items():
            print("\n")
            print(f"--------{key}--------\n")
            print("Wells to omit:\n", value.ommited_wells)
            print("\n")
            print(f"Controls set for {key}: {value.controls}")
            print(f"Reference sample for {key}: {value.reference}")
        print("\n")