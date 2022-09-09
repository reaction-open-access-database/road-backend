from .models import Molecule, Reaction, ReactionComponent, UserProfile
from .exceptions import InvalidMolecule
from rest_framework import serializers
from django.contrib.auth.models import User
from rdkit import Chem
import json


class RDKitMoleculeJSONField(serializers.Field):
    def to_representation(self, value):
        return json.loads(Chem.MolToJSON(value.molecule))

    def to_internal_value(self, data):
        if data == '':
            return {'json': None}

        if isinstance(data, dict):
            json_data = json.dumps(data)
        else:
            json_data = data

        try:
            mols = Chem.JSONToMols(json_data)
        except RuntimeError:
            raise InvalidMolecule('Invalid JSON data')

        if len(mols) != 1:
            raise InvalidMolecule(
                f'Molecule field must contain exactly one molecule. '
                f'{len(mols)} molecules found.'
            )

        return {'json': mols[0]}


class RDKitMoleculeSmilesField(serializers.Field):
    def to_representation(self, value):
        return Chem.MolToSmiles(value.molecule)

    def to_internal_value(self, data):
        if data == '':
            return {'smiles': None}

        try:
            return {'smiles': Chem.MolFromSmiles(data)}
        except ValueError:
            raise InvalidMolecule('Invalid SMILES data')


class RDKitMoleculeInchiField(serializers.Field):
    def to_representation(self, value):
        return Chem.MolToInchi(value.molecule)

    def to_internal_value(self, data):
        if data == '':
            return {'inchi': None}

        try:
            return {'inchi': Chem.MolFromInchi(data)}
        except ValueError:
            raise InvalidMolecule('Invalid InChI data')


class MoleculeSerializer(serializers.HyperlinkedModelSerializer):
    json = RDKitMoleculeJSONField(source='*')
    smiles = RDKitMoleculeSmilesField(source='*')
    inchi = RDKitMoleculeInchiField(source='*')

    class Meta:
        model = Molecule
        fields = ['url', 'name', 'json', 'smiles', 'inchi']

    def create(self, validated_data):
        # Ensure that only one of the JSON, SMILES and InChI representations
        # were provided
        representations = (
            validated_data.pop('json'),
            validated_data.pop('smiles'),
            validated_data.pop('inchi'),
        )

        provided_representations = [rep for rep in representations if rep]

        if len(provided_representations) == 1:
            validated_data['molecule'] = provided_representations[0]
        else:
            raise InvalidMolecule(
                'Exactly one of JSON, SMILES or InChI must be provided.'
            )

        return super().create(validated_data)

    # TODO: Override update as well


class ReactionSerializer(serializers.HyperlinkedModelSerializer):
    components = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='reactioncomponent-detail'
    )

    class Meta:
        model = Reaction
        fields = ['url', 'components']


class ReactionComponentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ReactionComponent
        fields = ['url', 'reaction', 'molecule', 'component_type']


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = UserProfile
        fields = ['url', 'username', 'email']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='userprofile-detail'
    )

    class Meta:
        model = User
        fields = ['profile']

