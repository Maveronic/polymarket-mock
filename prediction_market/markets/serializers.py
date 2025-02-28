from rest_framework import serializers
from .models import User, Event, Option, Bet

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'name', 'initial_probability', 'current_probability', 'current_odds']

class EventSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)  # Nested serializer for options

    class Meta:
        model = Event
        fields = ['id', 'name', 'description', 'options']

class BetSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all(), write_only=True)
    option = serializers.CharField(write_only=True)  # Accept name instead of ID
    option_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bet
        fields = ['id', 'user', 'event', 'option', 'amount', 'option_detail']

    def validate_option(self, value):
        return value  # We will validate option within `validate()`

    def validate(self, data):
        """
        Validate:
        - Option must exist within the given event.
        - User must have enough balance for the bet amount.
        """
        user = data['user']
        event = data['event']
        option_name = data['option']
        amount = data['amount']

        try:
            option = event.options.get(name=option_name)
        except Option.DoesNotExist:
            raise serializers.ValidationError(
                {"option": f"Option '{option_name}' does not exist in event '{event.name}'."}
            )

        if user.balance < amount:
            raise serializers.ValidationError(
                {"amount": f"Insufficient balance. You have {user.balance}, but tried to bet {amount}."}
            )

        # Save the actual option object into validated_data for later creation
        data['option'] = option

        return data

    def create(self, validated_data):
        """
        Create the bet and deduct balance immediately.
        """
        option = validated_data.pop('option')
        user = validated_data['user']
        amount = validated_data['amount']

        # Deduct balance directly here
        user.balance -= amount
        user.save()

        bet = Bet.objects.create(option=option, event=validated_data.pop('event'), **validated_data)
        return bet

    def get_option_detail(self, obj):
        return {
            "id": obj.option.id,
            "name": obj.option.name,
            "event": obj.option.event.name
        }

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'name', 'balance']