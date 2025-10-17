python main.py log 500 ml
    ```

*   To view your daily intake for today:

    ```bash
    python main.py daily
    ```

*   To view your weekly intake:

    ```bash
    python main.py weekly
    ```

*   To change the unit to ounces:

    ```bash
    python main.py unit oz
    ```

## Data Storage

The application stores data in a simple SQLite database named `hydration.db`. This file will be created automatically in the same directory as the script if it doesn't exist.

## Contributing

Contributions are welcome! Please feel free to submit pull requests with improvements or new features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
