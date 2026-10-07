"""Ordered mapped references and independent saving/buying location bindings."""

from spain_housing.models.scenario import GeographicReference, Scenario


def ordered_locations(
    locations: tuple[GeographicReference, ...],
) -> tuple[GeographicReference, ...]:
    if not locations or len(locations) != len(set(locations)):
        raise ValueError("mapped locations must be nonempty and unique")
    return tuple(sorted(locations, key=lambda location: (location.level, location.code)))


def location_pair(
    scenario: Scenario, mapped: GeographicReference
) -> tuple[GeographicReference, GeographicReference]:
    saving = scenario.locations.saving_location.location or mapped
    buying = scenario.locations.buying_location.location or mapped
    return saving, buying
