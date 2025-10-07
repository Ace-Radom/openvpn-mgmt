from app import config, create_app

app = create_app()
if config.config["app"]["is_production_env"]:
    app.config.update(DEBUG=False)
else:
    app.config.update(DEBUG=True)

if __name__ == "__main__":
    app.run()
