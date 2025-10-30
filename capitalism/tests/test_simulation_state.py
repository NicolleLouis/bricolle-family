import pytest

from capitalism.constants.simulation_step import (
    SimulationStep,
    DEFAULT_STEP_SEQUENCE,
)
from capitalism.models import Simulation, Human, PriceAnalytics
from capitalism.constants.object_type import ObjectType


def test_sequence_order_matches_spec():
    assert Simulation.STEP_SEQUENCE == DEFAULT_STEP_SEQUENCE
    assert Human.STEP_SEQUENCE == DEFAULT_STEP_SEQUENCE


@pytest.mark.django_db
def test_next_step_progression():
    simulation = Simulation.objects.create(step=SimulationStep.CONSUMPTION)

    human = Human.objects.create(step=SimulationStep.DEATH)

    assert simulation.next_step() == SimulationStep.DEATH
    assert simulation.step == SimulationStep.DEATH

    human.step = SimulationStep.ANALYTICS
    human.save(update_fields=["step"])

    assert simulation.next_step() == SimulationStep.ANALYTICS
    assert simulation.step == SimulationStep.ANALYTICS


@pytest.mark.django_db
def test_next_step_wraps_to_start():
    simulation = Simulation.objects.create(step=SimulationStep.END_OF_DAY)

    Human.objects.create(step=SimulationStep.START_OF_DAY)
    assert simulation.next_step() == SimulationStep.START_OF_DAY
    simulation.refresh_from_db()
    assert simulation.step == SimulationStep.START_OF_DAY


@pytest.mark.django_db
def test_cannot_change_when_humans_not_ready():
    simulation = Simulation.objects.create(step=SimulationStep.PRODUCTION)
    Human.objects.create(step=SimulationStep.BUYING)

    with pytest.raises(Simulation.InvalidHumanStepError):
        simulation.can_change_step()


@pytest.mark.django_db
def test_finish_start_of_day_advances_humans():
    simulation = Simulation.objects.create(step=SimulationStep.START_OF_DAY)
    human = Human.objects.create(
        name="Alice",
        job="miner",
        step=SimulationStep.START_OF_DAY,
    )
    Human.objects.create(
        name="Bob",
        job="farmer",
        step=SimulationStep.PRODUCTION,
    )

    result = simulation.finish_current_step_start_of_day()

    human.refresh_from_db()
    simulation.refresh_from_db()

    assert human.step == SimulationStep.PRODUCTION
    assert result == SimulationStep.PRODUCTION
    assert simulation.step == SimulationStep.PRODUCTION


@pytest.mark.django_db
def test_finish_start_of_day_invalid_steps_raise():
    simulation = Simulation.objects.create(step=SimulationStep.START_OF_DAY)
    Human.objects.create(
        name="Carol",
        job="miner",
        step=SimulationStep.SELLING,
    )

    with pytest.raises(RuntimeError):
        simulation.finish_current_step_start_of_day()


@pytest.mark.django_db
def test_finish_price_stats_records_price_analytics_and_advances_humans():
    simulation = Simulation.objects.create(step=SimulationStep.PRICE_STATS, day_number=4)
    human = Human.objects.create(step=SimulationStep.PRICE_STATS)
    other = Human.objects.create(step=SimulationStep.PRICE_STATS)

    human.owned_objects.create(type=ObjectType.WOOD, in_sale=True, price=5.0)
    human.owned_objects.create(type=ObjectType.WOOD, in_sale=True, price=15.0)
    human.owned_objects.create(type=ObjectType.WOOD, in_sale=False, price=100.0)
    other.owned_objects.create(type=ObjectType.ORE, in_sale=True, price=None)

    result = simulation.finish_current_step_price_stats()

    simulation.refresh_from_db()
    human.refresh_from_db()
    other.refresh_from_db()

    assert result == SimulationStep.BUYING
    assert simulation.step == SimulationStep.BUYING
    assert human.step == SimulationStep.BUYING
    assert other.step == SimulationStep.BUYING

    analytics_count = PriceAnalytics.objects.filter(day_number=4).count()
    assert analytics_count == len(ObjectType.choices)

    wood_stats = PriceAnalytics.objects.get(day_number=4, object_type=ObjectType.WOOD)
    assert wood_stats.lowest_price_displayed == pytest.approx(5.0)
    assert wood_stats.max_price_displayed == pytest.approx(15.0)
    assert wood_stats.average_price_displayed == pytest.approx(10.0)

    ore_stats = PriceAnalytics.objects.get(day_number=4, object_type=ObjectType.ORE)
    assert ore_stats.lowest_price_displayed == pytest.approx(0.0)
    assert ore_stats.max_price_displayed == pytest.approx(0.0)
    assert ore_stats.average_price_displayed == pytest.approx(0.0)


@pytest.mark.django_db
def test_finish_buying_runs_humans_in_random_order(monkeypatch):
    simulation = Simulation.objects.create(step=SimulationStep.BUYING)
    humans = [
        Human.objects.create(step=SimulationStep.BUYING, money=100),
        Human.objects.create(step=SimulationStep.BUYING, money=120),
        Human.objects.create(step=SimulationStep.BUYING, money=80),
    ]

    shuffle_calls = []

    def fake_shuffle(seq):
        shuffle_calls.append([human.id for human in seq])
        seq.reverse()

    monkeypatch.setattr("capitalism.models.simulation.random.shuffle", fake_shuffle)

    call_order = []
    original_perform = Human.perform_current_step

    def tracking_perform(self):
        call_order.append(self.id)
        return original_perform(self)

    monkeypatch.setattr(Human, "perform_current_step", tracking_perform)

    result = simulation.finish_current_step_buying()

    simulation.refresh_from_db()
    for human in humans:
        human.refresh_from_db()
        assert human.step == SimulationStep.CONSUMPTION

    expected_ids = [human.id for human in humans]
    assert shuffle_calls == [expected_ids]
    assert call_order == list(reversed(expected_ids))
    assert result == SimulationStep.CONSUMPTION
    assert simulation.step == SimulationStep.CONSUMPTION


@pytest.mark.django_db
def test_can_change_step_price_stats_returns_true_when_all_object_types_present():
    simulation = Simulation.objects.create(step=SimulationStep.PRICE_STATS, day_number=2)

    for object_type, _label in ObjectType.choices:
        PriceAnalytics.objects.create(
            day_number=2,
            object_type=object_type,
            lowest_price_displayed=0.0,
            max_price_displayed=0.0,
            average_price_displayed=0.0,
            lowest_price=0.0,
            max_price=0.0,
            average_price=0.0,
        )

    assert simulation.can_change_step_price_stats() is True


@pytest.mark.django_db
def test_can_change_step_price_stats_returns_false_when_object_type_missing():
    simulation = Simulation.objects.create(step=SimulationStep.PRICE_STATS, day_number=5)

    missing_type = ObjectType.choices[-1][0]
    for object_type, _label in ObjectType.choices:
        if object_type == missing_type:
            continue
        PriceAnalytics.objects.create(
            day_number=5,
            object_type=object_type,
            lowest_price_displayed=0.0,
            max_price_displayed=0.0,
            average_price_displayed=0.0,
            lowest_price=0.0,
            max_price=0.0,
            average_price=0.0,
        )

    # Ensure the missing type exists for a different day and should not count.
    PriceAnalytics.objects.create(
        day_number=6,
        object_type=missing_type,
        lowest_price_displayed=0.0,
        max_price_displayed=0.0,
        average_price_displayed=0.0,
        lowest_price=0.0,
        max_price=0.0,
        average_price=0.0,
    )

    assert simulation.can_change_step_price_stats() is False
