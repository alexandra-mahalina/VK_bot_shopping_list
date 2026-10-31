from peewee import *
import config
db = SqliteDatabase('database.db')

class BaseModel(Model):
    """
    Базовый абстрактный класс
    """
    class Meta:
        database = db


class User(BaseModel):
    """
    Класс, определяющий пользователя
    """
    user_id = IntegerField(primary_key=True)
    first_name = CharField()
    last_name = CharField(null=True)


class Product(BaseModel):
    """
    Класс, идентифицирующий продукт
    """
    user = ForeignKeyField(User, backref='products')
    title = CharField()
    is_done = BooleanField(default=False)
    position = IntegerField()

    def __str__(self):
        return '{position}. {check} {title}'.format(
            position = self.position,
            check='[V]' if self.is_done else '[ ]',
            title=self.title,
        )


def create_models():
    """
    Создает в базе данных таблицы для всех классов, наследуемых от класса BaseModel
    :return:
    """
    db.create_tables(BaseModel.__subclasses__())