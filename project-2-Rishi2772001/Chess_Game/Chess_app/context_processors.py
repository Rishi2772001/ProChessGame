# Chess_app/context_processors.py

from .models import Invite

def pending_invites_count(request):
    if request.user.is_authenticated:
        count = Invite.objects.filter(invitee=request.user, accepted=False).count()
    else:
        count = 0
    return {'pending_invites_count': count}
