from app import create_app

app = create_app()


def main():
    """
    Entry point for running the Flask application.

    Configures the host and port, and starts the Flask development
    server with debugging enabled.
    """
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == '__main__':
    main()
