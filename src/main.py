from src.services.slot_checker import SlotCheckerService


def main():
    checker = SlotCheckerService()
    checker.run()


if __name__ == "__main__":
    main()
