import readline
from sys import stdout
from re import match

RED = "\033[1;31m"
CYAN = "\033[1;36m"
RESET = "\033[0;0m"


def ask(question):
    '''
    Infinite loop to get yes or no answer or quit the script.
    '''
    while True:
        ans = input("\n" + question)
        al = ans.lower()
        if match('^y(es)?$', al):
            return True
        elif match('^n(o)?$', al):
            return False
        elif match('^q(uit)?$', al):
            stdout.write(CYAN)
            print("\nGoodbye.\n")
            stdout.write(RESET)
            quit()
        else:
            stdout.write(RED)
            print("%s is invalid. Enter (y)es, (n)o or (q)uit." % ans)
            stdout.write(RESET)
