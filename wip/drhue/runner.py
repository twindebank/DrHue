# give it home instance
# handle server and reloading of code
import sys


class Runner:
    def __init__(self, path_to_script, name_of_home_var='home', name_of_context_var='context'):
        pass

    def run(self):
        pass


def main():
    path_to_script = sys.argv[1]
    runner = Runner(path_to_script)
    runner.run()


if __name__ == '__main__':
    main()
