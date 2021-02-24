from itertools import product


def all(args):
    """Create all possible dimension combinations
    with the given input lists."""
    
    parameters = []    
    for option in product(*(args[k] for k in args.keys())):
        parameters.append(option)

    return parameters


def copy(args, other):
    """Create all possible dimension combinations
    with the given input lists, but append dimensions
    in 'other' to each option."""

    parameters = []
    for option in product(*(args[k] for k in args.keys())):
        if other:
            option += other
        parameters.append(option)

    return parameters


def append(args, other, index=0):
    """Create all possible dimension combinations with
    the given input lists, but append dimensions in 
    based on relating entry in other, indexed by term
    index to get the key."""

    parameters = []
    for option in product(*(args[k] for k in args.keys())):
        if other:
            key = option[index]
            option += (other[key],)
        parameters.append(option)

    return parameters