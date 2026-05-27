import json
import logging
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def load_data(filename):
    """Загрузка данных из JSON файла"""
    logger.info(f"Загрузка данных из файла: {filename}")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Успешно загружено {len(data)} треков")
        return data
    except FileNotFoundError:
        logger.error(f"Файл '{filename}' не найден")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Некорректный формат JSON в файле '{filename}': {e}")
        raise
    except PermissionError:
        logger.error(f"Нет доступа для чтения файла '{filename}'")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при загрузке файла '{filename}': {e}")
        raise


def calculate_metrics(tracks):
    """Расчёт всех метрик"""
    total_time = sum(t['duration_minutes'] * t['listens'] for t in tracks)

    genres = [t['genre'] for t in tracks]
    top_genre = Counter(genres).most_common(1)[0]

    top_track = max(tracks, key=lambda x: x['listens'])

    return total_time, top_genre, top_track


def create_plotly_visualization(tracks):
    """Интерактивные графики с Plotly"""
    df = pd.DataFrame(tracks)

    df['total_listen_time'] = df['duration_minutes'] * df['listens']

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Прослушивания по трекам', 'Распределение по жанрам',
                        'Длительность vs Прослушивания', 'Общее время по жанрам'),
        specs=[[{"type": "bar"}, {"type": "pie"}],
               [{"type": "scatter"}, {"type": "bar"}]]
    )

    fig.add_trace(
        go.Bar(x=df['track_name'], y=df['listens'],
               marker_color='lightblue', name='Прослушивания'),
        row=1, col=1
    )

    genre_counts = df['genre'].value_counts()
    fig.add_trace(
        go.Pie(labels=genre_counts.index, values=genre_counts.values,
               name='Жанры', hole=0.3),
        row=1, col=2
    )

    fig.add_trace(
        go.Scatter(x=df['duration_minutes'], y=df['listens'],
                   mode='markers+text',
                   text=df['track_name'],
                   textposition="top center",
                   marker=dict(size=12, color='green', opacity=0.6),
                   name='Треки'),
        row=2, col=1
    )

    genre_time = df.groupby('genre')['total_listen_time'].sum()
    fig.add_trace(
        go.Bar(x=genre_time.index, y=genre_time.values,
               marker_color='orange', name='Время'),
        row=2, col=2
    )

    fig.update_layout(height=800, showlegend=False,
                      title_text="Статистика прослушиваний музыки",
                      title_font_size=20)

    fig.update_xaxes(tickangle=45, row=1, col=1)
    fig.update_xaxes(tickangle=45, row=2, col=2)

    fig.show()


def create_seaborn_visualization(tracks):
    """Статистические графики с Seaborn"""
    df = pd.DataFrame(tracks)
    df['total_listen_time'] = df['duration_minutes'] * df['listens']

    sns.set_style("whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Статистика прослушиваний (Seaborn)', fontsize=16, fontweight='bold')

    sns.barplot(data=df, x='track_name', y='listens', ax=axes[0, 0],
                palette='Blues_d')
    axes[0, 0].set_title('Количество прослушиваний по трекам')
    axes[0, 0].tick_params(axis='x', rotation=90)

    genre_counts = df['genre'].value_counts()
    axes[0, 1].pie(genre_counts.values, labels=genre_counts.index,
                   autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
    axes[0, 1].set_title('Распределение треков по жанрам')

    sns.scatterplot(data=df, x='duration_minutes', y='listens',
                    size='total_listen_time', sizes=(50, 500),
                    hue='genre', palette='Set2', ax=axes[1, 0])
    axes[1, 0].set_title('Зависимость прослушиваний от длительности')

    genre_time = df.groupby('genre')['total_listen_time'].sum().sort_values()
    sns.barplot(x=genre_time.values, y=genre_time.index,
                ax=axes[1, 1], palette='Oranges_r')
    axes[1, 1].set_title('Общее время прослушивания по жанрам')
    axes[1, 1].set_xlabel('Минуты')

    plt.tight_layout()
    plt.show()


def print_report(tracks, total_time, top_genre, top_track):
    """Вывод текстового отчёта"""
    logger.info("Формирование текстового отчёта")
    print("=" * 60)
    print("ОТЧЁТ ПО СТАТИСТИКЕ ПРОСЛУШИВАНИЙ")
    print("=" * 60)
    print(f"Всего треков: {len(tracks)}")
    print(f"Уникальных исполнителей: {len(set(t['artist'] for t in tracks))}")
    print(f"Суммарное время прослушивания: {total_time:.2f} минут")
    print(f"Средняя длительность трека: {sum(t['duration_minutes'] for t in tracks) / len(tracks):.2f} минут")
    print(f"\nТоп-жанр: {top_genre[0]} ({top_genre[1]} треков)")
    print(f"\nСамый прослушиваемый трек:")
    print(f"  Название: {top_track['track_name']}")
    print(f"  Исполнитель: {top_track['artist']}")
    print(f"  Жанр: {top_track['genre']}")
    print(f"  Прослушиваний: {top_track['listens']}")
    print(f"  Длительность: {top_track['duration_minutes']} минут")
    print("=" * 60)


def main():
    """Основная функция"""
    try:
        tracks = load_data('music.json')

        total_time, top_genre, top_track = calculate_metrics(tracks)

        print_report(tracks, total_time, top_genre, top_track)

        logger.info("Генерация интерактивных графиков (Plotly)...")
        create_plotly_visualization(tracks)

        logger.info("Генерация статистических графиков (Seaborn)...")
        create_seaborn_visualization(tracks)
        
        logger.info("Анализ завершён успешно")
    except Exception as e:
        logger.error(f"Критическая ошибка в процессе выполнения: {e}")
        raise


if __name__ == "__main__":
    main()
