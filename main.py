from ui.userinterface import UserInterface
from ui.browsefiles import Browser
from datamanagement.da_parser import DAParser
from processor.processor import Processor

def main():

    # let user browse files and get file path
    browser = Browser()
    filepath = browser.file_path

    # Create a parser with the given filepath
    parser = DAParser(filepath)

    # Create a processor with the parser
    processor = Processor(parser)

    # run the application
    ui = UserInterface(processor)
    ui.start()


if __name__ == "__main__":
    main()