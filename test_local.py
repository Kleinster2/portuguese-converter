from api.portuguese_converter import transform_text

def test_vowel_combinations():
    # Test 'da Ana'
    result = transform_text('da Ana')
    print(f"Result for 'da Ana': {result}")
    assert result == 'dAna'

if __name__ == '__main__':
    test_vowel_combinations()
