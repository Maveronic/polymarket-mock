from django.contrib import admin
from django import forms
from django.db.models import Q
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import User, Event, Option, Bet

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1  # Number of empty option forms to display

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    inlines = [OptionInline]  # Show options inline when editing an event

class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter options based on the selected event
        if 'event' in self.data:
            try:
                event_id = int(self.data.get('event'))
                self.fields['option'].queryset = Option.objects.filter(event_id=event_id)
            except (ValueError, TypeError):
                pass  # Invalid input from the client; ignore and fallback to empty queryset
        elif self.instance.pk:
            # If editing an existing bet, show options for the event of the current bet
            self.fields['option'].queryset = self.instance.event.options.all()
        else:
            # If adding a new bet, show no options by default
            self.fields['option'].queryset = Option.objects.none()

class BetAdmin(admin.ModelAdmin):
    form = BetForm
    list_display = ('user', 'event', 'option', 'amount', 'created_at')
    list_filter = ('event',)  # Filter bets by event

    class Media:
        js = ('admin/js/bet_admin.js',)  # Add custom JavaScript for dynamic filtering

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('select-event/', self.admin_site.admin_view(self.select_event)),
            path('option/autocomplete/', self.admin_site.admin_view(self.option_autocomplete)),
        ]
        return custom_urls + urls

    def select_event(self, request):
        """
        Render a page to select an event before adding a bet.
        """
        if request.method == 'POST':
            event_id = request.POST.get('event')
            if event_id:
                # Redirect to the add bet page with the selected event ID
                url = reverse('admin:markets_bet_add') + f'?event={event_id}'
                return HttpResponseRedirect(url)
        events = Event.objects.all()
        return render(request, 'admin/select_event.html', {'events': events})

    def option_autocomplete(self, request):
        """
        Provide autocomplete options for the Option model based on the selected event.
        """
        event_id = request.GET.get('event_id')
        if event_id:
            options = Option.objects.filter(event_id=event_id)
            results = [{'id': option.id, 'text': option.name} for option in options]
        else:
            results = []
        return JsonResponse({'results': results})


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

# Register models with the admin site
admin.site.register(Event, EventAdmin)
admin.site.register(Option)
admin.site.register(Bet, BetAdmin)