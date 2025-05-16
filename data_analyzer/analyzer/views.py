import os
import pandas as pd
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Dataset, Analysis
from .forms import DatasetForm


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
            dataset.user = request.user
            dataset.save()
            return redirect('home')
    else:
        form = DatasetForm()
    return render(request, 'analyzer/upload.html', {'form': form})


@login_required
def analyze(request, dataset_id):
    dataset = Dataset.objects.get(id=dataset_id, user=request.user)

    if request.method == 'POST':
        analysis_type = request.POST.get('analysis_type')
        x_column = request.POST.get('x_column')
        y_column = request.POST.get('y_column')

       
        df = pd.read_csv(dataset.file.path)


        plt.figure(figsize=(10, 6))

        if analysis_type == 'hist':
            df[x_column].hist()
            plt.title(f'Гистограмма для {x_column}')
        elif analysis_type == 'scatter':
            plt.scatter(df[x_column], df[y_column])
            plt.title(f'Точечный график {x_column} vs {y_column}')
        elif analysis_type == 'line':
            plt.plot(df[x_column], df[y_column])
            plt.title(f'Линейный график {x_column} vs {y_column}')
        elif analysis_type == 'bar':
            df[x_column].value_counts().plot(kind='bar')
            plt.title(f'Столбчатая диаграмма для {x_column}')
        elif analysis_type == 'pie':
            df[x_column].value_counts().plot(kind='pie', autopct='%1.1f%%')
            plt.title(f'Круговая диаграмма для {x_column}')

        plt.tight_layout()


        image_path = f'analysis_results/{dataset.name}_{analysis_type}.png'
        full_path = os.path.join('media', image_path)
        plt.savefig(full_path)
        plt.close()


        analysis = Analysis.objects.create(
            dataset=dataset,
            analysis_type=analysis_type,
            x_column=x_column,
            y_column=y_column,
            image=image_path
        )

        return redirect('view_analysis', analysis_id=analysis.id)

    # Чтение столбцов для формы
    df = pd.read_csv(dataset.file.path)
    columns = df.columns.tolist()

    return render(request, 'analyzer/analyze.html', {
        'dataset': dataset,
        'columns': columns
    })


@login_required
def view_analysis(request, analysis_id):
    analysis = Analysis.objects.get(id=analysis_id, dataset__user=request.user)
    return render(request, 'analyzer/analysis_result.html', {'analysis': analysis})