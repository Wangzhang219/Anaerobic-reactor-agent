"""Main entry point for the anaerobic reactor agent."""


def main():
    from .cli.app import cli
    cli()


if __name__ == "__main__":
    main()
