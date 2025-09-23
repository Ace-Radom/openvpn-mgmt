from app import create_app

app = create_app()
app.secret_key = "change_this_to_a_random_secret_key"

if __name__ == "__main__":
    app.run(debug=True)
