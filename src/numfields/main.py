"""Entry point: python -m numfields"""


def main() -> None:
    from numfields.app import Application

    Application().run()


if __name__ == "__main__":
    main()
