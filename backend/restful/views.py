from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Courier
from .serializers import CourierSerializer


class CourierView(APIView):
    def get(self, request):
        articles = Courier.objects.all()
        serializer = CourierSerializer(articles, many=True)
        return Response({"articles": serializer.data})

    def post(self, request):
        article = request.data.get("article")
        # Create an article from the above data
        serializer = CourierSerializer(data=article)
        if serializer.is_valid(raise_exception=True):
            article_saved = serializer.save()
        return Response({"success": "Article '{}' created successfully".format(article_saved.title)})

    def put(self, request, pk):
        saved_article = get_object_or_404(Courier.objects.all(), pk=pk)
        data = request.data.get('article')
        serializer = CourierSerializer(instance=saved_article, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            article_saved = serializer.save()
        return Response({
            "success": "Article '{}' updated successfully".format(article_saved.title)
        })