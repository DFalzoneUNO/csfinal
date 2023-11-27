import sys
from tokenizer import Tokenizer
from narrate_parser import NarrateParser


def main():
    sample_text = """
    @module example-module:
    @scene example-scene:
        flavortext {
            "This is an example scene for testing purposes."
        };
        # This is a comment.
        # This is another comment!
        get "A yummy exampleburger";
        select {
            "Fires with that" => @file("./typo-mischief.nar")::arson-typo,
            has no "fries" ? "Fries with that" => yummy-fries,
            has "fries" ? "A drink to make it a combo" => @file("./fastfood.nar")::drink-combo
        };
    @end-scene
    @end-module example-module
    """
    if len(sys.argv) >= 2:
        with open(sys.argv[1]) as file_handle:
            sample_text = file_handle.read()
    tokenizer = Tokenizer(sample_text)
    parser = NarrateParser(tokenizer)
    ast = parser.parse_file()
    print(str(ast))   


if __name__ == "__main__":
    main()
