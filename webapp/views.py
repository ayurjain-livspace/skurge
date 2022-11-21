from rest_framework.views import APIView
from webapp.apps.skurge.common.util import APIResponse


class RUOK(APIView):
    """
        Health check.
    """

    def get(self, request):
        return APIResponse.send({"message": "imok"})
