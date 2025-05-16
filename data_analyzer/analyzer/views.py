import os
import pandas as pd
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Dataset, Analysis
from .forms import DatasetForm
from django.conf import settings

@login_required
def home(request):
    datasets = Dataset.objects.filter(user=request.user)
    analyses = Analysis.objects.filter(dataset__user=request.user).order_by('-created_at')[:5]
    return render(request, 'analyzer/home.html', {
        'datasets': datasets,
        'analyses': analyses
    })


@login_required
def upload_dataset(request):
    if request.method == 'POST':
        form = DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.user = request.user  # Устанавливаем текущего пользователя
            dataset.save()
            return redirect('home')
    else:
        form = DatasetForm()
    return render(request, 'analyzer/upload.html', {'form': form})


@login_required
def analyze(request, dataset_id):
    try:
        dataset = Dataset.objects.get(id=dataset_id, user=request.user)

        if request.method == 'POST':
            # Получаем параметры из формы
            analysis_type = request.POST.get('analysis_type')
            x_column = request.POST.get('x_column')
            y_column = request.POST.get('y_column', None)

            # Чтение данных
            df = pd.read_csv(dataset.file.path)

            # Создание графиков
            plt.figure(figsize=(10, 6))

            if analysis_type == 'hist':
                df[x_column].hist()
                plt.title(f'Гистограмма для {x_column}')
            elif analysis_type == 'scatter' and y_column:
                plt.scatter(df[x_column], df[y_column])
                plt.title(f'Точечный график: {x_column} vs {y_column}')
            elif analysis_type == 'line' and y_column:
                plt.plot(df[x_column], df[y_column])
                plt.title(f'Линейный график: {x_column} vs {y_column}')
            elif analysis_type == 'bar':
                df[x_column].value_counts().plot(kind='bar')
                plt.title(f'Столбчатая диаграмма: {x_column}')
            elif analysis_type == 'pie':
                df[x_column].value_counts().plot(kind='pie', autopct='%1.1f%%')
                plt.title(f'Круговая диаграмма: {x_column}')

            plt.tight_layout()

            # Сохранение изображения
            image_name = f'analysis_{dataset_id}_{analysis_type}.png'
            image_path = os.path.join(settings.MEDIA_ROOT, 'analysis', image_name)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            plt.savefig(image_path)
            plt.close()

            # Сохранение результата анализа
            analysis = Analysis.objects.create(
                dataset=dataset,
                analysis_type=analysis_type,
                x_column=x_column,
                y_column=y_column,
                image=f'analysis/{image_name}'
            )

            return redirect('view_analysis', analysis_id=analysis.id)

        # Для GET-запроса показываем форму
        df = pd.read_csv(dataset.file.path)
        columns = df.columns.tolist()

        return render(request, 'analyzer/analyze.html', {
            'dataset': dataset,
            'columns': columns,
            'error': None
        })

    except Exception as e:
        print(f"Ошибка анализа: {str(e)}")
        return render(request, 'analyzer/analyze.html', {
            'dataset': dataset,
            'columns': [],
            'error': str(e)
        })


@login_required
def view_analysis(request, analysis_id):
    try:
        analysis = Analysis.objects.get(id=analysis_id, dataset__user=request.user)

        # Проверяем существование файла изображения
        if not os.path.exists(analysis.image.path):
            raise FileNotFoundError(f"Файл {analysis.image.path} не найден")

        # Читаем данные для отображения статистики
        df = pd.read_csv(analysis.dataset.file.path)
        stats = {
            'x_column': {
                'mean': df[analysis.x_column].mean(),
                'median': df[analysis.x_column].median(),
                'std': df[analysis.x_column].std()
            }
        }
        if analysis.y_column:
            stats['y_column'] = {
                'mean': df[analysis.y_column].mean(),
                'median': df[analysis.y_column].median(),
                'std': df[analysis.y_column].std()
            }

        return render(request, 'analyzer/analysis_result.html', {
            'analysis': analysis,
            'stats': stats,
            'image_url': analysis.image.url
        })

    except Exception as e:
        print(f"Ошибка при просмотре анализа: {str(e)}")
        return render(request, 'analyzer/error.html', {
            'error': f"Не удалось отобразить результаты: {str(e)}"
        })