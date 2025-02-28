from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from .models import User, Event, Option, Bet
from .serializers import UserSerializer, EventSerializer, OptionSerializer, BetSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    Handles all CRUD operations related to users.

    Endpoints:
    - `GET /users/`: List all users
    - `POST /users/`: Create a new user
    - `GET /users/{id}/`: Retrieve a specific user
    - `PUT /users/{id}/`: Update a specific user
    - `DELETE /users/{id}/`: Delete a user
    - `PUT /users/{id}/deposit/`: Deposit money into user account
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['put'])
    def deposit(self, request, pk=None):
        """
        Deposit money into the user's account.

        Example Request Body:
        ```json
        {
            "amount": 500.0
        }
        ```

        Response (Success):
        ```json
        {
            "message": "500.0 has been added to John Doe's balance.",
            "new_balance": 1500.0
        }
        ```

        Response (Error):
        ```json
        {
            "error": "Invalid deposit amount"
        }
        ```
        """
        user = self.get_object()

        try:
            amount = float(request.data.get('amount', 0))
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (TypeError, ValueError):
            return Response({'error': 'Invalid deposit amount'}, status=status.HTTP_400_BAD_REQUEST)

        user.balance += amount
        user.save()

        return Response({'message': f'{amount} has been added to {user.name}\'s balance.', 'new_balance': user.balance})


class EventViewSet(viewsets.ModelViewSet):
    """
    Handles all CRUD operations related to events.

    Endpoints:
    - `GET /events/`: List all events
    - `POST /events/`: Create a new event
    - `GET /events/{id}/`: Retrieve a specific event
    - `PUT /events/{id}/`: Update a specific event
    - `DELETE /events/{id}/`: Delete an event
    - `GET /events/{id}/options/`: List all options for a specific event
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @action(detail=True, methods=['get'])
    def options(self, request, pk=None):
        """
        Retrieve all options for a given event.

        Response Example:
        ```json
        [
            {
                "id": 1,
                "name": "Tinubu Wins",
                "initial_probability": 0.5,
                "current_probability": 0.6,
                "current_odds": 1.5
            },
            {
                "id": 2,
                "name": "Obi Wins",
                "initial_probability": 0.5,
                "current_probability": 0.4,
                "current_odds": 2.5
            }
        ]
        ```
        """
        event = self.get_object()
        options = event.options.all()
        serializer = OptionSerializer(options, many=True)
        return Response(serializer.data)


class OptionViewSet(viewsets.ModelViewSet):
    """
    Handles all CRUD operations related to options within events.

    Endpoints:
    - `GET /options/`: List all options
    - `POST /options/`: Create a new option
    - `GET /options/{id}/`: Retrieve a specific option
    - `PUT /options/{id}/`: Update a specific option
    - `DELETE /options/{id}/`: Delete an option
    """
    queryset = Option.objects.all()
    serializer_class = OptionSerializer


class BetViewSet(viewsets.ModelViewSet):
    queryset = Bet.objects.all()
    serializer_class = BetSerializer

    def create(self, request, *args, **kwargs):
        """
        Place a bet on an option within a specific event.

        Example request body:
        {
            "user": 1,
            "event": 1,
            "option": "Tinubu",
            "amount": 500.0
        }
        """
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                {'error': 'Invalid data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.validated_data['user']
        amount = serializer.validated_data['amount']

        if user.balance < amount:
            return Response(
                {"error": "Insufficient balance"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            bet = serializer.save()
            user.balance -= amount
            user.save()

            # Update odds for the option since money has just been staked
            bet.option.update_probability_and_odds()

        return Response(BetSerializer(bet).data, status=status.HTTP_201_CREATED)