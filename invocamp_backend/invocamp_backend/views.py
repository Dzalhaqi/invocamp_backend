from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.static import serve
from rest_framework.decorators import api_view
from rest_framework.response import Response


def protected_serve(request, path, document_root=None, show_indexes=False):
  # if request.user.is_superuser:
  #   return serve(request, path, document_root, show_indexes)
  # return redirect('/')
  return serve(request, path, document_root, show_indexes)


@api_view(['GET'])
def handler_404(request, exception):
  return Response({
      'message': 'Error',
      'code': 404,
      'details': 'Resources not found',
  }, status=404)


@api_view(['GET'])
def handler_500(request):
  return Response({
      'message': 'Error',
      'code': 500,
      'details': 'Server error'
  }, status=500)
