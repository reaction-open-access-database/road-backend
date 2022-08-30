from rest_framework import viewsets
from .models import Molecule, Reaction, ReactionComponent, UserProfile
from .serializers import MoleculeSerializer, ReactionSerializer, \
    ReactionComponentSerializer, UserProfileSerializer
from .permissions import IsOwner, IsSuperUser, ReadOnly
from rest_framework.exceptions import NotFound


class HideUnauthorised:
    def permission_denied(self, request, message=None, code=None):
        raise NotFound()


class MoleculeViewSet(viewsets.ModelViewSet):
    queryset = Molecule.objects.all()
    serializer_class = MoleculeSerializer
    permission_classes = [IsSuperUser | IsOwner | ReadOnly]


class ReactionViewSet(viewsets.ModelViewSet):
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer
    permission_classes = [IsSuperUser | IsOwner | ReadOnly]


class ReactionComponentViewSet(viewsets.ModelViewSet):
    queryset = ReactionComponent.objects.all()
    serializer_class = ReactionComponentSerializer
    permission_classes = [IsSuperUser | IsOwner | ReadOnly]


class UserViewSet(HideUnauthorised, viewsets.ReadOnlyModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_permissions(self):
        # Allow users to view and edit their own profiles,
        # but only superusers to view and edit all profiles
        if self.action == 'retrieve':
            self.permission_classes = [IsOwner | IsSuperUser]
        elif self.action == 'list':
            self.permission_classes = [IsSuperUser]
        return super().get_permissions()
