from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from flash_cards.forms import AnswerFormSet, CategoryForm, QuestionForm, JsonQuestionForm
from flash_cards.models import Category, Question
from flash_cards.services import QuestionCreationError, QuestionCreationService

JSON_EXAMPLE_PAYLOAD = """{
  "category": "Culture générale",
  "question": "Quelle est la capitale de la France ?",
  "context": "Chapitre Géographie",
  "positive_answers": ["Paris"],
  "negative_answers": ["Lyon", "Marseille"]
}"""


def settings(request):
    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    validity = request.GET.get("validity", "").strip()
    questions = (
        Question.objects.select_related("category")
        .prefetch_related("answers")
        .annotate(
            answer_count=Count("answers"),
            positive_answers=Count("answers", filter=Q(answers__is_correct=True)),
            negative_answers=Count("answers", filter=Q(answers__is_correct=False)),
        )
        .order_by("-created_at")
    )
    if query:
        questions = questions.filter(text__icontains=query)
    if category_id:
        questions = questions.filter(category_id=category_id)
    if validity == "invalid":
        questions = questions.filter(
            Q(positive_answers=0) | Q(negative_answers=0)
        )
    elif validity == "valid":
        questions = questions.filter(positive_answers__gt=0, negative_answers__gt=0)

    categories = Category.objects.order_by("name")

    return render(
        request,
        "flash_cards/settings.html",
        {
            "questions": questions,
            "query": query,
            "category_id": category_id,
            "validity": validity,
            "categories": categories,
        },
    )


def categories(request):
    categories_qs = (
        Category.objects.annotate(question_count=Count("questions"))
        .order_by("name")
    )
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie ajoutée.")
            return redirect(reverse("flash_cards:categories"))
    else:
        form = CategoryForm()

    return render(
        request,
        "flash_cards/categories.html",
        {
            "categories": categories_qs,
            "form": form,
        },
    )


def question_form(request, question_id=None):
    if question_id:
        question_instance = get_object_or_404(Question, pk=question_id)
    else:
        question_instance = Question()

    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question_instance)
        formset = AnswerFormSet(request.POST, instance=question_instance)
        if form.is_valid() and formset.is_valid():
            question = form.save()
            formset.instance = question
            formset.save()
            messages.success(request, "Question enregistrée.")
            return redirect(reverse("flash_cards:settings"))
    else:
        form = QuestionForm(instance=question_instance)
        formset = AnswerFormSet(instance=question_instance)

    return render(
        request,
        "flash_cards/question_form.html",
        {
            "form": form,
            "formset": formset,
            "question": question_instance if question_instance.pk else None,
        },
    )


def question_delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        question.delete()
        messages.success(request, "Question supprimée.")
        return redirect(reverse("flash_cards:settings"))
    return redirect(reverse("flash_cards:question_edit", args=[question_id]))


def question_json_form(request):
    if request.method == "POST":
        form = JsonQuestionForm(request.POST)
        if form.is_valid():
            payload = form.parsed_payload or {}
            positive_answers = payload.get("positive_answers") or []
            negative_answers = payload.get("negative_answers") or []
            if not isinstance(positive_answers, list):
                form.add_error(None, "'positive_answers' doit être un tableau.")
            elif not isinstance(negative_answers, list):
                form.add_error(None, "'negative_answers' doit être un tableau.")
            else:
                service = QuestionCreationService()
                try:
                    service.create_question(
                        text=payload.get("question", ""),
                        category_id=payload.get("category_id"),
                        category_name=payload.get("category"),
                        context=payload.get("context"),
                        positive_answers=positive_answers,
                        negative_answers=negative_answers,
                    )
                except Category.DoesNotExist:
                    form.add_error(None, "Catégorie introuvable.")
                except QuestionCreationError as exc:
                    form.add_error(None, str(exc))
                else:
                    messages.success(request, "Question ajoutée à partir du JSON.")
                    return redirect(reverse("flash_cards:settings"))
    else:
        form = JsonQuestionForm()

    return render(
        request,
        "flash_cards/question_json_form.html",
        {
            "form": form,
            "json_example": JSON_EXAMPLE_PAYLOAD,
        },
    )
