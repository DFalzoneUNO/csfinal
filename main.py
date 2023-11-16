import sys
from tokenizer import Tokenizer, TokenError


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
            has "fries" ? "A drink to make it a combo" => combo-meal
        };
    @end-scene
    @end-module example-module
    """
    if len(sys.argv) >= 2:
        with open(sys.argv[1]) as file_handle:
            sample_text = file_handle.read()
    tokenizer = Tokenizer(sample_text)
    tokens = tokenizer.tokenize(debug_mode=True)
    print(f"===\nNumber of tokens: {len(tokens)}\nNumber of lines: {tokenizer.current_line}")    


if __name__ == "__main__":
    main()
