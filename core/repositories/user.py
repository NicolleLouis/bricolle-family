from django.contrib.auth.models import User


class UserRepository:
    @staticmethod
    def get_family_members(user):
        return User.objects.select_related('userprofile__family').filter(userprofile__family=user.userprofile.family)
