from api.portuguese_converter import transform_text

def test_transformations():
    # Test cases with expected transformations
    test_cases = [
        ('muito louco', 'muintu loucu'),
        ('olho', 'ôli'),  # noun form
        ('eu olho', 'eu olho'),  # verb form
        ('estou', 'tô'),
        ('escola', 'iscola'),
        ('mentira', 'mintira'),
    ]
    
    for input_text, expected in test_cases:
        result = transform_text(input_text)
        print(f"\nInput: {input_text}")
        print(f"Output: {result['after']}")
        print(f"Explanations: {result['explanations']}")
        print(f"Combinations: {result['combinations']}")
        assert result['after'] == expected, f"Expected '{expected}' but got '{result['after']}'"

if __name__ == '__main__':
    test_transformations()
