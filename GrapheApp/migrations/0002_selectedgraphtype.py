

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GrapheApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SelectedGraphType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('graph_type', models.CharField(choices=[('line', 'Line Plot'), ('scatter', 'Scatter Plot'), ('box', 'Box Plot'), ('histogram', 'Histogram'), ('kde', 'KDE Plot'), ('violin', 'Violin Plot'), ('bar', 'Bar Plot'), ('heatmap', 'Heatmap'), ('pie', 'Pie Chart')], max_length=10)),
            ],
        ),
    ]
