def getargs():
    from argparse import ArgumentParser
    '''
    Return arguments
    '''
    parser = ArgumentParser(description='Answer yes or no to a question.')
    parser.add_argument("question", type=str, help="A question to ask.")
    return parser.parse_args()


def cats():
    from os import name
    from os import system
    '''
    CLEAR ALL THE SCREENS!
    '''
    if name == 'nt':
        system('cls')
    else:
        system('clear')


def main():
    from .ask import ask

    args = getargs()
    cats()
    question = args.question

    if ask(question):
        print("\nYou answered yes.\n")
    else:
        print("\nYou answered no.\n")


if __name__ == '__main__':
    main()
