import random

# Original code snippet
original_snippet_concatenation = '("....." + a * b + ".....")'
original_snippet_interpolation = '(".....%d.....%d...", a * b, c)' # c-style
original_snippet_others = '(".....{a * b}.....{c}...")' # others 

# Error types
error_types_concatenation = [
        lambda s: s.replace('*', '/'),  
        lambda s: s.replace('+', '-'),  # modify this 
        lambda s: s.replace('+ "', ''),
        lambda s: s.replace('" +', ''),  
        lambda s: s.replace('+ "....."', '"'),  
        lambda s: s.replace('....."', '"'),  
        lambda s: s.replace('a * b', 'a * '),  
        lambda s: s.replace('a * b', '* b'),
        lambda s: s.replace('a * b', 'a + '),  
        lambda s: s.replace('a * b', '+ b'),
        lambda s: s + ' + c', 
        lambda s: 'c + ' + s,  
        lambda s: s.replace('a * b', 'a * b + c'),
        lambda s: s.replace('a * b', 'a + b + c'),
        lambda s: s.replace('a * b', 'a b + c'),
        lambda s: s.replace('a * b', '-a * b c'),
    ]

# Error types
error_types_interpolation = [
        lambda s: s.replace('%d..."', '"'),  
        lambda s: s.replace('a * b', 'a, b'),  
        lambda s: s.replace('a * b,', ''),
        lambda s: s.replace('" +', ''),  
        lambda s: s.replace('+ "....."', '"'),  
        lambda s: s.replace('....."', '"'),  
        lambda s: s.replace('a * b', 'a * '),  
        lambda s: s.replace('a * b', '* b'),
        lambda s: s.replace('a * b', 'a + '),  
        lambda s: s.replace('a * b', '+ b'),
        lambda s: s + ' + c', 
        lambda s: 'c + ' + s,  
        lambda s: s.replace('a * b', 'a * b + c'),
        lambda s: s.replace('a * b', 'a + b + c'),
        lambda s: s.replace('a * b', 'a b + c'),
        lambda s: s.replace('a * b', '-a * b c'),
    ]

# List to hold permutations
permutations_concatenation = []
permutations_interpolation = []

# Function to introduce an error into a code snippet
def introduce_error(snippet, error_types):
    
    # Select a random error to introduce
    error_func = random.choice(error_types)
    return error_func(snippet)

def error_concatenation():
    for _ in range(14):
        erroneous_snippet = introduce_error(original_snippet_concatenation, error_types_concatenation)
        permutations_concatenation.append(erroneous_snippet)
    return permutations_concatenation

def error_interpolation():
    for _ in range(14):
        erroneous_snippet = introduce_error(original_snippet_concatenation, error_types_concatenation)
        permutations_interpolation.append(erroneous_snippet)
    return permutations_interpolation


# # Display the generated permutations
# for i, permutation in enumerate(permutations, start=1):
#     print(f"Permutation {i}: {permutation}")