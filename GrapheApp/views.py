# Import des modules Django et des bibliothèques Python nécessaires
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import FileUploadForm
from .models import SelectedGraphType
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from django.conf import settings
from io import BytesIO
import base64
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import json
import plotly

# Vue pour le téléchargement de fichiers
def file(request):
    global df

    # Traitement du formulaire POST
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)

        # Validation du formulaire
        if form.is_valid():
            instance = form.save()

            # Lecture du fichier selon son extension
            file_extension = instance.file.name.split('.')[-1].lower()
            if file_extension == 'csv':
                df = pd.read_csv(instance.file, delimiter=',')
            elif file_extension == 'json':
                df = pd.read_json(instance.file)
            elif file_extension == 'xlsx':
                df = pd.read_excel(instance.file)
            else:
                os.remove(instance.file.path)
                return redirect('graphe')

            # Conversion du DataFrame en dictionnaire sérialisé
            serialized_df = df.to_dict(orient='records')

            # Stockage des colonnes et des données dans la session
            request.session['column_names'] = df.columns.tolist()
            request.session['df'] = serialized_df

            # Redirection vers la page des graphiques
            return redirect('graphe')
    else:
        # Création d'un formulaire de téléchargement de fichier
        form = FileUploadForm()

    # Affichage de la page de téléchargement de fichier
    return render(request, 'file.html', {'form': form})


# Fonction pour calculer des statistiques personnalisées
def calculate_statistics(df, selected_column_name1, selected_column_name2):
    mean_value = df[selected_column_name2].mean()
    median_value = df[selected_column_name2].median()
    mode_value = df[selected_column_name2].mode().iloc[0]
    range_value = df[selected_column_name2].max() - df[selected_column_name2].min()
    variance_value = df[selected_column_name2].var()
    std_deviation_value = df[selected_column_name2].std()
    count_value = df[selected_column_name2].count()

    # Création d'un dictionnaire pour stocker les statistiques
    statistics_dict = {
        'Mean': mean_value,
        'Median': median_value,
        'Mode': mode_value,
        'Range': range_value,
        'Variance': variance_value,
        'Écart-type': std_deviation_value,
        'Count': count_value,
    }

    # Conversion du dictionnaire en DataFrame pour un meilleur formatage
    statistics_df = pd.DataFrame(list(statistics_dict.items()), columns=['Statistic', 'Value'])

    return statistics_df.to_html(classes='table table-striped table-bordered border', index=False)


# Vue pour afficher les graphiques
def graphe(request):
    # Récupération des colonnes et des données depuis la session
    column_names = request.session.get('column_names', [])
    serialized_df = request.session.get('df')

    # Création du DataFrame à partir des données sérialisées
    df = pd.DataFrame(serialized_df)

    # Traitement du formulaire POST
    if request.method == 'POST':
        selected_column_name1 = request.POST.get('column_name1')
        selected_column_name2 = request.POST.get('column_name2')
        selected_graph_type = request.POST.get('graph')

        print("Selected Column 1:", selected_column_name1)
        print("Selected Column 2:", selected_column_name2)
        print("Selected Graph Type:", selected_graph_type)

        # Vérification des colonnes sélectionnées
        if selected_column_name1 not in column_names or selected_column_name2 not in column_names:
            return HttpResponse("Invalid column names")

        # Agrégation des données selon la colonne sélectionnée
        aggregated_df = df.groupby(selected_column_name1, as_index=False).agg({selected_column_name2: np.mean})

        # Calcul des statistiques descriptives
        statistics_df = df[[selected_column_name1, selected_column_name2]].describe()

        fig = None

        # Vérification du type de graphique sélectionné
        if selected_graph_type in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            if selected_graph_type == '1':
                fig = px.line(aggregated_df, x=selected_column_name1, y=selected_column_name2, markers=True)
            elif selected_graph_type == '2':
                fig = px.scatter(aggregated_df, x=selected_column_name1, y=selected_column_name2, title=f'Scatter Plot for {selected_column_name1} and {selected_column_name2}')
            elif selected_graph_type == '3':
                fig = px.box(df, x=selected_column_name1, y=selected_column_name2)
            elif selected_graph_type == '4':
                fig = px.histogram(df, x=selected_column_name1)
            elif selected_graph_type == '5':
                fig = px.density_heatmap(df, x=selected_column_name1, y=selected_column_name2, marginal_x="rug", marginal_y="rug")
            elif selected_graph_type == '6':
                fig = px.violin(df, x=selected_column_name1, y=selected_column_name2, box=True, points="all")
            elif selected_graph_type == '7':
                fig = px.bar(df, x=selected_column_name1, y=selected_column_name2)
            elif selected_graph_type == '8':
                correlation_matrix = df.corr()
                fig = px.imshow(correlation_matrix, labels=dict(color="Correlation"), x=column_names, y=column_names, color_continuous_scale='Viridis')
                fig.update_layout(title='Heatmap')
            elif selected_graph_type == '9':
                category_counts = df[selected_column_name1].value_counts()
                fig = px.pie(category_counts, values=category_counts, names=category_counts.index, title=f'Pie Chart for {selected_column_name1}')
        else:
            print("Type de graphique invalide")

        # Si le type de graphique n'est pas valide, affiche un message d'erreur
        if fig is None:
            return render(request, 'graphe.html', {
                'column_names': column_names,
                'selected_column_name1': selected_column_name1,
                'selected_column_name2': selected_column_name2,
                'selected_graph_type': selected_graph_type,
                'graph_type_choices': SelectedGraphType.GRAPH_TYPE_CHOICES,
                'graph_html': None,
                'error_message': "Type de graphique ou données non valides pour les colonnes sélectionnées",
            })

        if 'df':
            print("df is present")

        # Calcul des statistiques personnalisées
        statistics = calculate_statistics(df, selected_column_name1, selected_column_name2)

        # Mise en forme de l'arrière-plan du graphique
        fig.update_layout(
            paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent
            plot_bgcolor='rgba(0, 0, 0, 0)'     # Transparent
        )

        # Convertit la figure Plotly en HTML
        graph_html = fig.to_html(full_html=False)

        # Affichage de la page des graphiques avec les résultats
        return render(request, 'graphe.html', {
            'column_names': column_names,
            'selected_column_name1': selected_column_name1,
            'selected_column_name2': selected_column_name2,
            'selected_graph_type': selected_graph_type,
            'graph_type_choices': SelectedGraphType.GRAPH_TYPE_CHOICES,
            'statistics': statistics,
            'graph_html': graph_html
        })

    # Rendu du formulaire initial
    return render(request, 'graphe.html', {
        'column_names': column_names,
        'graph_type_choices': SelectedGraphType.GRAPH_TYPE_CHOICES,
    })
