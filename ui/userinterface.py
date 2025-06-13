from processor.processor import Processor

class UserInterface:
    def __init__(self, processor:Processor):
        self.processor = processor

    def start(self):
        self.processor.process()
        for key, value in self.processor.omitted_wells.items():
            print("\nWells to omit for target:")
            print(f"--------{key}--------\n", value)
            controls = self.processor.controls[key]
            reference = self.processor.reference[key]
            print(f"Controls set for {key}: {controls}")
            print(f"Reference sample for {key}: {reference}")
            print("\n")