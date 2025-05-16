from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from analyzer import views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home, name='home'),
    path('upload/', views.upload_dataset, name='upload'),
    path('analyze/<int:dataset_id>/', views.analyze, name='analyze'),
    path('analysis/<int:analysis_id>/', views.view_analysis, name='view_analysis'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)