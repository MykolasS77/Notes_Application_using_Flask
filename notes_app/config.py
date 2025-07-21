class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///notes.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test"  # it best to load it using load_dotenv but i lieave it like this for now since the purpose of this changes is to reorganize the project
