from django.forms import Form


class Choices(Form):
    cast = (('food', 'Їжа'),
            ('arm', 'Зброя'),
            ('medicine', 'Ліки'),
            ('clothes', 'Одяг'))

    status = (('processing', 'В обробці'),
              ('accepted', 'Прийнята'),
              ('rejected', 'Відхилена'),
              ('sent', 'Відправлено'),
              ('done', 'Виконана'))
