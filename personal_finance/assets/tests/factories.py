import factory
from django.contrib.auth import get_user_model

from personal_finance.assets.models import Asset
from personal_finance.assets.models import Holding
from personal_finance.assets.models import Portfolio

UserModel = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserModel

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        # Allow overriding via: UserFactory(password="secret")
        pwd = extracted or "testpass123"
        self.set_password(pwd)
        if create:
            self.save()


class AssetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Asset

    symbol = factory.Sequence(lambda n: f"AST{n}")
    name = factory.Faker("word")
    asset_type = Asset.ASSET_STOCK
    currency = "USD"
    exchange = "NYSE"


class PortfolioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Portfolio

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Portfolio {n}")
    description = factory.Faker("sentence")
    is_default = False


class HoldingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Holding

    user = factory.SubFactory(UserFactory)
    asset = factory.SubFactory(AssetFactory)
    portfolio = None
    quantity = "1.0"
    average_price = "100.0"
    currency = "USD"
