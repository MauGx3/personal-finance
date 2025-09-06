from rest_framework import permissions
from rest_framework import viewsets

from personal_finance.assets.models import Asset
from personal_finance.assets.models import Holding
from personal_finance.assets.models import Portfolio
from personal_finance.assets.serializers import AssetSerializer
from personal_finance.assets.serializers import HoldingSerializer
from personal_finance.assets.serializers import PortfolioSerializer


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # default to the requesting user if not provided
        if not serializer.validated_data.get("user"):
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class HoldingViewSet(viewsets.ModelViewSet):
    queryset = Holding.objects.all()
    serializer_class = HoldingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not serializer.validated_data.get("user"):
            serializer.save(user=self.request.user)
        else:
            serializer.save()
