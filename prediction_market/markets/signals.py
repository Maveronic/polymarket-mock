from django.db.models.signals import post_save
from django.db.models import Sum
from django.dispatch import receiver
from .models import Bet

@receiver(post_save, sender=Bet)
def deduct_balance_on_bet(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user.balance -= instance.amount
        user.save()
        instance.option.update_probability_and_odds()


@receiver(post_save, sender=Bet)
def handle_bet_placed(sender, instance, created, **kwargs):
    if not created:
        return  # Only handle newly placed bets

    option = instance.option
    event = option.event

    # Deduct user's balance
    user = instance.user
    user.balance -= instance.amount
    user.save()

    # Total staked across all options of the event
    total_staked = Bet.objects.filter(option__event=event).aggregate(total=Sum('amount'))['total'] or 0

    # Recalculate probability and odds for each option
    for opt in event.options.all():
        option_staked = Bet.objects.filter(option=opt).aggregate(total=Sum('amount'))['total'] or 0

        if total_staked == 0:
            opt.current_probability = opt.initial_probability  # Fallback if no bets at all
        else:
            opt.current_probability = option_staked / total_staked

        opt.current_odds = (1 / opt.current_probability) if opt.current_probability > 0 else 0
        opt.save()