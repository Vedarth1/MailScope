from src import create_app
from src.config.config import Config

configuration = Config()
env_config = configuration.dev_config 

app = create_app(env_config)

if __name__ == "__main__":
    app.run(host=env_config.HOST, 
            port=env_config.PORT, 
            debug=env_config.DEBUG)
