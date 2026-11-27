from .models import UserProfile


def get_user_role(user, session=None):
    if not user or not user.is_authenticated:
        return None
    if user.is_staff or user.is_superuser:
        return UserProfile.ROLE_ADMIN
    profile = UserProfile.objects.filter(user=user).first()
    if profile and profile.role == UserProfile.ROLE_ADMIN:
        return UserProfile.ROLE_ADMIN
    if session is not None:
        session_role = session.get('active_role')
        if session_role in (UserProfile.ROLE_CREATOR, UserProfile.ROLE_VIEWER):
            return session_role
    if profile:
        return profile.role
    return UserProfile.ROLE_VIEWER


def role_context(request):
    role = get_user_role(request.user, request.session)
    return {
        'active_role': role,
        'is_creator_role': role == UserProfile.ROLE_CREATOR,
        'is_admin_role': role == UserProfile.ROLE_ADMIN,
        'is_viewer_role': role == UserProfile.ROLE_VIEWER,
    }
