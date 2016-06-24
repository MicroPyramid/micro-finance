from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from micro_admin.models import User

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class UserPermissionRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs.get('user_id'))
        if not (
            request.user.is_admin or request.user == user or
            (
                request.user.has_perm("branch_manager") and
                request.user.branch == user.branch
            )
        ):
            return HttpResponseRedirect(reverse('micro_admin:userslist'))
        return super(UserPermissionRequiredMixin, self).dispatch(request, *args, **kwargs)
