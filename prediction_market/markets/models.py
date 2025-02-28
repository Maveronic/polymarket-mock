from django.db import models

# User model
class User(models.Model):
    name = models.CharField(max_length=255)
    balance = models.FloatField(default=0.0)  # Starting balance

    def __str__(self):
        return self.name

# Event model
class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Option model (choices in an event)
class Option(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=255)  # e.g., "Yes", "No"
    initial_probability = models.FloatField()  # Manually set at creation
    current_probability = models.FloatField(default=0.0)
    current_odds = models.FloatField(default=0.0)

    def update_probability_and_odds(self):
        # Total money staked on this event
        total_bets_on_event = sum(
            bet.amount for option in self.event.options.all() for bet in option.bets.all()
        )
        # Money staked on this option
        total_bets_on_option = sum(bet.amount for bet in self.bets.all())

        if total_bets_on_event > 0:
            self.current_probability = total_bets_on_option / total_bets_on_event
            self.current_odds = 1 / self.current_probability if self.current_probability > 0 else 0
        else:
            self.current_probability = self.initial_probability
            self.current_odds = 1 / self.initial_probability if self.initial_probability > 0 else 0

        self.save()

    def __str__(self):
        return self.name

# Bet model (user places bet on an option)
class Bet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bets')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bets')
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='bets')
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} bet {self.amount} on {self.option.name}"
