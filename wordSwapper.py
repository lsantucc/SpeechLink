def replace_words(sentence, word_map):
    """
    Replace words in a sentence based on a given word mapping.

    Args:
        sentence (str): The input sentence.
        word_map (dict): A dictionary where keys are words to be replaced 
                         and values are the words to replace them with.

    Returns:
        str: The modified sentence.
    """
    words = sentence.split()  # Split the sentence into individual words
    modified_words = [word_map.get(word, word) for word in words]  # Replace words if they exist in the map
    return ' '.join(modified_words)  # Join the modified words back into a sentence

# Example usage
if __name__ == "__main__":
    # Input sentence
    sentence = input("Enter a sentence: ")

    # Define the word mapping (e.g., replace "cat" with "dog")
    word_map = {}
    print("Enter the word mappings (type 'done' when finished):")
    while True:
        original_word = input("Word to replace: ")
        if original_word.lower() == 'done':
            break
        replacement_word = input(f"Replace '{original_word}' with: ")
        word_map[original_word] = replacement_word

    # Replace the words
    modified_sentence = replace_words(sentence, word_map)
    
    print("\nModified Sentence:")
    print(modified_sentence)
