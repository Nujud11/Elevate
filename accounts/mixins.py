from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

class RoleRequiredMixin(LoginRequiredMixin):
    
    required_role = None  # override in subclass

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:                                               # 1. First, check if user is authenticated (using the mixin's built-in check)
            return self.handle_no_permission() 

        if request.user.is_superuser:                                                       # 2. Allow superusers to access any view
            return super().dispatch(request, *args, **kwargs) 

        profile = getattr(request.user, "profile", None)                                    # 3. Check user's role
        if self.required_role and (not profile or profile.role != self.required_role):
            return redirect("forbidden")
        
        return super().dispatch(request, *args, **kwargs)                                   # Proceed normally if all checks pass
