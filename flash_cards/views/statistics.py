from django.shortcuts import render

from flash_cards.services.statistics import (
    CategoryPerformanceLeaderboardService,
    QuestionAttemptDistributionChartService,
    QuestionPerformanceScatterChartService,
)


def statistics(request):
    chart_service = QuestionAttemptDistributionChartService()
    performance_service = QuestionPerformanceScatterChartService()
    leaderboard_service = CategoryPerformanceLeaderboardService()
    performance_chart, trend_accuracy = performance_service.render()
    context = {
        "attempt_distribution_chart": chart_service.render(),
        "performance_chart": performance_chart,
        "performance_trend_accuracy": trend_accuracy,
        "category_leaderboard": leaderboard_service.top_categories(),
    }
    return render(request, "flash_cards/statistics.html", context)
