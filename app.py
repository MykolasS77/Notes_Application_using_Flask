import notes_app


if __name__ == "__main__":
    app = notes_app.create_app(__name__)
    app.run(debug=True)
