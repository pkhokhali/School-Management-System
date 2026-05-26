from rest_framework.exceptions import PermissionDenied

from .models import InstituteSettings


class FeatureFlagViewMixin:
    feature_key = None

    def check_feature(self):
        key = self.feature_key
        if key and not InstituteSettings.is_feature_enabled(key):
            raise PermissionDenied({
                'feature': key,
                'enabled': False,
                'detail': f'Feature "{key}" is not enabled.',
            })

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.check_feature()
